# -*- coding: utf-8 -*-
"""
Fase de acao (side-scroller).

Junta tudo: o arqueiro, as flechas que viram plataforma, os inimigos que dropam
itens, a coleta por interacao (tecla E) e o overlay do TSP (tecla T), que mostra
a ordem otima de recolher os itens da fase e voltar ao ponto de partida.

As duas fases usam esta mesma classe, mudando so o "layout" (ver _layout).
"""

import pygame

import config
from core.estados import Estado
from core.camera import Camera
from entidades.jogador import Jogador
from entidades.inimigo import Inimigo
from entidades.item import ItemNoChao, MATERIAIS
from entidades.efeitos import explosao, TextoFlutuante
from telas.hud import HUD
from telas.tela_inventario import TelaInventario
from telas import comum
from core.cenario import Fundo, desenhar_solido, desenhar_plataforma
from algoritmos.tsp import resolver_tsp


def _layout(numero):
    """Devolve os dados de montagem de cada fase."""
    chao_y = 240
    if numero == 1:
        largura = 1600
        solidos = [
            pygame.Rect(0, chao_y, largura, 60),     # chao
            pygame.Rect(900, 150, 16, 90),           # pilar pra treinar a escalada
        ]
        plataformas = [
            pygame.Rect(260, 195, 70, 10),
            pygame.Rect(430, 165, 70, 10),
            pygame.Rect(820, 95, 130, 10),           # plataforma alta (bonus)
        ]
        # (material_drop, x, alcance_patrulha)
        inimigos = [("madeira", 200, 48), ("pena", 560, 40),
                    ("couro", 1150, 60), ("ferro", 1350, 50)]
        # (material, x, y_centro)
        itens = [("couro", 650, 226), ("madeira", 1250, 226),
                 ("madeira", 320, 186), ("pena", 470, 156),
                 ("cristal", 866, 86), ("ferro", 884, 86)]
        dica = "Mouse: mirar/atirar  |  E: coletar  |  T: rota otima  |  I: inventario"
    else:
        largura = 1700
        solidos = [
            pygame.Rect(0, chao_y, largura, 60),
            pygame.Rect(780, 90, 24, 150),           # parede alta: escalada obrigatoria
        ]
        plataformas = [
            pygame.Rect(300, 185, 70, 10),
            pygame.Rect(1050, 175, 90, 10),
            pygame.Rect(1250, 140, 90, 10),
        ]
        inimigos = [("couro", 250, 60), ("ferro", 500, 50),
                    ("ferro", 1120, 60), ("cristal", 1460, 50)]
        itens = [("ferro", 250, 226), ("madeira", 360, 168),
                 ("couro", 1080, 162), ("cristal", 1300, 128)]
        dica = "A parede bloqueia: finque flechas nela e suba ate o topo!"

    porta = pygame.Rect(largura - 80, chao_y - 60, 24, 60)
    return dict(largura=largura, solidos=solidos, plataformas=plataformas,
                inimigos=inimigos, itens=itens, porta=porta, chao_y=chao_y, dica=dica)


class Fase(Estado):
    def __init__(self, jogo, numero):
        super().__init__(jogo)
        self.numero = numero
        self.mundo = jogo.mundo
        self.recursos = jogo.recursos
        dados = _layout(numero)

        self.largura_mundo = dados["largura"]
        self.altura_mundo = config.ALTURA
        self.chao_y = dados["chao_y"]
        self.solidos = dados["solidos"]
        self.plataformas = dados["plataformas"]
        self.porta = dados["porta"]
        self.dica = dados["dica"]
        self.pos_inicial = (40, self.chao_y - 24)

        self.jogador = Jogador(*self.pos_inicial, self.recursos)
        self.inimigos = [self._criar_inimigo(d, x, alc) for (d, x, alc) in dados["inimigos"]]
        self.itens = [ItemNoChao(x, y, MATERIAIS[ch], self.recursos) for (ch, x, y) in dados["itens"]]
        self.flechas = []
        self.particulas = []
        self.textos = []

        self.camera = Camera(config.LARGURA, config.ALTURA, self.largura_mundo)
        self.hud = HUD(self.mundo, self.recursos)
        self.fundo = Fundo(self.recursos, "dia")
        self.tile_grama = self.recursos.tile_grama()
        self.tile_terra = self.recursos.tile_terra()
        self.tile_plataforma = self.recursos.tile_plataforma()

        self.overlay = None
        self.mostrar_rota = False
        self.resultado_tsp = None
        self._itens_rota = []

    def _criar_inimigo(self, dropa, x, alcance):
        return Inimigo(x, self.chao_y - 18, self.recursos, dropa=dropa, alcance=alcance)

    def plataformas_uma_via(self):
        """Plataformas que so seguram por cima = flutuantes + flechas fincadas."""
        return self.plataformas + [f.plataforma_rect() for f in self.flechas if f.fincada]

    # ----------------------------------------------------------- eventos
    def tratar_evento(self, evento):
        if self.overlay is not None:
            if self.overlay.tratar_evento(evento):
                self.overlay = None
            return

        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                self.jogador.pular()
            elif evento.key in (pygame.K_i, pygame.K_TAB):
                self.overlay = TelaInventario(self.mundo, self.recursos)
            elif evento.key == pygame.K_t:
                self.mostrar_rota = not self.mostrar_rota
                if self.mostrar_rota:
                    self._recalcular_rota()
            elif evento.key == pygame.K_e:
                self._coletar_proximos()
            elif evento.key == pygame.K_ESCAPE:
                from telas.menu import MenuState
                self.jogo.trocar_estado(MenuState(self.jogo))

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            interno = self.jogo.mouse_para_interno(evento.pos)
            alvo = self.camera.tela_para_mundo(interno)
            flecha = self.jogador.criar_flecha(alvo, self.mundo.arco)
            if flecha:
                self.flechas.append(flecha)
                self._limitar_flechas()

    # ----------------------------------------------------------- update
    def atualizar(self, dt):
        if self.overlay is not None:
            return  # jogo pausado enquanto o inventario esta aberto

        self.jogador.atualizar(dt, self)

        for f in self.flechas:
            f.atualizar(dt, self)
        self._colisao_flecha_inimigo()
        self.flechas = [f for f in self.flechas if not f.morta]

        for inim in list(self.inimigos):
            inim.atualizar(dt, self)
            if inim.morto:
                self._dropar(inim)
                self.particulas += explosao(inim.rect.centerx, inim.rect.centery, config.VERMELHO, 12)
                self.camera.sacudir(3)
                self.inimigos.remove(inim)
            elif inim.rect.colliderect(self.jogador.rect):
                if self.jogador.levar_dano(self.mundo, 1, origem_x=inim.rect.centerx):
                    self.camera.sacudir(4)

        for it in self.itens:
            it.atualizar(dt)

        for p in self.particulas:
            p.atualizar(dt)
        self.particulas = [p for p in self.particulas if not p.morta]
        for t in self.textos:
            t.atualizar(dt)
        self.textos = [t for t in self.textos if not t.morto]

        # rota do TSP fica desatualizada quando um item some -> recalcula
        if self.mostrar_rota and len(self.itens) != len(self._itens_rota):
            self._recalcular_rota()

        self.camera.seguir(self.jogador.rect)
        self.camera.atualizar(dt)
        self._checar_queda()

        if self.mundo.vida <= 0:
            from telas.menu import GameOverState
            self.jogo.trocar_estado(GameOverState(self.jogo, self.numero))
            return

        if self.jogador.rect.colliderect(self.porta):
            self._avancar()

    def _colisao_flecha_inimigo(self):
        for f in self.flechas:
            if f.fincada or f.morta:
                continue
            for inim in self.inimigos:
                if not inim.morto and f.rect.colliderect(inim.rect):
                    inim.levar_dano(f.dano)
                    f.morta = True
                    break

    def _dropar(self, inim):
        material = MATERIAIS[inim.dropa]
        self.itens.append(ItemNoChao(inim.rect.centerx, inim.rect.centery, material, self.recursos))

    def _limitar_flechas(self):
        fincadas = [f for f in self.flechas if f.fincada]
        excedente = len(fincadas) - config.MAX_FLECHAS_FINCADAS
        for f in fincadas[:max(0, excedente)]:
            f.morta = True
        if excedente > 0:
            self.flechas = [f for f in self.flechas if not f.morta]

    def _coletar_proximos(self):
        """Coleta (tecla E) os itens que estiverem perto do jogador."""
        centro = self.jogador.rect.center
        restantes = []
        for it in self.itens:
            dx = it.rect.centerx - centro[0]
            dy = it.rect.centery - centro[1]
            if dx * dx + dy * dy <= 24 * 24:
                self.mundo.inventario.adicionar(it.material, 1)
                self.particulas += explosao(it.rect.centerx, it.rect.centery, it.material.cor, 6)
                self.textos.append(TextoFlutuante(it.rect.centerx, it.rect.top,
                                                  "+" + it.material.nome, config.AMARELO,
                                                  self.recursos))
            else:
                restantes.append(it)
        self.itens = restantes

    def _checar_queda(self):
        if self.jogador.rect.top > self.altura_mundo + 40:
            self.jogador.levar_dano(self.mundo, 1)
            self.jogador.rect.topleft = self.pos_inicial
            self.jogador.vy = 0
            self.camera.sacudir(5)

    def _recalcular_rota(self):
        self._itens_rota = list(self.itens)
        pontos = [self.jogador.rect.center] + [it.centro for it in self._itens_rota]
        self.resultado_tsp = resolver_tsp(pontos)

    def _avancar(self):
        if self.numero == 1:
            from fases.vila import Vila
            self.jogo.trocar_estado(Vila(self.jogo))
        else:
            from telas.menu import VitoriaState
            self.jogo.trocar_estado(VitoriaState(self.jogo))

    # ----------------------------------------------------------- desenho
    def desenhar(self, tela):
        self._desenhar_fundo(tela)

        # solidos (chao, paredes, pilares) feitos de tiles
        for s in self.solidos:
            desenhar_solido(tela, self.camera.aplicar(s), self.tile_grama, self.tile_terra)
        # plataformas flutuantes
        for p in self.plataformas:
            desenhar_plataforma(tela, self.camera.aplicar(p), self.tile_plataforma)

        # porta de saida
        porta = self.camera.aplicar(self.porta)
        pygame.draw.rect(tela, config.ROXO, porta)
        pygame.draw.rect(tela, config.AMARELO, porta, 1)

        for it in self.itens:
            it.desenhar(tela, self.camera)
        for inim in self.inimigos:
            inim.desenhar(tela, self.camera)
        for f in self.flechas:
            f.desenhar(tela, self.camera)
        for p in self.particulas:
            p.desenhar(tela, self.camera)

        self.jogador.desenhar(tela, self.camera)
        self._desenhar_arco_e_mira(tela)

        for t in self.textos:
            t.desenhar(tela, self.camera)

        if self.mostrar_rota:
            self._desenhar_rota(tela)

        self.hud.desenhar(tela, self.dica)

        if self.overlay is not None:
            self.overlay.desenhar(tela)

    def _desenhar_fundo(self, tela):
        self.fundo.desenhar(tela, self.camera.offset_x)

    def _desenhar_arco_e_mira(self, tela):
        import math
        # direcao calculada no MUNDO (sem o tremor da camera, pra mira nao tremer)
        alvo = self.camera.tela_para_mundo(self.jogo.mouse_interno())
        centro = self.jogador.rect.center
        dx = alvo[0] - centro[0]
        dy = alvo[1] - centro[1]
        dist = math.hypot(dx, dy) or 1.0
        ux, uy = dx / dist, dy / dist
        px, py = -uy, ux  # perpendicular, pra desenhar o arco

        origem = self.camera.aplicar_ponto(centro)

        # previa da trajetoria (a curvinha pontilhada que a flecha vai fazer)
        self._desenhar_trajetoria(tela, centro, ux, uy)

        # o arco (uma curva curta) e a flecha encaixada apontando pro cursor
        topo = (origem[0] + px * 6, origem[1] + py * 6)
        base = (origem[0] - px * 6, origem[1] - py * 6)
        frente = (origem[0] + ux * 5, origem[1] + uy * 5)
        pygame.draw.lines(tela, config.MARROM_CLARO, False, [topo, frente, base], 2)
        rabo = (origem[0] - ux * 3, origem[1] - uy * 3)
        ponta = (origem[0] + ux * 10, origem[1] + uy * 10)
        pygame.draw.line(tela, config.BRANCO, rabo, ponta, 1)

        # mira no cursor
        mira = self.jogo.mouse_interno()
        pygame.draw.circle(tela, config.BRANCO, mira, 3, 1)

    def _desenhar_trajetoria(self, tela, centro, ux, uy):
        vel = config.FORCA_FLECHA * self.mundo.arco.velocidade
        vx = ux * vel
        vy = uy * vel
        x, y = float(centro[0]), float(centro[1])
        for i in range(50):
            vy = min(vy + config.GRAVIDADE_FLECHA, config.VEL_MAX_QUEDA)
            x += vx
            y += vy
            if y > self.altura_mundo or x < 0 or x > self.largura_mundo:
                break
            ponto_solido = pygame.Rect(int(x) - 1, int(y) - 1, 2, 2)
            if any(ponto_solido.colliderect(s) for s in self.solidos):
                break
            if i % 3 == 0:
                px, py = self.camera.aplicar_ponto((x, y))
                pygame.draw.circle(tela, config.AMARELO, (int(px), int(py)), 1)

    def _desenhar_rota(self, tela):
        fonte = self.recursos.fonte(15)
        if not self._itens_rota or self.resultado_tsp is None:
            comum.texto(tela, fonte, "TSP: nenhum item para coletar", config.LARGURA // 2,
                        44, config.AMARELO, centro=True)
            return

        coords = [self.jogador.rect.center] + [it.centro for it in self._itens_rota]
        ordem = self.resultado_tsp.ordem
        for i in range(len(ordem)):
            a = self.camera.aplicar_ponto(coords[ordem[i]])
            b = self.camera.aplicar_ponto(coords[ordem[(i + 1) % len(ordem)]])
            pygame.draw.line(tela, config.AMARELO, a, b, 2)
        for posicao, indice in enumerate(ordem):
            p = self.camera.aplicar_ponto(coords[indice])
            pygame.draw.circle(tela, config.VERMELHO if indice == 0 else config.AMARELO, p, 4)
            comum.texto(tela, fonte, str(posicao), p[0] - 2, p[1] - 16, config.BRANCO)

        r = self.resultado_tsp
        comum.texto(tela, fonte,
                    f"TSP {r.metodo}  -  custo {r.custo:.0f}  ({len(self._itens_rota)} pontos)",
                    config.LARGURA // 2, 44, config.AMARELO, centro=True)
