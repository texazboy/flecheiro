# -*- coding: utf-8 -*-
"""
Sistema simples de animacao por quadros (frames).

Uma Animacao guarda uma lista de superficies e troca de quadro no tempo certo.
Cada entidade tem a SUA Animacao (com tempo/indice proprios), mas os quadros em
si ficam em cache no Recursos pra nao recortar o spritesheet toda hora.
"""

import pygame


def fatiar_tira(spritesheet, quantidade):
    """
    Corta uma tira HORIZONTAL de quadros do mesmo tamanho.
    Ex.: uma imagem 64x16 com 4 quadros -> 4 superficies de 16x16.
    """
    quantidade = max(1, quantidade)
    largura = spritesheet.get_width() // quantidade
    altura = spritesheet.get_height()
    quadros = []
    for i in range(quantidade):
        recorte = pygame.Rect(i * largura, 0, largura, altura)
        quadros.append(spritesheet.subsurface(recorte).copy())
    return quadros


class Animacao:
    def __init__(self, quadros, fps=8, repetir=True):
        self.quadros = quadros if quadros else [pygame.Surface((1, 1), pygame.SRCALPHA)]
        self.duracao = 1.0 / max(1, fps)
        self.repetir = repetir
        self.tempo = 0.0
        self.indice = 0

    def reiniciar(self):
        self.tempo = 0.0
        self.indice = 0

    def atualizar(self, dt):
        if len(self.quadros) <= 1:
            return
        self.tempo += dt
        while self.tempo >= self.duracao:
            self.tempo -= self.duracao
            self.indice += 1
            if self.indice >= len(self.quadros):
                self.indice = 0 if self.repetir else len(self.quadros) - 1

    def quadro(self):
        return self.quadros[self.indice]

    def terminou(self):
        return (not self.repetir) and self.indice >= len(self.quadros) - 1
