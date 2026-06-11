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
import random
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


class Moeda:
    """Moedinha fisica: pula, quica no chao e voa pro jogador quando ele
    chega perto (efeito ima). Coleta automatica no toque."""

    def __init__(self, x, y, recursos):
        self.sprite = recursos.sprite_moeda()
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-1.4, 1.4)
        self.vy = random.uniform(-3.2, -1.6)
        self.rect = self.sprite.get_rect(center=(int(x), int(y)))
        self.coletada = False
        self.vida = 12.0          # some sozinha se ninguem pegar

    def atualizar(self, dt, fase, jogador):
        self.vida -= dt
        # ima: perto do jogador, a moeda corre pra ele
        dx = jogador.rect.centerx - self.x
        dy = jogador.rect.centery - self.y
        dist2 = dx * dx + dy * dy
        if dist2 < 42 * 42 and dist2 > 1:
            dist = dist2 ** 0.5
            self.vx = dx / dist * 3.2
            self.vy = dy / dist * 3.2
        else:
            self.vy = min(self.vy + 0.28, 8.0)
            self.vx *= 0.99

        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))

        # quica nos solidos (so por cima, o suficiente pro efeito)
        if self.vy > 0:
            for s in fase.solidos:
                if self.rect.colliderect(s) and self.rect.bottom - self.vy <= s.top + 4:
                    self.rect.bottom = s.top
                    self.y = float(self.rect.centery)
                    self.vy = -self.vy * 0.45
                    self.vx *= 0.8
                    if abs(self.vy) < 0.7:
                        self.vy = 0.0
                        self.vx = 0.0
                    break

        if self.rect.colliderect(jogador.rect):
            self.coletada = True

    @property
    def sumiu(self):
        return self.coletada or self.vida <= 0

    def desenhar(self, tela, camera):
        # gira "de mentira" estreitando na horizontal
        fase_giro = (pygame.time.get_ticks() * 0.006 + self.x * 0.3) % 2.0
        larg = max(1, int(self.sprite.get_width() * abs(fase_giro - 1.0)))
        img = pygame.transform.scale(self.sprite, (larg, self.sprite.get_height()))
        destino = img.get_rect(center=camera.aplicar(self.rect).center)
        tela.blit(img, destino)


class Bau:
    """Bau de tesouro: abre com E e cospe materiais + moedas."""

    def __init__(self, x, y, conteudo, recursos):
        self.recursos = recursos
        self.conteudo = conteudo          # tuplinha de chaves de material
        self.aberto = False
        self.sprite = recursos.sprite_bau(False)
        self.rect = self.sprite.get_rect(midbottom=(x, y))

    def abrir(self):
        self.aberto = True
        self.sprite = self.recursos.sprite_bau(True)

    def desenhar(self, tela, camera):
        destino = camera.aplicar(self.rect)
        tela.blit(self.sprite, destino)
        if not self.aberto:
            # brilho chamando o jogador
            pulso = (pygame.time.get_ticks() // 400) % 2 == 0
            if pulso:
                pygame.draw.rect(tela, (255, 240, 170),
                                 (destino.centerx - 1, destino.top - 5, 2, 2))


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
