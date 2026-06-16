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
        # coracao do Cryo's Mini GUI se existir; senao o desenhado na mao
        img = recursos.sprite_opcional("coracao")
        if img is not None:
            img = pygame.transform.scale(img, (10, 10))
            self.coracao_cheio = img
            claro = img.copy()
            claro.fill((40, 40, 40), special_flags=pygame.BLEND_RGB_ADD)
            self.coracao_claro = claro
            vazio = img.copy()
            vazio.fill((90, 90, 90, 255), special_flags=pygame.BLEND_RGBA_MULT)
            vazio.fill((30, 26, 34), special_flags=pygame.BLEND_RGB_ADD)
            self.coracao_vazio = vazio
            self._passo_coracao = 11
        else:
            self.coracao_cheio = _desenhar_mapa(_MAPA_CORACAO, config.VERMELHO, brilho=True)
            self.coracao_claro = _desenhar_mapa(_MAPA_CORACAO, (255, 120, 110), brilho=True)
            self.coracao_vazio = _desenhar_mapa(_MAPA_CORACAO, (58, 50, 66))
            self._passo_coracao = 10
        self.moeda = self._fazer_moeda()
        self.placa = self._fazer_placa(126, 44)
        self.faixa_dica = self._fazer_faixa_dica()
        self.alerta_vida = self._fazer_alerta_vida()
        self._placas_local = {}   # cache das placas do canto direito
        # barra de HP ornamentada (GandalfHardcore) se existir
        self.hpframe = recursos.sprite_opcional("hpbar")   # 116x64
        if self.hpframe is not None:
            self.placa_dados = self._fazer_placa(86, 30)   # ouro + arco ao lado

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

    def _desenhar_hpframe(self, tela, agora, vida_baixa):
        """HUD com a barra ornamentada do GandalfHardcore: retrato (arco) +
        barra de vida, e ouro/arco numa placa ao lado."""
        tela.blit(self.hpframe, (2, 2))
        # retrato: disco escuro + arco no circulo da esquerda
        pygame.draw.circle(tela, (20, 18, 28), (2 + 31, 2 + 30), 22)
        self._icone_arco(tela, 2 + 24, 2 + 24, self.mundo.arco.cor)
        # barra de vida preenchendo o slot segmentado (canto inferior direito)
        barra = pygame.Rect(2 + 60, 2 + 48, 49, 9)
        pygame.draw.rect(tela, (34, 14, 14), barra)
        frac = self.mundo.vida / self.mundo.vida_max
        if frac > 0:
            cor = (210, 64, 58)
            if vida_baixa and math.sin(agora * 6.0) > 0.3:
                cor = (255, 130, 120)
            fill = pygame.Rect(barra.left, barra.top, int(barra.width * frac), barra.height)
            pygame.draw.rect(tela, cor, fill)
            pygame.draw.line(tela, (255, 150, 140), (fill.left, fill.top),
                             (fill.right - 1, fill.top), 1)
        # placa lateral com ouro + arco
        tela.blit(self.placa_dados, (120, 6))
        tela.blit(self.moeda, (126, 12))
        comum.texto(tela, self.fonte, str(self.mundo.ouro), 138, 11, config.AMARELO)
        comum.texto(tela, self.fonte, self.mundo.arco.nome, 126, 23, config.VERDE)

    # ------------------------------------------------------------- frame
    def desenhar(self, tela, dica="", local=""):
        agora = pygame.time.get_ticks() * 0.001

        # com um coracao so, as bordas pulsam em vermelho (perigo!)
        vida_baixa = self.mundo.vida == 1
        if vida_baixa:
            pulso = (math.sin(agora * 6.0) + 1) / 2
            self.alerta_vida.set_alpha(int(110 + 130 * pulso))
            tela.blit(self.alerta_vida, (0, 0))

        if self.hpframe is not None:
            self._desenhar_hpframe(tela, agora, vida_baixa)
        else:
            tela.blit(self.placa, (3, 3))
            for i in range(self.mundo.vida_max):
                if i < self.mundo.vida:
                    if vida_baixa and math.sin(agora * 6.0) > 0.3:
                        img = self.coracao_claro
                    else:
                        img = self.coracao_cheio
                else:
                    img = self.coracao_vazio
                tela.blit(img, (9 + i * self._passo_coracao, 7))
            tela.blit(self.moeda, (9, 19))
            comum.texto(tela, self.fonte, str(self.mundo.ouro), 21, 18, config.AMARELO)
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
