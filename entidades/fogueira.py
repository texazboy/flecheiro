# -*- coding: utf-8 -*-
"""
Fogueira-checkpoint.

Chegar perto de uma fogueira acende ela, vira o seu ponto de renascimento (se
cair num vao ou levar dano fatal de queda, volta aqui em vez do inicio) e ainda
recupera um coracao - uma vez por fogueira. Mecanica classica de plataforma que
deixa as fases longas menos punitivas e mais divertidas.
"""

import pygame


class Fogueira:
    def __init__(self, x, chao_y, recursos):
        self.anim = recursos.animacao("fogueira", "arde", 26, fps=8)
        self.rect = pygame.Rect(0, 0, 22, 24)
        self.rect.midbottom = (x, chao_y)
        self.ativada = False     # ja virou checkpoint
        self.curou = False       # ja deu o coracao

    def perto_de(self, rect):
        return abs(self.rect.centerx - rect.centerx) < 26 and \
            abs(self.rect.bottom - rect.bottom) < 30

    def atualizar(self, dt):
        self.anim.atualizar(dt)

    def desenhar(self, tela, camera):
        quadro = self.anim.quadro()
        if not self.ativada:
            # apagada: bem escurecida ate o jogador chegar
            quadro = quadro.copy()
            quadro.fill((90, 90, 90, 255), special_flags=pygame.BLEND_RGBA_MULT)
        destino = quadro.get_rect(midbottom=camera.aplicar(self.rect).midbottom)
        tela.blit(quadro, destino)
