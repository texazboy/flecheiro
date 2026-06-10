# -*- coding: utf-8 -*-
"""
Desenho do cenario: fundo com parallax e chao/plataformas feitos de tiles.

Tudo tem fallback procedural, entao funciona sem nenhuma imagem. Se existir
'fundo.png' em assets/, ele e usado como camada distante; senao desenhamos
morros em camadas (com parallax) na mao. O chao/plataformas usam os tiles do
Recursos (que tambem tem fallback).
"""

import pygame

import config


class Fundo:
    """Fundo do cenario, com rolagem em parallax (camadas em velocidades diferentes)."""

    def __init__(self, recursos, tema="dia"):
        self.tema = tema
        self.cor_ceu = config.AZUL_NOITE if tema == "noite" else config.AZUL_CEU
        self.img = recursos.fundo_img()  # Surface ou None

    def desenhar(self, tela, offset_x):
        tela.fill(self.cor_ceu)
        if self.img is not None:
            self._tile_horizontal(tela, self.img, offset_x * 0.3)
        else:
            self._morros(tela, offset_x)

    def _tile_horizontal(self, tela, img, deslocamento):
        w = img.get_width()
        y = tela.get_height() - img.get_height()
        x = -(int(deslocamento) % w) - w
        while x < tela.get_width():
            tela.blit(img, (x, y))
            x += w

    def _morros(self, tela, offset_x):
        if self.tema == "noite":
            camadas = [((40, 52, 84), 0.3, 150, 175, 260),
                       ((30, 40, 66), 0.55, 175, 200, 200)]
        else:
            camadas = [((78, 140, 96), 0.3, 150, 175, 260),
                       (config.VERDE_ESCURO, 0.55, 175, 200, 200)]
        for cor, fator, raio_y, base_y, passo in camadas:
            deslocamento = int(offset_x * fator) % passo
            x = -passo - deslocamento
            while x < config.LARGURA + passo:
                pygame.draw.ellipse(tela, cor, (x, base_y, passo + 60, raio_y))
                x += passo


def desenhar_solido(tela, rect_tela, tile_topo, tile_miolo):
    """Preenche um retangulo solido com tiles: grama no topo, terra no resto."""
    tw, th = tile_miolo.get_size()
    clip_antigo = tela.get_clip()
    tela.set_clip(rect_tela)
    for tx in range(rect_tela.left, rect_tela.right, tw):
        tela.blit(tile_topo, (tx, rect_tela.top))
        ty = rect_tela.top + th
        while ty < rect_tela.bottom:
            tela.blit(tile_miolo, (tx, ty))
            ty += th
    tela.set_clip(clip_antigo)


def desenhar_plataforma(tela, rect_tela, tile):
    tw = tile.get_width()
    clip_antigo = tela.get_clip()
    tela.set_clip(rect_tela)
    for tx in range(rect_tela.left, rect_tela.right, tw):
        tela.blit(tile, (tx, rect_tela.top))
    tela.set_clip(clip_antigo)
