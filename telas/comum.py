# -*- coding: utf-8 -*-
"""
Funcoes de desenho reaproveitadas pelas telas (texto, painel, etc.).

O texto renderizado fica num cache: a HUD escreve as mesmas frases todo frame
e o font.render do pygame nao e de graca. Quando o cache passa do limite a
gente simplesmente zera ele (acontece raramente, ex. textos de dano que mudam).
"""

import pygame

import config

_cache_texto = {}


def _render(fonte, msg, cor):
    chave = (id(fonte), msg, cor)
    img = _cache_texto.get(chave)
    if img is None:
        if len(_cache_texto) > 400:
            _cache_texto.clear()
        img = fonte.render(msg, True, cor)
        _cache_texto[chave] = img
    return img


def texto(tela, fonte, msg, x, y, cor=config.BRANCO, centro=False, sombra=True):
    img = _render(fonte, msg, cor)
    r = img.get_rect()
    if centro:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    if sombra:
        tela.blit(_render(fonte, msg, config.PRETO), (r.x + 1, r.y + 1))
    tela.blit(img, r)
    return r


def painel(tela, rect, cor_fundo=(28, 30, 44), cor_borda=config.BRANCO, alpha=235):
    """Desenha um painel semi-transparente com borda."""
    superficie = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    superficie.fill((cor_fundo[0], cor_fundo[1], cor_fundo[2], alpha))
    tela.blit(superficie, rect.topleft)
    pygame.draw.rect(tela, cor_borda, rect, 1)


def escurecer(tela, alpha=150):
    """Cobre a tela toda com um veu escuro (pra destacar um overlay por cima)."""
    veu = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
    veu.fill((0, 0, 0, alpha))
    tela.blit(veu, (0, 0))
