# -*- coding: utf-8 -*-
"""
Tela de pausa (Esc). Antes o Esc jogava direto pro menu e perdia a fase toda;
agora pausa de verdade, mostra os controles e deixa escolher entre continuar
ou desistir pro menu.
"""

import pygame

import config
from core import som
from telas import comum

_CONTROLES = [
    "A/D ou setas .... andar",
    "Espaco ......... pular",
    "Segurar mouse .. tensionar o arco (solta = atira)",
    "E .............. coletar / conversar",
    "T .............. rota otima de coleta (TSP)",
    "I .............. inventario",
    "M .............. som liga/desliga",
]


class Pausa:
    def __init__(self, recursos):
        self.fonte = recursos.fonte(24)
        self.fonte_p = recursos.fonte(15)

    def tratar_evento(self, evento):
        """Devolve 'voltar', 'menu' ou None."""
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_RETURN):
                som.tocar("clique")
                return "voltar"
            if evento.key == pygame.K_q:
                return "menu"
        return None

    def desenhar(self, tela):
        comum.escurecer(tela, 160)
        painel = pygame.Rect(90, 40, config.LARGURA - 180, config.ALTURA - 80)
        comum.painel(tela, painel)
        comum.texto(tela, self.fonte, "PAUSA", painel.centerx, painel.top + 18,
                    config.AMARELO, centro=True)
        y = painel.top + 40
        for linha in _CONTROLES:
            comum.texto(tela, self.fonte_p, linha, painel.left + 14, y, config.BRANCO)
            y += 15
        comum.texto(tela, self.fonte_p, "[Esc] continuar     [Q] desistir pro menu",
                    painel.centerx, painel.bottom - 16, config.CINZA, centro=True)
