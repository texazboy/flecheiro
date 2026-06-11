# -*- coding: utf-8 -*-
"""
HUD: a placa do canto com coracoes/ouro/arco, a placa do lugar, a faixa de
dicas embaixo e o alerta pulsante de vida baixa.

Todas as pecas fixas (placas, faixa, icones) sao pre-renderizadas no init;
no frame a frame e so blit + numeros.
"""

import math

import pygame

import config
from core import som
from telas import comum

# 7x6, 1 = pixel aceso
_MAPA_CORACAO = [
    "0110110",
    "1111111",
    "1111111",
    "0111110",
    "0011100",
    "0001000",
]


def _desenhar_mapa(mapa, cor, brilho=False):
    s = pygame.Surface((len(mapa[0]), len(mapa)), pygame.SRCALPHA)
    for y, linha in enumerate(mapa):
        for x, c in enumerate(linha):
            if c == "1":
                s.set_at((x, y), cor)
    if brilho:
        s.set_at((1, 1), (255, 255, 255))
        s.set_at((2, 1), (255, 200, 200))
    return s


class HUD:
    def __init__(self, mundo, recursos):
        self.mundo = mundo
        self.fonte = recursos.fonte(16)
        self.coracao_cheio = _desenhar_mapa(_MAPA_CORACAO, config.VERMELHO, brilho=True)
        self.coracao_claro = _desenhar_mapa(_MAPA_CORACAO, (255, 120, 110), brilho=True)
        self.coracao_vazio = _desenhar_mapa(_MAPA_CORACAO, (58, 50, 66))
        self.moeda = self._fazer_moeda()
        self.placa = self._fazer_placa(126, 44)
        self.faixa_dica = self._fazer_faixa_dica()
        self.alerta_vida = self._fazer_alerta_vida()
        self._placas_local = {}   # cache das placas do canto direito

    # ------------------------------------------------------------- pecas
    @staticmethod
    def _fazer_moeda():
        s = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(s, config.AMARELO, (4, 4), 3)
        pygame.draw.circle(s, (160, 130, 40), (4, 4), 3, 1)
        s.set_at((3, 3), config.BRANCO)
        return s

    @staticmethod
    def _fazer_placa(largura, altura):
        """Plaquinha com fio dourado (mesma familia visual dos paineis)."""
        s = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.rect(s, (28, 20, 18, 220), (0, 0, largura, altura), border_radius=5)
        pygame.draw.rect(s, (16, 16, 26, 165), (1, 1, largura - 2, altura - 2),
                         border_radius=4)
        pygame.draw.rect(s, (198, 148, 70, 200), (1, 1, largura - 2, altura - 2),
                         width=1, border_radius=4)
        pygame.draw.line(s, (238, 200, 124, 90), (4, 1), (largura - 5, 1), 1)
        return s

    @staticmethod
    def _fazer_faixa_dica():
        """Gradiente escuro no rodape pra dica nunca sumir na grama."""
        s = pygame.Surface((config.LARGURA, 26), pygame.SRCALPHA)
        for y in range(26):
            alfa = int(150 * (y / 25) ** 1.4)
            s.fill((8, 8, 14, alfa), (0, y, config.LARGURA, 1))
        return s

    @staticmethod
    def _fazer_alerta_vida():
        """Moldura vermelha nas bordas; pulsa quando resta um coracao so."""
        s = pygame.Surface((config.LARGURA, config.ALTURA), pygame.SRCALPHA)
        for i in range(22):
            alfa = int(64 * (1 - i / 22))
            pygame.draw.rect(s, (200, 40, 40, alfa),
                             (i, i, config.LARGURA - 2 * i, config.ALTURA - 2 * i), 1)
        return s

    def _icone_arco(self, tela, x, y, cor):
        """Mini arco com corda e flecha, na cor do arco equipado."""
        pygame.draw.lines(tela, cor, False, [(x, y), (x + 3, y + 4), (x, y + 8)], 2)
        pygame.draw.line(tela, (210, 210, 220), (x, y), (x, y + 8), 1)
        pygame.draw.line(tela, config.MARROM_CLARO, (x - 1, y + 4), (x + 5, y + 4), 1)
        pygame.draw.polygon(tela, (210, 210, 220),
                            [(x + 5, y + 3), (x + 7, y + 4), (x + 5, y + 5)])

    # ------------------------------------------------------------- frame
    def desenhar(self, tela, dica="", local=""):
        agora = pygame.time.get_ticks() * 0.001

        # com um coracao so, as bordas pulsam em vermelho (perigo!)
        vida_baixa = self.mundo.vida == 1
        if vida_baixa:
            pulso = (math.sin(agora * 6.0) + 1) / 2
            self.alerta_vida.set_alpha(int(110 + 130 * pulso))
            tela.blit(self.alerta_vida, (0, 0))

        tela.blit(self.placa, (3, 3))

        # coracoes (o ultimo "bate" quando a vida esta no talo)
        for i in range(self.mundo.vida_max):
            if i < self.mundo.vida:
                if vida_baixa and math.sin(agora * 6.0) > 0.3:
                    img = self.coracao_claro
                else:
                    img = self.coracao_cheio
            else:
                img = self.coracao_vazio
            tela.blit(img, (9 + i * 10, 8))

        # ouro
        tela.blit(self.moeda, (9, 19))
        comum.texto(tela, self.fonte, str(self.mundo.ouro), 21, 18, config.AMARELO)

        # arco equipado
        self._icone_arco(tela, 11, 31, self.mundo.arco.cor)
        comum.texto(tela, self.fonte, self.mundo.arco.nome, 22, 31, config.VERDE)

        # canto direito: onde estamos + estado do som
        if local:
            larg = self.fonte.size(local)[0]
            if local not in self._placas_local:
                self._placas_local[local] = self._fazer_placa(larg + 12, 16)
            tela.blit(self._placas_local[local], (config.LARGURA - larg - 15, 3))
            comum.texto(tela, self.fonte, local, config.LARGURA - larg - 9, 6, config.BRANCO)
        if som.esta_mudo():
            comum.texto(tela, self.fonte, "som off [M]", config.LARGURA - 6 -
                        self.fonte.size("som off [M]")[0], 22, config.CINZA)

        if dica:
            tela.blit(self.faixa_dica, (0, config.ALTURA - 26))
            comum.texto(tela, self.fonte, dica, config.LARGURA // 2,
                        config.ALTURA - 10, config.BRANCO, centro=True)
