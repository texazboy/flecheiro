# -*- coding: utf-8 -*-
"""
Efeitinhos visuais ("juice"): particulas e textos flutuantes.

Nada essencial pra jogabilidade, mas e o que faz o jogo parecer vivo: uma
poeirinha quando um inimigo morre, um brilho quando o item e coletado e um
"+Madeira" subindo quando voce pega algo.
"""

import math
import random

import pygame


class Particula:
    def __init__(self, x, y, cor):
        self.x = float(x)
        self.y = float(y)
        ang = random.uniform(0, math.tau)
        forca = random.uniform(0.6, 2.2)
        self.vx = math.cos(ang) * forca
        self.vy = math.sin(ang) * forca - 1.0   # joga um pouco pra cima
        self.cor = cor
        self.vida = random.uniform(0.3, 0.6)
        self.tam = random.randint(1, 3)

    @property
    def morta(self):
        return self.vida <= 0

    def atualizar(self, dt):
        self.vy += 0.15           # gravidadezinha
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


def explosao(x, y, cor, quantidade=10):
    """Devolve uma lista de particulas saindo de um ponto."""
    return [Particula(x, y, cor) for _ in range(quantidade)]
