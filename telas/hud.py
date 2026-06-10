# -*- coding: utf-8 -*-
"""HUD: vida (coracoes), ouro, arco equipado e a linha de dicas de teclas."""

import pygame

import config
from telas import comum


class HUD:
    def __init__(self, mundo, recursos):
        self.mundo = mundo
        self.fonte = recursos.fonte(16)

    def desenhar(self, tela, dica=""):
        # coracoes de vida
        for i in range(self.mundo.vida_max):
            x = 6 + i * 12
            cheio = i < self.mundo.vida
            cor = config.VERMELHO if cheio else config.CINZA_ESCURO
            pygame.draw.rect(tela, cor, (x, 6, 9, 8))
            pygame.draw.rect(tela, config.PRETO, (x, 6, 9, 8), 1)

        # ouro e arco
        comum.texto(tela, self.fonte, f"Ouro: {self.mundo.ouro}", 6, 18, config.AMARELO)
        comum.texto(tela, self.fonte, self.mundo.arco.nome, 6, 30, config.VERDE)

        if dica:
            comum.texto(tela, self.fonte, dica, config.LARGURA // 2,
                        config.ALTURA - 10, config.BRANCO, centro=True)
