# -*- coding: utf-8 -*-
"""
Tela de pausa (Esc). Antes o Esc jogava direto pro menu e perdia a fase toda;
agora pausa de verdade, mostra os controles (com as teclinhas desenhadas) e
deixa escolher entre continuar ou desistir pro menu.
"""

import pygame

import config
from core import som
from telas import comum

# (tecla, acao) - viram keycaps na tela
_CONTROLES = [
    ("A/D", "andar"),
    ("Espaco", "pular"),
    ("Mouse", "segurar tensiona o arco, soltar atira"),
    ("E", "coletar / conversar"),
    ("T", "rota otima de coleta (TSP)"),
    ("I", "inventario"),
    ("M", "som liga/desliga"),
]


class Pausa:
    def __init__(self, recursos):
        self.fonte = recursos.fonte(24)
        self.fonte_p = recursos.fonte(15)
        self._nasceu = pygame.time.get_ticks()

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
        desloc = int((1.0 - comum.surgimento(self._nasceu)) * 14)
        painel = pygame.Rect(94, 30 + desloc, config.LARGURA - 188, config.ALTURA - 60)
        comum.painel(tela, painel)

        comum.faixa_titulo(tela, self.fonte, "PAUSA", painel.centerx, painel.top + 16)
        comum.separador(tela, painel.left + 10, painel.right - 10, painel.top + 30)

        y = painel.top + 40
        for tecla_txt, acao in _CONTROLES:
            r = comum.keycap(tela, self.fonte_p, tecla_txt, painel.left + 14, y)
            comum.texto(tela, self.fonte_p, acao, r.right + 8, y + 1, config.BRANCO)
            y += 17

        comum.separador(tela, painel.left + 10, painel.right - 10, painel.bottom - 28)
        comum.legenda_teclas(tela, self.fonte_p,
                             [("Esc", "continuar"), ("Q", "desistir")],
                             painel.centerx, painel.bottom - 21)
