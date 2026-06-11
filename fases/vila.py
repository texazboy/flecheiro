# -*- coding: utf-8 -*-
"""
Vila entre as fases: zona segura, sem inimigos, sempre de noitinha.

O jogador conversa com tres NPCs (todos tem dialogo simples). O ferreiro abre a
ferraria (mochila 0/1) e o lojista abre a loja; o aldeao so conversa - e muda de
assunto conforme o jogo avanca. A direita fica a saida pra proxima fase.

O cenario (casas, janelas acesas, postes) e desenhado UMA vez em cima da
superficie do terreno; o que se mexe (vaga-lumes, fumaca da chamine) e leve.
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
from entidades.efeitos import fumaca
from fases.npc import NPC
from telas.hud import HUD
from telas.dialogo import Dialogo
from telas.ferraria import Ferraria
from telas.loja import Loja
from telas.tela_inventario import TelaInventario
from telas.pausa import Pausa
from telas import comum

# (x da casa, x da chamine)
_CASAS = [(120, 178), (370, 428), (580, 638)]
_POSTES = [300, 720]


class Vila(Estado):
    def __init__(self, jogo, proxima_fase=2):
        super().__init__(jogo)
        self.mundo = jogo.mundo
        self.recursos = jogo.recursos
        self.proxima_fase = proxima_fase
        self.largura_mundo = 900
        self.chao_y = 240
        self.solidos = [
            pygame.Rect(0, self.chao_y, self.largura_mundo, 60),
            pygame.Rect(-10, 0, 10, self.chao_y),                      # parede esquerda
        ]
        self.pos_inicial = (40, self.chao_y - 24)
        self.jogador = Jogador(*self.pos_inicial, self.recursos)

        if proxima_fase <= 2:
            falas_jank = ["Dizem que a floresta la na frente esta cheia de bichos.",
                          "No meu tempo a gente subia torre na flecha mesmo!",
                          "Boa sorte, rapaz."]
        else:
            falas_jank = ["A ultima estrada tem vaos no chao, tome cuidado.",
                          "Finque uma flecha na beirada que ela vira ponte.",
                          "Volte inteiro, rapaz."]

        self.npcs = [
            NPC(200, self.chao_y, "ferreiro", "Ferreiro Tom",
                ["Bem-vindo a minha forja, arqueiro!",
                 "Me traga materiais que eu forjo um arco melhor.",
                 "Quanto melhor o material, melhor o arco. Use a cabeca."],
                config.LARANJA, self.recursos, acao="ferreiro"),
            NPC(430, self.chao_y, "lojista", "Dona Cila",
                ["Ola! Precisando de alguma coisa?",
                 "Compro seus materiais e vendo curas.",
                 "Ouro e ouro, nao desperdice!"],
                config.AZUL_CEU, self.recursos, acao="lojista"),
            NPC(640, self.chao_y, "aldeao", "Velho Jank",
                falas_jank, config.VERDE, self.recursos, acao="dialogo"),
        ]

        self.porta = pygame.Rect(self.largura_mundo - 60, self.chao_y - 60, 24, 60)
        self.camera = Camera(config.LARGURA, config.ALTURA, self.largura_mundo)
        self.hud = HUD(self.mundo, self.recursos)
        self.fundo = Fundo(self.recursos, "noite", semente=5)
        self.terreno, self.luzes_fixas = montar_terreno(
            self.largura_mundo, self.solidos, [], self.recursos,
            semente=11, tema="noite")
        self.luzes = Luzes(AMBIENTE["noite"])
        self._desenhar_cenario_fixo()

        self.particulas = []
        self._timer_fumaca = 0.0
        self.vagalumes = [dict(x=random.uniform(60, self.largura_mundo - 60),
                               y=random.uniform(150, 225),
                               defasagem=random.uniform(0, math.tau))
                          for _ in range(14)]

        self.overlay = None
        self.npc_em_acao = None

    def entrar(self):
        som.musica("vila")

    def plataformas_uma_via(self):
        return []

    # ------------------------------------------------- cenario pre-renderizado
    def _desenhar_cenario_fixo(self):
        """Casas e postes entram direto na superficie do terreno; os pontos de
        luz (janelas e lampadas) vao pra lista que alimenta a iluminacao."""
        sup = self.terreno
        for cx, _ in _CASAS:
            self._desenhar_casa(sup, cx)
        for px in _POSTES:
            self._desenhar_poste(sup, px)

    def _desenhar_casa(self, sup, x):
        chao = self.chao_y
        parede = (82, 64, 54)
        pygame.draw.rect(sup, parede, (x, chao - 60, 76, 60))
        pygame.draw.rect(sup, (66, 50, 42), (x, chao - 60, 76, 60), 1)
        pygame.draw.polygon(sup, (148, 62, 58), [(x - 7, chao - 60), (x + 83, chao - 60),
                                                 (x + 38, chao - 88)])
        pygame.draw.rect(sup, (110, 110, 118), (x + 52, chao - 84, 8, 18))   # chamine
        pygame.draw.rect(sup, config.MARROM, (x + 30, chao - 30, 16, 30))    # porta
        pygame.draw.rect(sup, (50, 38, 32), (x + 30, chao - 30, 16, 30), 1)
        sup.set_at((x + 43, chao - 16), config.AMARELO)                      # macaneta
        # janela acesa: o brilho de verdade vem do sistema de iluminacao
        janela = pygame.Rect(x + 9, chao - 48, 12, 12)
        pygame.draw.rect(sup, (255, 222, 140), janela)
        pygame.draw.rect(sup, (60, 46, 38), janela, 1)
        pygame.draw.line(sup, (60, 46, 38), (janela.centerx, janela.top),
                         (janela.centerx, janela.bottom - 1), 1)
        self.luzes_fixas.append((janela.centerx, janela.centery, 36, (255, 205, 130)))

    def _desenhar_poste(self, sup, x):
        chao = self.chao_y
        pygame.draw.rect(sup, (70, 72, 84), (x, chao - 46, 3, 46))
        pygame.draw.rect(sup, config.AMARELO, (x - 2, chao - 52, 7, 6))
        pygame.draw.rect(sup, (60, 60, 70), (x - 2, chao - 52, 7, 6), 1)
        self.luzes_fixas.append((x + 1, chao - 49, 60, (255, 222, 150)))

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
                self._ao_fechar_overlay()
            return

        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                self.jogador.pular()
            elif evento.key in (pygame.K_i, pygame.K_TAB):
                self.overlay = TelaInventario(self.mundo, self.recursos)
            elif evento.key == pygame.K_e:
                self._interagir()
            elif evento.key in (pygame.K_ESCAPE, pygame.K_p):
                self.overlay = Pausa(self.recursos)

    def _interagir(self):
        alvo = self._npc_proximo()
        if alvo is not None:
            self.npc_em_acao = alvo
            self.overlay = Dialogo(alvo.nome, alvo.falas, self.recursos,
                                   retrato=alvo.sprite)
        elif self.jogador.rect.colliderect(self.porta):
            som.tocar("porta")
            from fases.fase import Fase
            self.jogo.trocar_estado(Fase(self.jogo, self.proxima_fase))

    def _ao_fechar_overlay(self):
        # se fechou um dialogo de ferreiro/lojista, abre a tela correspondente
        if isinstance(self.overlay, Dialogo) and self.npc_em_acao is not None:
            acao = self.npc_em_acao.acao
            self.npc_em_acao = None
            if acao == "ferreiro":
                self.overlay = Ferraria(self.mundo, self.recursos)
                return
            if acao == "lojista":
                self.overlay = Loja(self.mundo, self.recursos)
                return
        self.overlay = None
        self.npc_em_acao = None

    def _npc_proximo(self):
        for npc in self.npcs:
            if npc.perto_de(self.jogador.rect):
                return npc
        return None

    # ----------------------------------------------------------- update
    def atualizar(self, dt):
        if self.overlay is not None:
            return
        self.mundo.tempo += dt
        self.jogador.atualizar(dt, self)
        self.camera.seguir(self.jogador.rect)
        self.camera.atualizar(dt)

        # fumaca subindo das chamines
        self._timer_fumaca += dt
        if self._timer_fumaca > 0.45:
            self._timer_fumaca = 0.0
            _, chamine_x = random.choice(_CASAS)
            self.particulas.append(fumaca(chamine_x + 4, self.chao_y - 86))
        for p in self.particulas:
            p.atualizar(dt)
        self.particulas = [p for p in self.particulas if not p.morta]

    # ----------------------------------------------------------- desenho
    def desenhar(self, tela):
        self.fundo.desenhar(tela, self.camera.offset_x)
        tela.blit(self.terreno, self.camera.origem())

        porta = self.camera.aplicar(self.porta)
        pygame.draw.rect(tela, config.ROXO, porta)
        pygame.draw.rect(tela, config.AMARELO, porta, 1)

        for p in self.particulas:
            p.desenhar(tela, self.camera)

        # o aviso [E] some enquanto um dialogo/loja esta aberto
        proximo = self._npc_proximo() if self.overlay is None else None
        for npc in self.npcs:
            npc.desenhar(tela, self.camera, destacar=(npc is proximo))

        self.jogador.desenhar(tela, self.camera)

        # iluminacao da noite: lampadas, janelas, portal e a luz do arqueiro
        self.luzes.adicionar(self.jogador.rect.centerx, self.jogador.rect.centery,
                             72, (255, 226, 185))
        self.luzes.adicionar(self.porta.centerx, self.porta.centery, 48, (215, 160, 255))
        for x, y, raio, cor in self.luzes_fixas:
            self.luzes.adicionar(x, y, raio, cor)
        self.luzes.aplicar(tela, self.camera)

        self._desenhar_vagalumes(tela)   # eles brilham por conta propria

        dica = "E: conversar / seguir   |   I: inventario"
        self.hud.desenhar(tela, dica, "Vila")

        if self.jogador.rect.colliderect(self.porta):
            fonte = self.recursos.fonte(15)
            p = self.camera.aplicar(self.porta)
            comum.texto(tela, fonte, "[E] seguir", p.centerx, p.top - 10,
                        config.AMARELO, centro=True)

        if self.overlay is not None:
            self.overlay.desenhar(tela)

    def _desenhar_vagalumes(self, tela):
        agora = pygame.time.get_ticks() * 0.001
        for v in self.vagalumes:
            x = v["x"] + math.sin(agora * 0.7 + v["defasagem"]) * 14
            y = v["y"] + math.sin(agora * 1.3 + v["defasagem"] * 2) * 6
            brilho = (math.sin(agora * 3 + v["defasagem"]) + 1) / 2
            if brilho < 0.3:
                continue  # apagadinho, nem desenha
            px, py = self.camera.aplicar_ponto((x, y))
            tam = 2 if brilho > 0.75 else 1
            pygame.draw.rect(tela, (235, 235, 130), (int(px), int(py), tam, tam))
