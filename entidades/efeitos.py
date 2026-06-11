# -*- coding: utf-8 -*-
"""
Efeitinhos visuais ("juice"): particulas e textos flutuantes.

Nada essencial pra jogabilidade, mas e o que faz o jogo parecer vivo: poeira
quando um inimigo morre, brilho quando o item e coletado, rastro atras da
flecha, fumaca subindo da chamine da vila...

A Particula e generica: os parametros opcionais controlam espalhamento,
gravidade e tempo de vida, e as funcoes la embaixo (explosao, faisca, fumaca)
sao so receitas prontas com valores que ficaram bons no olho.
"""

import math
import random

import pygame


class Particula:
    def __init__(self, x, y, cor, espalhar=2.2, sobe=1.0, gravidade=0.15,
                 vida=(0.3, 0.6), tam=(1, 3)):
        self.x = float(x)
        self.y = float(y)
        ang = random.uniform(0, math.tau)
        forca = random.uniform(0.3, 1.0) * espalhar
        self.vx = math.cos(ang) * forca
        self.vy = math.sin(ang) * forca - sobe
        self.gravidade = gravidade
        self.cor = cor
        self.vida = random.uniform(*vida)
        self.tam = random.randint(*tam)

    @property
    def morta(self):
        return self.vida <= 0

    def atualizar(self, dt):
        self.vy += self.gravidade
        self.x += self.vx
        self.y += self.vy
        self.vida -= dt

    def desenhar(self, tela, camera):
        px, py = camera.aplicar_ponto((self.x, self.y))
        pygame.draw.rect(tela, self.cor, (int(px), int(py), self.tam, self.tam))


class TextoFlutuante:
    def __init__(self, x, y, texto, cor, recursos):
        self.x = float(x)
        self.y = float(y)
        self.texto = texto
        self.cor = cor
        self.fonte = recursos.fonte(15)
        self.vida = 0.8

    @property
    def morto(self):
        return self.vida <= 0

    def atualizar(self, dt):
        self.y -= 18 * dt          # sobe devagar
        self.vida -= dt

    def desenhar(self, tela, camera):
        from telas import comum  # import local pra evitar import circular
        px, py = camera.aplicar_ponto((self.x, self.y))
        comum.texto(tela, self.fonte, self.texto, int(px), int(py), self.cor, centro=True)


# ------------------------------------------------------------- receitas
def explosao(x, y, cor, quantidade=10):
    """Estouro de poeira: usado em morte de inimigo e coleta de item."""
    return [Particula(x, y, cor) for _ in range(quantidade)]


def faisca(x, y, cor):
    """Pontinho que quase nao se mexe; serve de rastro e de brilho de porta."""
    return Particula(x, y, cor, espalhar=0.4, sobe=0.1, gravidade=0.0,
                     vida=(0.15, 0.35), tam=(1, 1))


def fumaca(x, y):
    """Fumacinha que sobe devagar (chamine da vila)."""
    return Particula(x, y, (152, 152, 162), espalhar=0.25, sobe=0.35,
                     gravidade=-0.01, vida=(1.2, 2.0), tam=(2, 3))
