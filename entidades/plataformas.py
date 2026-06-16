# -*- coding: utf-8 -*-
"""
Plataformas dinamicas: as que se movem e as que desmoronam quando voce pisa.

As duas sao plataformas de "uma via" (so seguram por cima), igual as flutuantes
normais - a diferenca e que o rect delas muda com o tempo. A Fase trata o
"carregar o jogador junto" (plataforma movel) e o "avisar que pisou" (fragil).
"""

import math

import pygame

import config


def _desenhar_madeira(tela, rect_tela, tile, tom=None):
    """Preenche um rect com o tile de plataforma, com clip e tinta opcional."""
    clip = tela.get_clip()
    tela.set_clip(rect_tela)
    for tx in range(rect_tela.left, rect_tela.right, tile.get_width()):
        tela.blit(tile, (tx, rect_tela.top))
    tela.set_clip(clip)
    if tom:
        veu = pygame.Surface(rect_tela.size, pygame.SRCALPHA)
        veu.fill(tom)
        tela.blit(veu, rect_tela.topleft)


class PlataformaMovel:
    """Plataforma que vai e volta num eixo. O jogador anda junto quando esta
    em cima dela."""

    def __init__(self, x, y, largura, eixo="h", amplitude=64, periodo=3.2):
        self.rect = pygame.Rect(x, y, largura, 10)
        self.base_x = x
        self.base_y = y
        self.eixo = eixo
        self.amplitude = amplitude
        self.omega = 2 * math.pi / periodo
        self.tempo = 0.0
        self.dx = 0
        self.dy = 0

    def atualizar(self, dt):
        self.tempo += dt
        ox, oy = self.rect.x, self.rect.y
        desloc = math.sin(self.tempo * self.omega) * self.amplitude
        if self.eixo == "h":
            self.rect.x = int(self.base_x + desloc)
        else:
            self.rect.y = int(self.base_y + desloc)
        self.dx = self.rect.x - ox
        self.dy = self.rect.y - oy

    def desenhar(self, tela, camera, tile):
        r = camera.aplicar(self.rect)
        _desenhar_madeira(tela, r, tile, tom=(120, 150, 200, 40))   # tom azulado
        pygame.draw.rect(tela, (90, 120, 170), r, 1)
        # setinhas indicando que ela se mexe
        cor = (210, 225, 245)
        cy = r.centery
        if self.eixo == "h":
            pygame.draw.polygon(tela, cor, [(r.left - 5, cy), (r.left - 1, cy - 3), (r.left - 1, cy + 3)])
            pygame.draw.polygon(tela, cor, [(r.right + 5, cy), (r.right + 1, cy - 3), (r.right + 1, cy + 3)])
        else:
            cx = r.centerx
            pygame.draw.polygon(tela, cor, [(cx, r.top - 5), (cx - 3, r.top - 1), (cx + 3, r.top - 1)])
            pygame.draw.polygon(tela, cor, [(cx, r.bottom + 5), (cx - 3, r.bottom + 1), (cx + 3, r.bottom + 1)])


class PlataformaFragil:
    """Pisou, ela treme e cai; depois de um tempo, volta. Boa pra travessias
    de ritmo (nao da pra ficar parado)."""

    ESPERA_QUEDA = 0.55
    TEMPO_FORA = 2.2

    def __init__(self, x, y, largura):
        self.rect = pygame.Rect(x, y, largura, 10)
        self.estado = "firme"      # firme -> tremendo -> caiu -> firme
        self.timer = 0.0
        self.tremor = 0.0

    @property
    def solida(self):
        return self.estado in ("firme", "tremendo")

    def pisada(self):
        if self.estado == "firme":
            self.estado = "tremendo"
            self.timer = self.ESPERA_QUEDA

    def atualizar(self, dt):
        if self.estado == "tremendo":
            self.timer -= dt
            self.tremor = math.sin(self.timer * 50) * 1.4
            if self.timer <= 0:
                self.estado = "caiu"
                self.timer = self.TEMPO_FORA
        elif self.estado == "caiu":
            self.timer -= dt
            if self.timer <= 0:
                self.estado = "firme"
                self.tremor = 0.0

    def desenhar(self, tela, camera, tile):
        r = camera.aplicar(self.rect)
        if self.estado == "caiu":
            # so o contorno tracejado de onde ela volta
            for x in range(r.left, r.right, 6):
                pygame.draw.line(tela, (90, 80, 70), (x, r.top), (x + 3, r.top), 1)
            return
        if self.estado == "tremendo":
            r = r.move(int(self.tremor), 0)
        _desenhar_madeira(tela, r, tile, tom=(40, 20, 16, 40))      # tom rachado
        pygame.draw.line(tela, (60, 36, 24), (r.left + 4, r.top + 4),
                         (r.left + 9, r.bottom - 3), 1)             # rachadura
        pygame.draw.line(tela, (60, 36, 24), (r.right - 7, r.top + 3),
                         (r.right - 3, r.bottom - 4), 1)
