# -*- coding: utf-8 -*-
"""
A flecha do arqueiro.

E a mecanica central do jogo: a flecha voa em arco (tem gravidade propria) e,
quando bate numa estrutura solida, ela se FINCA e vira uma pequena plataforma em
que o jogador pode subir. Atirando flechas numa parede da pra escalar.

Quem trata a colisao flecha-inimigo e a Fase (pra ja cuidar do drop de item);
aqui a flecha cuida do voo, de fincar na parede e de sumir quando sai do mundo.
"""

import math

import pygame

import config


class Flecha:
    def __init__(self, x, y, dir_x, dir_y, dano, vel_mult, recursos):
        self.sprite = recursos.sprite_flecha()
        vel = config.FORCA_FLECHA * vel_mult
        self.x = float(x)
        self.y = float(y)
        self.vx = dir_x * vel
        self.vy = dir_y * vel
        self.dano = dano
        self.angulo = math.atan2(self.vy, self.vx)
        self.fincada = False
        self.morta = False        # marcada para remocao
        self.rect = pygame.Rect(0, 0, 6, 6)
        self.rect.center = (int(self.x), int(self.y))

    def atualizar(self, dt, fase):
        if self.fincada:
            return

        self.vy = min(self.vy + config.GRAVIDADE_FLECHA, config.VEL_MAX_QUEDA)
        self.x += self.vx
        self.y += self.vy
        self.angulo = math.atan2(self.vy, self.vx)
        self.rect.center = (int(self.x), int(self.y))

        # bateu numa estrutura solida? finca.
        for s in fase.solidos:
            if self.rect.colliderect(s):
                self._fincar(s)
                return

        # saiu do mundo -> some
        if (self.y > fase.altura_mundo + 60 or self.x < -60
                or self.x > fase.largura_mundo + 60):
            self.morta = True

    def _fincar(self, solido):
        self.fincada = True
        self.vx = 0.0
        self.vy = 0.0
        # encosta a ponta na superficie que bateu (so pra ficar bonitinho)
        self.x = max(solido.left, min(self.x, solido.right))
        self.y = max(solido.top, min(self.y, solido.bottom))
        self.rect.center = (int(self.x), int(self.y))

    def plataforma_rect(self):
        """A barrinha em que o jogador consegue pisar (so quando fincada)."""
        return pygame.Rect(int(self.x) - 8, int(self.y) - 2, 16, 5)

    def desenhar(self, tela, camera):
        graus = -math.degrees(self.angulo)
        img = pygame.transform.rotate(self.sprite, graus)
        destino = img.get_rect(center=camera.aplicar_ponto((self.x, self.y)))
        tela.blit(img, destino)
        if self.fincada:
            # mostra de leve a plataforma onde da pra pisar
            p = camera.aplicar(self.plataforma_rect())
            pygame.draw.line(tela, config.MARROM_CLARO, (p.left, p.top), (p.right, p.top), 1)
