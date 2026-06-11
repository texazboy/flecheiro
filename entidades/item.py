# -*- coding: utf-8 -*-
"""
Itens coletaveis do jogo.

Tem duas coisas aqui:
  - Material : a DEFINICAO de um tipo de item (nome, peso, valor, raridade...).
               E so dado, sem nada de pygame -> facil de testar e de usar nos
               algoritmos (mochila usa peso/valor, ordenacao usa raridade).
  - ItemNoChao : o item fisico jogado no mundo quando um inimigo morre. Tem
               posicao, fica "flutuando" de leve e some quando o jogador coleta.
"""

import math
from dataclasses import dataclass

import pygame

import config


@dataclass(frozen=True)
class Material:
    chave: str          # id interno (sem acento), usado como sprite e como chave
    nome: str           # nome exibido na tela (pode ter acento)
    peso: int           # usado na mochila da ferraria
    valor: int          # qualidade que agrega ao forjar / valor de venda
    raridade: str       # comum, incomum, raro...
    cor: tuple          # cor do placeholder quando nao ha sprite


# Catalogo dos materiais que existem no jogo.
MATERIAIS = {
    "madeira": Material("madeira", "Madeira", 2, 3, "comum", config.MARROM),
    "couro":   Material("couro", "Couro", 2, 4, "comum", config.MARROM_CLARO),
    "pena":    Material("pena", "Pena", 1, 2, "comum", config.BRANCO),
    "ferro":   Material("ferro", "Ferro", 3, 7, "incomum", config.CINZA),
    "cristal": Material("cristal", "Cristal", 4, 12, "raro", config.ROXO),
}

# Ordem em que os drops aparecem (do mais comum pro mais raro), so pra
# distribuir os drops dos inimigos de um jeito previsivel.
TABELA_DROPS = ["madeira", "pena", "couro", "ferro", "cristal"]


class ItemNoChao:
    """Item largado no mundo, esperando ser coletado."""

    def __init__(self, x, y, material, recursos):
        self.material = material
        self.sprite = recursos.sprite_item(material)
        self.rect = self.sprite.get_rect(center=(int(x), int(y)))
        self.base_y = float(self.rect.centery)
        self.tempo = 0.0
        self.coletado = False

    @property
    def centro(self):
        return (self.rect.centerx, self.rect.centery)

    def atualizar(self, dt):
        # leve flutuacao pra chamar atencao do jogador
        self.tempo += dt
        desloc = math.sin(self.tempo * 4.0) * 2.0
        self.rect.centery = int(self.base_y + desloc)

    def desenhar(self, tela, camera):
        destino = camera.aplicar(self.rect)
        # sombrinha simples no chao
        sombra = pygame.Rect(0, 0, self.rect.width, 3)
        sombra.center = (destino.centerx, destino.bottom + 4)
        pygame.draw.ellipse(tela, config.CINZA_ESCURO, sombra)
        tela.blit(self.sprite, destino)
