# -*- coding: utf-8 -*-
"""Funcoes de desenho reaproveitadas pelas telas (texto, painel, etc.)."""

import pygame

import config


def texto(tela, fonte, msg, x, y, cor=config.BRANCO, centro=False, sombra=True):
    img = fonte.render(msg, True, cor)
    r = img.get_rect()
    if centro:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    if sombra:
        sombra_img = fonte.render(msg, True, config.PRETO)
        tela.blit(sombra_img, (r.x + 1, r.y + 1))
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
