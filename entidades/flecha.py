# -*- coding: utf-8 -*-
"""
A flecha do arqueiro.

E a mecanica central do jogo: a flecha voa em arco (tem gravidade propria) e,
quando bate numa estrutura solida, ela se FINCA e vira uma pequena plataforma em
que o jogador pode subir. Atirando flechas numa parede da pra escalar - e nos
vaos da fase 3 elas tambem servem de ponte.

Quem trata a colisao flecha-inimigo e a Fase (pra ja cuidar do drop de item);
aqui a flecha cuida do voo, de fincar na parede e de sumir quando sai do mundo.

Detalhe de desempenho: rotacionar a imagem todo frame e caro, entao guardamos
as rotacoes ja calculadas num cache de 10 em 10 graus (a olho nao da pra notar
a diferenca, e economiza milhares de rotates por segundo).
"""

import math

import pygame

import config
from core import som


class Flecha:
    _cache_rotacao = {}

    def __init__(self, x, y, dir_x, dir_y, dano, velocidade, recursos):
        self.sprite = recursos.sprite_flecha()
        self.x = float(x)
        self.y = float(y)
        self.vx = dir_x * velocidade
        self.vy = dir_y * velocidade
        self.dano = dano
        self.angulo = math.atan2(self.vy, self.vx)
        self.fincada = False
        self.morta = False        # marcada para remocao
        self.balanco = 0.0        # vibracao logo depois de fincar
        self.rect = pygame.Rect(0, 0, 6, 6)
        self.rect.center = (int(self.x), int(self.y))

    def atualizar(self, dt, fase):
        if self.fincada:
            if self.balanco > 0:
                self.balanco = max(0.0, self.balanco - dt)
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
        self.balanco = 0.35       # treme um pouquinho com o impacto
        som.tocar("fincar")

    def plataforma_rect(self):
        """A barrinha em que o jogador consegue pisar (so quando fincada)."""
        return pygame.Rect(int(self.x) - 8, int(self.y) - 2, 16, 5)

    def _quadro_rotacionado(self):
        graus_base = -math.degrees(self.angulo)
        if self.balanco > 0:
            forca = self.balanco / 0.35
            graus_base += math.sin(self.balanco * 45.0) * 10.0 * forca
        graus = int(round(graus_base / 10.0)) * 10 % 360
        chave = (id(self.sprite), graus)
        img = Flecha._cache_rotacao.get(chave)
        if img is None:
            img = pygame.transform.rotate(self.sprite, graus)
            Flecha._cache_rotacao[chave] = img
        return img

    def desenhar(self, tela, camera):
        img = self._quadro_rotacionado()
        destino = img.get_rect(center=camera.aplicar_ponto((self.x, self.y)))
        tela.blit(img, destino)
        if self.fincada:
            # mostra de leve a plataforma onde da pra pisar
            p = camera.aplicar(self.plataforma_rect())
            pygame.draw.line(tela, config.MARROM_CLARO, (p.left, p.top), (p.right, p.top), 1)
