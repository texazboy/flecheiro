# -*- coding: utf-8 -*-
"""Telas de menu inicial, vitoria e game over."""

import pygame

import config
from core.estados import Estado
from core.mundo import Mundo
from telas import comum


class MenuState(Estado):
    def __init__(self, jogo):
        super().__init__(jogo)
        self.fonte_g = jogo.recursos.fonte(48)
        self.fonte = jogo.recursos.fonte(20)
        self.fonte_p = jogo.recursos.fonte(16)

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.jogo.mundo = Mundo()          # comeca uma partida nova
                from fases.fase import Fase
                self.jogo.trocar_estado(Fase(self.jogo, 1))
            elif evento.key == pygame.K_ESCAPE:
                self.jogo.rodando = False

    def desenhar(self, tela):
        tela.fill(config.AZUL_NOITE)
        comum.texto(tela, self.fonte_g, "FLECHEIRO", config.LARGURA // 2, 70,
                    config.AMARELO, centro=True)
        comum.texto(tela, self.fonte_p, "um arqueiro, algoritmos e muitas flechas",
                    config.LARGURA // 2, 104, config.BRANCO, centro=True)
        comum.texto(tela, self.fonte, "ENTER  -  comecar", config.LARGURA // 2, 150,
                    config.VERDE, centro=True)
        comum.texto(tela, self.fonte_p,
                    "Mover: A/D ou setas   Pular: Espaco   Atirar: clique do mouse",
                    config.LARGURA // 2, 190, config.CINZA, centro=True)
        comum.texto(tela, self.fonte_p,
                    "Coletar: E   Rota otima (TSP): T   Inventario: I",
                    config.LARGURA // 2, 208, config.CINZA, centro=True)
        comum.texto(tela, self.fonte_p, "ESC para sair", config.LARGURA // 2,
                    config.ALTURA - 16, config.CINZA, centro=True)


class VitoriaState(Estado):
    def __init__(self, jogo):
        super().__init__(jogo)
        self.fonte_g = jogo.recursos.fonte(44)
        self.fonte = jogo.recursos.fonte(18)

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_ESCAPE):
            self.jogo.trocar_estado(MenuState(self.jogo))

    def desenhar(self, tela):
        tela.fill(config.VERDE_ESCURO)
        m = self.jogo.mundo
        comum.texto(tela, self.fonte_g, "VITORIA!", config.LARGURA // 2, 80,
                    config.AMARELO, centro=True)
        comum.texto(tela, self.fonte, f"Arcos forjados: {m.arcos_forjados}    Ouro: {m.ouro}",
                    config.LARGURA // 2, 140, config.BRANCO, centro=True)
        comum.texto(tela, self.fonte, f"Arco final: {m.arco.nome}",
                    config.LARGURA // 2, 162, config.BRANCO, centro=True)
        comum.texto(tela, self.fonte, "ENTER para voltar ao menu", config.LARGURA // 2,
                    config.ALTURA - 30, config.CINZA, centro=True)


class GameOverState(Estado):
    def __init__(self, jogo, numero):
        super().__init__(jogo)
        self.numero = numero
        self.fonte_g = jogo.recursos.fonte(44)
        self.fonte = jogo.recursos.fonte(18)

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_r, pygame.K_RETURN):
                self.jogo.mundo.vida = self.jogo.mundo.vida_max
                from fases.fase import Fase
                self.jogo.trocar_estado(Fase(self.jogo, self.numero))
            elif evento.key == pygame.K_ESCAPE:
                self.jogo.trocar_estado(MenuState(self.jogo))

    def desenhar(self, tela):
        tela.fill((40, 20, 24))
        comum.texto(tela, self.fonte_g, "VOCE CAIU", config.LARGURA // 2, 90,
                    config.VERMELHO, centro=True)
        comum.texto(tela, self.fonte, "R - tentar a fase de novo     ESC - menu",
                    config.LARGURA // 2, 150, config.BRANCO, centro=True)
