# -*- coding: utf-8 -*-
"""
Fase de acao (side-scroller).

Junta tudo: o arqueiro com o tiro carregado (segurar o mouse tensiona o arco),
as flechas que viram plataforma, inimigos terrestres e voadores, a coleta por
interacao (tecla E) e o overlay do TSP (tecla T), que mostra a ordem otima de
recolher os itens da fase e ainda marca qual e o proximo alvo da rota.

Sao tres fases com a mesma classe, mudando o layout e a hora do dia:
  1 - dia      (campo aberto, tutorial natural das mecanicas)
  2 - poente   (a parede alta que obriga a escalar com flechas)
  3 - noite    (vaos no chao onde a flecha fincada vira ponte)
"""

import math
import random

import pygame

import config
from core.estados import Estado
from core.camera import Camera
from core import som
from core.cenario import Fundo, montar_terreno
from core.luz import Luzes, AMBIENTE
from entidades.jogador import Jogador
from entidades.inimigo import Inimigo, InimigoVoador
from entidades.item import ItemNoChao, Moeda, Bau, MATERIAIS
from entidades.efeitos import explosao, faisca, poeira, Onda, TextoFlutuante
from telas.hud import HUD
from telas.tela_inventario import TelaInventario
from telas.pausa import Pausa
from telas import comum
from algoritmos.tsp import resolver_tsp

TOTAL_FASES = 3
TEMA_POR_FASE = {1: "dia", 2: "poente", 3: "noite"}


def _layout(numero):
    """Dados de montagem de cada fase. Inimigos: ("chao", drop, x, alcance)
    patrulha no chao; ("voo", drop, x, y) paira em volta do ponto."""
    chao_y = 240
    if numero == 1:
        largura = 1600
        solidos = [
            pygame.Rect(0, chao_y, largura, 60),     # chao corrido
            pygame.Rect(900, 150, 16, 90),           # pilar pra treinar a escalada
        ]
        plataformas = [
            pygame.Rect(260, 195, 70, 10),
            pygame.Rect(430, 165, 70, 10),
            pygame.Rect(820, 95, 130, 10),           # plataforma alta (bonus)
        ]
        inimigos = [("chao", "madeira", 200, 48), ("chao", "pena", 560, 40),
                    ("voo", "pena", 700, 120),
                    ("chao", "couro", 1150, 60), ("chao", "ferro", 1350, 50)]
        itens = [("couro", 650, 226), ("madeira", 1250, 226),
                 ("madeira", 320, 186), ("pena", 470, 156),
                 ("cristal", 866, 86), ("ferro", 884, 86)]
        baus = [(900, 95, ("ferro", "couro"))]          # premio da plataforma alta
        placas = [(140, "Atire flechas nas paredes: da pra subir em cima delas!"),
                  (840, "A plataforma la em cima guarda um bau. Escale com flechas.")]
        dica = "Segure o mouse pra tensionar o arco  |  E coleta  |  T rota  |  I inventario"
    elif numero == 2:
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
        inimigos = [("chao", "couro", 250, 60), ("chao", "ferro", 500, 50),
                    ("voo", "pena", 880, 70),
                    ("chao", "ferro", 1120, 60), ("chao", "cristal", 1460, 50)]
        itens = [("ferro", 250, 226), ("madeira", 360, 168),
                 ("couro", 1080, 162), ("cristal", 1300, 128)]
        baus = [(792, 90, ("cristal", "pena"))]         # no topo da parede
        placas = [(700, "Parede alta demais? Finque flechas nela e use de escada.")]
        dica = "A parede bloqueia o caminho: finque flechas nela e suba!"
    else:
        largura = 2000
        solidos = [
            # chao com VAOS: cair neles machuca; flecha fincada vira ponte
            pygame.Rect(0, chao_y, 520, 60),
            pygame.Rect(600, chao_y, 460, 60),
            pygame.Rect(1140, chao_y, 860, 60),
            pygame.Rect(900, 120, 24, 120),          # torre 1
            pygame.Rect(1500, 90, 24, 150),          # torre 2 (mais alta)
        ]
        plataformas = [
            pygame.Rect(380, 180, 70, 10),
            pygame.Rect(700, 170, 80, 10),
            pygame.Rect(1250, 180, 80, 10),
            pygame.Rect(1620, 140, 90, 10),
        ]
        inimigos = [("chao", "couro", 300, 60), ("voo", "pena", 560, 150),
                    ("chao", "ferro", 800, 70), ("voo", "pena", 1100, 130),
                    ("voo", "pena", 1450, 80), ("chao", "cristal", 1700, 80)]
        itens = [("ferro", 250, 226), ("cristal", 912, 106), ("madeira", 740, 152),
                 ("couro", 1280, 162), ("cristal", 1512, 76), ("ferro", 1900, 226)]
        baus = [(1660, 140, ("cristal", "ferro"))]      # na plataforma alta final
        placas = [(450, "Vaos a frente! Uma flecha fincada na beirada vira ponte."),
                  (1180, "Falta pouco. As tochas marcam o caminho.")]
        dica = "Noite fechada: cuidado com os vaos - a flecha fincada vira ponte!"

    porta = pygame.Rect(largura - 80, chao_y - 60, 24, 60)
    return dict(largura=largura, solidos=solidos, plataformas=plataformas,
                inimigos=inimigos, itens=itens, baus=baus, placas=placas,
                porta=porta, chao_y=chao_y, dica=dica)


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
        self.inimigos = [self._criar_inimigo(d) for d in dados["inimigos"]]
        self.itens = [ItemNoChao(x, y, MATERIAIS[ch], self.recursos)
                      for (ch, x, y) in dados["itens"]]
        self.baus = [Bau(x, y, conteudo, self.recursos)
                     for (x, y, conteudo) in dados["baus"]]
        self.placas = [(pygame.Rect(x - 10, self.chao_y - 18, 20, 18), txt)
                       for (x, txt) in dados["placas"]]
        self.moedas = []
        self.flechas = []
        self.particulas = []
        self.textos = []

        self.camera = Camera(config.LARGURA, config.ALTURA, self.largura_mundo)
        self.hud = HUD(self.mundo, self.recursos)
        self.tema = TEMA_POR_FASE.get(numero, "noite")
        self.fundo = Fundo(self.recursos, self.tema, semente=numero)
        self.terreno, self.luzes_fixas = montar_terreno(
            self.largura_mundo, self.solidos, self.plataformas, self.recursos,
            semente=numero * 7, tema=self.tema)
        self.luzes = Luzes(AMBIENTE.get(self.tema))
        self.brilho_porta = self._fazer_brilho_porta()

        # tochas fincadas nas beiradas dos vaos da fase noturna: a luz
        # tremulante marca o perigo de longe
        self.tochas = []
        if numero == 3:
            self.tochas = [(508, 239), (588, 239), (1052, 239), (1152, 239)]
            for tx, ty in self.tochas:
                pygame.draw.rect(self.terreno, (70, 54, 40), (tx - 1, ty - 12, 2, 13))
                pygame.draw.rect(self.terreno, (255, 180, 80), (tx - 2, ty - 16, 4, 5))
                pygame.draw.rect(self.terreno, (255, 230, 150), (tx - 1, ty - 15, 2, 2))

        # placas de aviso e uns barris fazendo companhia pra porta
        sprite_placa = self.recursos.sprite_placa()
        for r, _txt in self.placas:
            self.terreno.blit(sprite_placa, (r.centerx - 8, self.chao_y - 16))
        self._desenhar_barris(self.porta.left - 22, self.chao_y)
        # na fase noturna, uma lapide perto do primeiro vao (aviso... tarde demais)
        if numero == 3:
            lapide = self.recursos.sprite_opcional("lapide", 16)
            if lapide is not None:
                self.terreno.blit(lapide, (478 - lapide.get_width() // 2,
                                           self.chao_y - lapide.get_height()))

        # cache das sombras de contato (elipse escura nos pes)
        self._sombras = {}

        self.overlay = None
        self.mostrar_rota = False
        self.resultado_tsp = None
        self._itens_rota = []

        # tiro carregado e os timers de efeito
        self.carregando = False
        self.carga = 0.0
        self.hitstop = 0.0
        self._timer_porta = 0.0
        self._aviso_carga = False

        # vida ambiente: folhas de dia, brasas no poente, vagalumes de noite
        self.ondas = []
        self.folhas = []
        self._timer_folha = 0.0
        self.passaros = []
        self._timer_passaro = random.uniform(2.0, 5.0)
        self.vagalumes = []
        if self.tema == "noite":
            self.vagalumes = [dict(x=random.uniform(0, self.largura_mundo),
                                   y=random.uniform(120, 225),
                                   defasagem=random.uniform(0, math.tau))
                              for _ in range(12)]

        # rastreio do pouso/corrida pra soltar poeirinha nos pes
        self._no_chao_antes = True
        self._vy_queda = 0.0
        self._timer_passo = 0.0

    def entrar(self):
        som.musica("fase")

    def _criar_inimigo(self, dados):
        tipo, drop, x, extra = dados
        if tipo == "voo":
            return InimigoVoador(x, extra, self.recursos, dropa=drop)
        return Inimigo(x, self.chao_y - 15, self.recursos, dropa=drop, alcance=extra)

    def _desenhar_barris(self, x, chao):
        """Barril + caixote encostados na saida. Cada um usa o png de assets/
        se existir; senao sai a versao desenhada na mao."""
        t = self.terreno
        img_b = self.recursos.sprite_opcional("barril", 14)
        img_c = self.recursos.sprite_opcional("caixote", 13)

        if img_b is not None:
            t.blit(img_b, (x, chao - img_b.get_height()))
        else:
            pygame.draw.rect(t, (66, 44, 28), (x, chao - 14, 12, 14))
            pygame.draw.rect(t, (108, 74, 44), (x + 1, chao - 13, 10, 12))
            pygame.draw.line(t, (60, 40, 26), (x + 1, chao - 10), (x + 10, chao - 10), 1)
            pygame.draw.line(t, (60, 40, 26), (x + 1, chao - 5), (x + 10, chao - 5), 1)

        cx = x - 13
        if img_c is not None:
            t.blit(img_c, (cx - img_c.get_width() + 12, chao - img_c.get_height()))
        else:
            pygame.draw.rect(t, (66, 44, 28), (cx, chao - 11, 12, 11))
            pygame.draw.rect(t, (120, 86, 52), (cx + 1, chao - 10, 10, 9))
            pygame.draw.line(t, (66, 44, 28), (cx + 1, chao - 10), (cx + 10, chao - 2), 1)
            pygame.draw.line(t, (66, 44, 28), (cx + 10, chao - 10), (cx + 1, chao - 2), 1)

    def _sombra(self, tela, rect_mundo):
        """Elipse de sombra nos pes (igual jogo HD-2D, aterra os sprites)."""
        larg = rect_mundo.width + 4
        s = self._sombras.get(larg)
        if s is None:
            s = pygame.Surface((larg, 4), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (0, 0, 0, 70), (0, 0, larg, 4))
            self._sombras[larg] = s
        r = self.camera.aplicar(rect_mundo)
        tela.blit(s, (r.centerx - larg // 2, r.bottom - 2))

    def _fazer_brilho_porta(self):
        s = pygame.Surface((72, 88), pygame.SRCALPHA)
        for raio, alfa in ((34, 18), (24, 32), (15, 48)):
            pygame.draw.ellipse(s, (180, 120, 230, alfa),
                                (36 - raio, 44 - raio * 1.2, raio * 2, raio * 2.4))
        return s

    def plataformas_uma_via(self):
        """Plataformas que so seguram por cima = flutuantes + flechas fincadas."""
        return self.plataformas + [f.plataforma_rect() for f in self.flechas if f.fincada]

    # ----------------------------------------------------------- eventos
    def tratar_evento(self, evento):
        if self.overlay is not None:
            resultado = self.overlay.tratar_evento(evento)
            if isinstance(self.overlay, Pausa):
                if resultado == "menu":
                    from telas.menu import MenuState
                    self.jogo.trocar_estado(MenuState(self.jogo))
                elif resultado == "voltar":
                    self.overlay = None
            elif resultado:
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
                self._interagir()
            elif evento.key in (pygame.K_ESCAPE, pygame.K_p):
                self.carregando = False
                self.overlay = Pausa(self.recursos)

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.jogador.cooldown_tiro <= 0:
                self.carregando = True
                self.carga = 0.0
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if self.carregando:
                self._soltar_flecha(evento.pos)
            self.carregando = False

    def _soltar_flecha(self, pos_janela):
        interno = self.jogo.mouse_para_interno(pos_janela)
        alvo = self.camera.tela_para_mundo(interno)
        flecha = self.jogador.criar_flecha(alvo, self.mundo.arco, self.carga)
        if flecha:
            self.flechas.append(flecha)
            self._limitar_flechas()

    # ----------------------------------------------------------- update
    def atualizar(self, dt):
        if self.overlay is not None:
            return  # jogo pausado enquanto tem overlay aberto

        self.mundo.tempo += dt

        # hit-stop: o mundo congela um instante depois de um abate (impacto!)
        if self.hitstop > 0:
            self.hitstop -= dt
            self.camera.atualizar(dt)
            return

        if self.carregando:
            self.carga = min(1.0, self.carga + dt / config.TEMPO_CARGA)
            if self.carga >= 1.0 and not self._aviso_carga:
                # arco totalmente tensionado: clique + anelzinho de aviso
                self._aviso_carga = True
                som.tocar("pronto", 0.7)
                self.ondas.append(Onda(self.jogador.rect.centerx,
                                       self.jogador.rect.centery, 12, config.AMARELO, 0.2))
        else:
            self._aviso_carga = False
        self.jogador.mirando = self.carregando

        if not self.jogador.no_chao:
            self._vy_queda = max(self._vy_queda, self.jogador.vy)
        self.jogador.atualizar(dt, self)
        self._efeitos_de_movimento(dt)

        for f in self.flechas:
            f.atualizar(dt, self)
            if not f.fincada and not f.morta and random.random() < 0.5:
                self.particulas.append(faisca(f.x, f.y, config.AMARELO))
        self._colisao_flecha_inimigo()
        self.flechas = [f for f in self.flechas if not f.morta]

        for inim in list(self.inimigos):
            inim.atualizar(dt, self)
            if inim.morto:
                self._dropar(inim)
                for _ in range(random.randint(2, 3)):
                    self.moedas.append(Moeda(inim.rect.centerx, inim.rect.centery,
                                             self.recursos))
                self.particulas += explosao(inim.rect.centerx, inim.rect.centery,
                                            inim.cor_explosao, 12)
                self.ondas.append(Onda(inim.rect.centerx, inim.rect.centery, 20))
                self.camera.sacudir(3)
                self.hitstop = 0.05
                self.mundo.abatidos += 1
                som.tocar("morte")
                self.inimigos.remove(inim)
            elif inim.rect.colliderect(self.jogador.rect):
                if self.jogador.levar_dano(self.mundo, 1, origem_x=inim.rect.centerx):
                    self.camera.sacudir(4)

        for it in self.itens:
            it.atualizar(dt)

        # moedas: fisica + ima + coleta automatica
        for m in self.moedas:
            m.atualizar(dt, self, self.jogador)
            if m.coletada:
                self.mundo.ouro += 1
                som.tocar("moeda", 0.5)
                self.particulas.append(faisca(m.x, m.y, config.AMARELO))
        self.moedas = [m for m in self.moedas if not m.sumiu]

        # fagulhas na porta de saida, pra ela chamar o jogador de longe
        self._timer_porta += dt
        if self._timer_porta > 0.2:
            self._timer_porta = 0.0
            px = self.porta.centerx + random.randint(-10, 10)
            py = self.porta.centery + random.randint(-24, 24)
            self.particulas.append(faisca(px, py, random.choice((config.ROXO, config.AMARELO))))

        for p in self.particulas:
            p.atualizar(dt)
        self.particulas = [p for p in self.particulas if not p.morta]
        if len(self.particulas) > config.PARTICULAS_MAX:
            del self.particulas[:len(self.particulas) - config.PARTICULAS_MAX]
        for o in self.ondas:
            o.atualizar(dt)
        self.ondas = [o for o in self.ondas if not o.morta]
        for t in self.textos:
            t.atualizar(dt)
        self.textos = [t for t in self.textos if not t.morto]

        self._atualizar_ambiente(dt)

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
                    som.tocar("acerto")
                    f.morta = True
                    break

    def _dropar(self, inim):
        material = MATERIAIS[inim.dropa]
        self.itens.append(ItemNoChao(inim.rect.centerx, inim.rect.centery,
                                     material, self.recursos))

    def _limitar_flechas(self):
        fincadas = [f for f in self.flechas if f.fincada]
        excedente = len(fincadas) - config.MAX_FLECHAS_FINCADAS
        for f in fincadas[:max(0, excedente)]:
            f.morta = True
        if excedente > 0:
            self.flechas = [f for f in self.flechas if not f.morta]

    def _interagir(self):
        """Tecla E: abre bau perto, le placa perto, ou coleta itens."""
        jrect = self.jogador.rect
        for bau in self.baus:
            if not bau.aberto and jrect.colliderect(bau.rect.inflate(20, 16)):
                self._abrir_bau(bau)
                return
        for placa_rect, txt in self.placas:
            if jrect.colliderect(placa_rect.inflate(16, 8)):
                from telas.dialogo import Dialogo
                self.carregando = False
                self.overlay = Dialogo("Placa", [txt], self.recursos)
                return
        self._coletar_proximos()

    def _abrir_bau(self, bau):
        bau.abrir()
        som.tocar("bau")
        cx, cy = bau.rect.centerx, bau.rect.top
        self.ondas.append(Onda(cx, cy, 16, (255, 230, 150), 0.25))
        self.particulas += explosao(cx, cy, config.AMARELO, 10)
        for chave in bau.conteudo:
            self.itens.append(ItemNoChao(cx + random.randint(-14, 14), cy - 6,
                                         MATERIAIS[chave], self.recursos))
        for _ in range(4):
            self.moedas.append(Moeda(cx, cy - 4, self.recursos))

    def _coletar_proximos(self):
        """Coleta (tecla E) os itens que estiverem perto do jogador."""
        centro = self.jogador.rect.center
        restantes = []
        pegou = False
        for it in self.itens:
            dx = it.rect.centerx - centro[0]
            dy = it.rect.centery - centro[1]
            if dx * dx + dy * dy <= 24 * 24:
                self.mundo.inventario.adicionar(it.material, 1)
                self.mundo.coletados += 1
                pegou = True
                self.particulas += explosao(it.rect.centerx, it.rect.centery,
                                            it.material.cor, 6)
                self.textos.append(TextoFlutuante(it.rect.centerx, it.rect.top,
                                                  "+" + it.material.nome, config.AMARELO,
                                                  self.recursos))
            else:
                restantes.append(it)
        self.itens = restantes
        if pegou:
            som.tocar("coleta")

    def _efeitos_de_movimento(self, dt):
        """Poeira nos pes ao correr e ao aterrissar (com 'tum' em queda alta)."""
        jog = self.jogador
        pe_x, pe_y = jog.rect.centerx, jog.rect.bottom
        if jog.no_chao and not self._no_chao_antes:
            forte = self._vy_queda > 6.5
            self.particulas += poeira(pe_x, pe_y, 8 if forte else 4)
            if forte:
                self.ondas.append(Onda(pe_x, pe_y - 2, 14, (220, 210, 190), 0.22))
                self.camera.sacudir(2)
                som.tocar("fincar", 0.35)
            self._vy_queda = 0.0
        elif jog.no_chao and abs(jog.vx) > 0.1:
            self._timer_passo += dt
            if self._timer_passo > 0.22:
                self._timer_passo = 0.0
                self.particulas += poeira(pe_x - jog.vx * 3, pe_y, 2)
        self._no_chao_antes = jog.no_chao

    def _atualizar_ambiente(self, dt):
        """Vida de fundo: folhas (dia), brasas (poente), passaros e vagalumes."""
        if self.tema in ("dia", "poente"):
            self._timer_folha += dt
            if self._timer_folha > 0.5 and len(self.folhas) < 18:
                self._timer_folha = 0.0
                ox = self.camera.offset_x
                if self.tema == "dia":
                    cor = random.choice(((120, 190, 110), (180, 200, 90), (150, 180, 80)))
                    self.folhas.append(dict(x=ox + random.uniform(0, config.LARGURA),
                                            y=-4.0, vy=random.uniform(14, 24),
                                            fase=random.uniform(0, math.tau), cor=cor))
                else:
                    cor = random.choice(((255, 170, 90), (255, 210, 120), (230, 130, 80)))
                    self.folhas.append(dict(x=ox + random.uniform(0, config.LARGURA),
                                            y=random.uniform(180, 250), vy=-random.uniform(8, 16),
                                            fase=random.uniform(0, math.tau), cor=cor))
            agora = pygame.time.get_ticks() * 0.001
            for f in self.folhas:
                f["y"] += f["vy"] * dt
                f["x"] += math.sin(agora * 2.0 + f["fase"]) * 18 * dt
            self.folhas = [f for f in self.folhas if -10 < f["y"] < config.ALTURA + 10]

        if self.tema == "dia":
            self._timer_passaro -= dt
            if self._timer_passaro <= 0:
                self._timer_passaro = random.uniform(5.0, 11.0)
                self.passaros.append(dict(x=-12.0, y=random.uniform(28, 105),
                                          vel=random.uniform(22, 34)))
            for p in self.passaros:
                p["x"] += p["vel"] * dt
            self.passaros = [p for p in self.passaros if p["x"] < config.LARGURA + 16]

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
        som.tocar("porta")
        if self.numero < TOTAL_FASES:
            from fases.vila import Vila
            self.jogo.trocar_estado(Vila(self.jogo, proxima_fase=self.numero + 1))
        else:
            from telas.menu import VitoriaState
            self.jogo.trocar_estado(VitoriaState(self.jogo))

    # ----------------------------------------------------------- desenho
    def desenhar(self, tela):
        agora = pygame.time.get_ticks() * 0.001
        self.fundo.desenhar(tela, self.camera.offset_x)
        for p in self.passaros:
            self._desenhar_passaro(tela, p, agora)
        tela.blit(self.terreno, self.camera.origem())

        # porta de saida com brilho pulsante
        porta = self.camera.aplicar(self.porta)
        pulso = 120 + int(60 * math.sin(agora * 4.0))
        self.brilho_porta.set_alpha(pulso)
        tela.blit(self.brilho_porta, (porta.centerx - 36, porta.centery - 44))
        pygame.draw.rect(tela, config.ROXO, porta)
        pygame.draw.rect(tela, config.AMARELO, porta, 1)
        pygame.draw.circle(tela, (210, 170, 240), porta.center, 5, 1)

        for f in self.folhas:
            px, py = self.camera.aplicar_ponto((f["x"], f["y"]))
            pygame.draw.rect(tela, f["cor"], (int(px), int(py), 2, 2))

        # sombras de contato antes de todo mundo (aterra os sprites no chao);
        # morcego nao tem: esta voando
        if self.jogador.no_chao:
            self._sombra(tela, self.jogador.rect)
        for inim in self.inimigos:
            if isinstance(inim, Inimigo):
                self._sombra(tela, inim.rect)
        for bau in self.baus:
            self._sombra(tela, bau.rect)

        for bau in self.baus:
            bau.desenhar(tela, self.camera)
        for it in self.itens:
            it.desenhar(tela, self.camera)
        for m in self.moedas:
            m.desenhar(tela, self.camera)
        for inim in self.inimigos:
            inim.desenhar(tela, self.camera)
        for f in self.flechas:
            f.desenhar(tela, self.camera)
        for p in self.particulas:
            p.desenhar(tela, self.camera)

        self.jogador.desenhar(tela, self.camera)

        # ----- iluminacao: escurece a noite e abre as pocas de luz -----
        if self.luzes.ativa:
            self._pedir_luzes(agora)
            self.luzes.aplicar(tela, self.camera)

        # o que brilha por conta propria vem DEPOIS da luz
        self._desenhar_vagalumes(tela, agora)
        for o in self.ondas:
            o.desenhar(tela, self.camera)
        self._desenhar_arco_e_mira(tela)

        for t in self.textos:
            t.desenhar(tela, self.camera)

        if self.mostrar_rota:
            self._desenhar_rota(tela)

        self.hud.desenhar(tela, self.dica, f"Fase {self.numero}/{TOTAL_FASES}")

        if self.overlay is not None:
            self.overlay.desenhar(tela)

    def _pedir_luzes(self, agora):
        luz = self.luzes
        luz.adicionar(self.jogador.rect.centerx, self.jogador.rect.centery,
                      72, (255, 226, 185))
        luz.adicionar(self.porta.centerx, self.porta.centery, 56, (215, 160, 255))
        for x, y, raio, cor in self.luzes_fixas:
            luz.adicionar(x, y, raio, cor)
        for tx, ty in self.tochas:
            tremor = 44 + math.sin(agora * 13.0 + tx) * 5
            luz.adicionar(tx, ty - 14, tremor, (255, 188, 110))
        for it in self.itens:
            if it.material.chave == "cristal":
                pulso = 24 + math.sin(agora * 3.0 + it.rect.x) * 5
                luz.adicionar(it.rect.centerx, it.rect.centery, pulso, (185, 130, 235))

    def _desenhar_vagalumes(self, tela, agora):
        for v in self.vagalumes:
            x = v["x"] + math.sin(agora * 0.7 + v["defasagem"]) * 14
            y = v["y"] + math.sin(agora * 1.3 + v["defasagem"] * 2) * 6
            brilho = (math.sin(agora * 3 + v["defasagem"]) + 1) / 2
            if brilho < 0.3:
                continue
            px, py = self.camera.aplicar_ponto((x, y))
            if px < -4 or px > config.LARGURA + 4:
                continue
            tam = 2 if brilho > 0.75 else 1
            pygame.draw.rect(tela, (235, 235, 130), (int(px), int(py), tam, tam))

    @staticmethod
    def _desenhar_passaro(tela, passaro, agora):
        x, y = int(passaro["x"]), int(passaro["y"])
        bater = math.sin(agora * 9.0 + passaro["x"] * 0.1) * 2
        cor = (52, 62, 76)
        pygame.draw.line(tela, cor, (x - 3, y - int(bater)), (x, y), 1)
        pygame.draw.line(tela, cor, (x, y), (x + 3, y - int(bater)), 1)

    # --- mira, arco e a previa da trajetoria ---
    def _vel_flecha_atual(self):
        return config.FORCA_FLECHA * (0.55 + 0.45 * self.carga) * self.mundo.arco.velocidade

    def _desenhar_arco_e_mira(self, tela):
        # direcao calculada no MUNDO (sem o tremor da camera, pra mira nao tremer)
        alvo = self.camera.tela_para_mundo(self.jogo.mouse_interno())
        centro = self.jogador.rect.center
        dx = alvo[0] - centro[0]
        dy = alvo[1] - centro[1]
        dist = math.hypot(dx, dy) or 1.0
        ux, uy = dx / dist, dy / dist
        px, py = -uy, ux  # perpendicular, pra desenhar o arco

        origem = self.camera.aplicar_ponto(centro)

        if self.carregando:
            self._desenhar_trajetoria(tela, centro, ux, uy)
            # barrinha de tensao em cima do jogador
            r = self.camera.aplicar(self.jogador.rect)
            cor = (int(232 + 23 * self.carga), int(196 - 120 * self.carga), 70)
            pygame.draw.rect(tela, config.PRETO, (r.left - 1, r.top - 8, 18, 4))
            pygame.draw.rect(tela, cor, (r.left, r.top - 7, int(16 * self.carga), 2))

        # o arco (curva curta) e a flecha encaixada apontando pro cursor
        recuo = 2 + 3 * self.carga if self.carregando else 2
        topo = (origem[0] + px * 6, origem[1] + py * 6)
        base = (origem[0] - px * 6, origem[1] - py * 6)
        frente = (origem[0] + ux * (7 - recuo), origem[1] + uy * (7 - recuo))
        pygame.draw.lines(tela, config.MARROM_CLARO, False, [topo, frente, base], 2)
        rabo = (origem[0] - ux * recuo, origem[1] - uy * recuo)
        ponta = (origem[0] + ux * (12 - recuo), origem[1] + uy * (12 - recuo))
        pygame.draw.line(tela, config.BRANCO, rabo, ponta, 1)

        mira = self.jogo.mouse_interno()
        pygame.draw.circle(tela, config.BRANCO, mira, 3, 1)

    def _desenhar_trajetoria(self, tela, centro, ux, uy):
        """Pontilha o caminho que a flecha faria se soltasse agora."""
        vel = self._vel_flecha_atual()
        vx = ux * vel
        vy = uy * vel
        x, y = float(centro[0]), float(centro[1])
        for i in range(50):
            vy = min(vy + config.GRAVIDADE_FLECHA, config.VEL_MAX_QUEDA)
            x += vx
            y += vy
            if y > self.altura_mundo or x < 0 or x > self.largura_mundo:
                break
            ponto = pygame.Rect(int(x) - 1, int(y) - 1, 2, 2)
            if any(ponto.colliderect(s) for s in self.solidos):
                px, py = self.camera.aplicar_ponto((x, y))
                pygame.draw.circle(tela, config.BRANCO, (int(px), int(py)), 2, 1)
                break
            if i % 3 == 0:
                px, py = self.camera.aplicar_ponto((x, y))
                pygame.draw.circle(tela, config.AMARELO, (int(px), int(py)), 1)

    # --- overlay do TSP ---
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

        # marcador pulsante no PROXIMO alvo da rota (o jogador e o ponto 0)
        if len(ordem) > 1:
            alvo = coords[ordem[1]]
            ax, ay = self.camera.aplicar_ponto(alvo)
            ax = max(12, min(config.LARGURA - 12, ax))
            ay = max(26, min(config.ALTURA - 30, ay))
            salto = math.sin(pygame.time.get_ticks() * 0.008) * 3
            topo = ay - 18 + salto
            pygame.draw.polygon(tela, config.AMARELO,
                                [(ax - 5, topo), (ax + 5, topo), (ax, topo + 7)])
            pygame.draw.polygon(tela, config.PRETO,
                                [(ax - 5, topo), (ax + 5, topo), (ax, topo + 7)], 1)

        r = self.resultado_tsp
        comum.texto(tela, fonte,
                    f"TSP {r.metodo}  -  custo {r.custo:.0f}  ({len(self._itens_rota)} pontos)",
                    config.LARGURA // 2, 44, config.AMARELO, centro=True)
