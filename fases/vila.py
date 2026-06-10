# -*- coding: utf-8 -*-
"""
Vila entre as fases: zona segura, sem inimigos.

O jogador conversa com tres NPCs (todos tem dialogo simples). O ferreiro abre a
ferraria (mochila 0/1) e o lojista abre a loja; o aldeao so conversa. A direita
fica a saida para a proxima fase.
"""

import pygame

import config
from core.estados import Estado
from core.camera import Camera
from entidades.jogador import Jogador
from fases.npc import NPC
from telas.hud import HUD
from telas.dialogo import Dialogo
from telas.ferraria import Ferraria
from telas.loja import Loja
from telas.tela_inventario import TelaInventario
from telas import comum
from core.cenario import Fundo, desenhar_solido


class Vila(Estado):
    def __init__(self, jogo):
        super().__init__(jogo)
        self.mundo = jogo.mundo
        self.recursos = jogo.recursos
        self.largura_mundo = 900
        self.chao_y = 240
        self.solidos = [
            pygame.Rect(0, self.chao_y, self.largura_mundo, 60),
            pygame.Rect(-10, 0, 10, self.chao_y),                      # parede esquerda
        ]
        self.pos_inicial = (40, self.chao_y - 24)
        self.jogador = Jogador(*self.pos_inicial, self.recursos)

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
                ["Dizem que a floresta la na frente esta cheia de bichos.",
                 "No meu tempo a gente subia torre na flecha mesmo!",
                 "Boa sorte, rapaz."],
                config.VERDE, self.recursos, acao="dialogo"),
        ]

        self.porta = pygame.Rect(self.largura_mundo - 60, self.chao_y - 60, 24, 60)
        self.camera = Camera(config.LARGURA, config.ALTURA, self.largura_mundo)
        self.hud = HUD(self.mundo, self.recursos)
        self.fundo = Fundo(self.recursos, "noite")
        self.tile_grama = self.recursos.tile_grama()
        self.tile_terra = self.recursos.tile_terra()
        self.overlay = None
        self.npc_em_acao = None

    def plataformas_uma_via(self):
        return []

    # ----------------------------------------------------------- eventos
    def tratar_evento(self, evento):
        if self.overlay is not None:
            if self.overlay.tratar_evento(evento):
                self._ao_fechar_overlay()
            return

        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                self.jogador.pular()
            elif evento.key in (pygame.K_i, pygame.K_TAB):
                self.overlay = TelaInventario(self.mundo, self.recursos)
            elif evento.key == pygame.K_e:
                self._interagir()
            elif evento.key == pygame.K_ESCAPE:
                from telas.menu import MenuState
                self.jogo.trocar_estado(MenuState(self.jogo))

    def _interagir(self):
        alvo = self._npc_proximo()
        if alvo is not None:
            self.npc_em_acao = alvo
            self.overlay = Dialogo(alvo.nome, alvo.falas, self.recursos)
        elif self.jogador.rect.colliderect(self.porta):
            from fases.fase import Fase
            self.jogo.trocar_estado(Fase(self.jogo, 2))

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
        self.jogador.atualizar(dt, self)
        self.camera.seguir(self.jogador.rect)

    # ----------------------------------------------------------- desenho
    def desenhar(self, tela):
        self.fundo.desenhar(tela, self.camera.offset_x)
        for s in self.solidos:
            desenhar_solido(tela, self.camera.aplicar(s), self.tile_grama, self.tile_terra)
        # casinhas de fundo
        for cx in (150, 400, 600):
            self._desenhar_casa(tela, cx)

        porta = self.camera.aplicar(self.porta)
        pygame.draw.rect(tela, config.ROXO, porta)
        pygame.draw.rect(tela, config.AMARELO, porta, 1)

        proximo = self._npc_proximo()
        for npc in self.npcs:
            npc.desenhar(tela, self.camera, destacar=(npc is proximo))

        self.jogador.desenhar(tela, self.camera)

        dica = "E: conversar / seguir   |   I: inventario"
        self.hud.desenhar(tela, dica)

        if self.jogador.rect.colliderect(self.porta):
            fonte = self.recursos.fonte(15)
            p = self.camera.aplicar(self.porta)
            comum.texto(tela, fonte, "[E] seguir", p.centerx, p.top - 10,
                        config.AMARELO, centro=True)

        if self.overlay is not None:
            self.overlay.desenhar(tela)

    def _desenhar_casa(self, tela, cx):
        x = cx - self.camera.offset_x
        pygame.draw.rect(tela, (92, 70, 58), (x, 180, 70, 60))      # parede
        pygame.draw.polygon(tela, config.VERMELHO, [(x - 6, 180), (x + 76, 180), (x + 35, 152)])
        pygame.draw.rect(tela, config.MARROM, (x + 28, 210, 16, 30))  # porta
