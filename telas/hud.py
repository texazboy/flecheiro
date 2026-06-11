# -*- coding: utf-8 -*-
"""
HUD: coracoes de vida, ouro com moedinha, arco equipado, nome do lugar e a
linha de dicas de teclas. Os icones sao desenhados pixel a pixel uma vez so
na criacao e reaproveitados.
"""

import math

import pygame

import config
from core import som
from telas import comum

# 7x6, X = pixel aceso
_MAPA_CORACAO = [
    "0110110",
    "1111111",
    "1111111",
    "0111110",
    "0011100",
    "0001000",
]


def _desenhar_mapa(mapa, cor):
    s = pygame.Surface((len(mapa[0]), len(mapa)), pygame.SRCALPHA)
    for y, linha in enumerate(mapa):
        for x, c in enumerate(linha):
            if c == "1":
                s.set_at((x, y), cor)
    return s


class HUD:
    def __init__(self, mundo, recursos):
        self.mundo = mundo
        self.fonte = recursos.fonte(16)
        self.coracao_cheio = _desenhar_mapa(_MAPA_CORACAO, config.VERMELHO)
        self.coracao_vazio = _desenhar_mapa(_MAPA_CORACAO, config.CINZA_ESCURO)
        self.moeda = self._fazer_moeda()
        self.alerta_vida = self._fazer_alerta_vida()

    @staticmethod
    def _fazer_alerta_vida():
        """Moldura vermelha nas bordas; pulsa quando resta um coracao so."""
        s = pygame.Surface((config.LARGURA, config.ALTURA), pygame.SRCALPHA)
        for i in range(22):
            alfa = int(64 * (1 - i / 22))
            pygame.draw.rect(s, (200, 40, 40, alfa),
                             (i, i, config.LARGURA - 2 * i, config.ALTURA - 2 * i), 1)
        return s

    @staticmethod
    def _fazer_moeda():
        s = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(s, config.AMARELO, (4, 4), 3)
        pygame.draw.circle(s, (160, 130, 40), (4, 4), 3, 1)
        s.set_at((3, 3), config.BRANCO)
        return s

    def desenhar(self, tela, dica="", local=""):
        # com um coracao so, as bordas pulsam em vermelho (perigo!)
        if self.mundo.vida == 1:
            pulso = (math.sin(pygame.time.get_ticks() * 0.006) + 1) / 2
            self.alerta_vida.set_alpha(int(110 + 130 * pulso))
            tela.blit(self.alerta_vida, (0, 0))

        # coracoes
        for i in range(self.mundo.vida_max):
            img = self.coracao_cheio if i < self.mundo.vida else self.coracao_vazio
            tela.blit(img, (6 + i * 10, 6))

        # ouro
        tela.blit(self.moeda, (6, 17))
        comum.texto(tela, self.fonte, str(self.mundo.ouro), 17, 16, config.AMARELO)

        # arco equipado (chip colorido + nome)
        pygame.draw.rect(tela, self.mundo.arco.cor, (6, 30, 6, 6))
        pygame.draw.rect(tela, config.PRETO, (6, 30, 6, 6), 1)
        comum.texto(tela, self.fonte, self.mundo.arco.nome, 16, 29, config.VERDE)

        # canto direito: onde estamos + estado do som
        if local:
            comum.texto(tela, self.fonte, local, config.LARGURA - 6 -
                        self.fonte.size(local)[0], 6, config.BRANCO)
        if som.esta_mudo():
            comum.texto(tela, self.fonte, "som off [M]", config.LARGURA - 6 -
                        self.fonte.size("som off [M]")[0], 18, config.CINZA)

        if dica:
            comum.texto(tela, self.fonte, dica, config.LARGURA // 2,
                        config.ALTURA - 10, config.BRANCO, centro=True)
