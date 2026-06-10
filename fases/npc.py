# -*- coding: utf-8 -*-
"""
NPCs amigaveis da vila.

Todos tem dialogo simples. Alem do papo, o ferreiro abre a ferraria (mochila) e
o lojista abre a loja - isso fica indicado pelo campo 'acao'. O NPC de dialogo
("aldeao") so conversa mesmo.
"""

import pygame

import config
from telas import comum


class NPC:
    def __init__(self, x, y, tipo, nome, falas, cor, recursos, acao="dialogo"):
        self.tipo = tipo
        self.nome = nome
        self.falas = falas
        self.acao = acao          # "dialogo", "ferreiro" ou "lojista"
        self.sprite = recursos.sprite_npc(tipo, cor)
        self.rect = self.sprite.get_rect(midbottom=(x, y))
        self._fonte = recursos.fonte(15)

    def perto_de(self, rect, distancia=22):
        return abs(self.rect.centerx - rect.centerx) < distancia and \
            abs(self.rect.centery - rect.centery) < 40

    def desenhar(self, tela, camera, destacar=False):
        destino = camera.aplicar(self.rect)
        tela.blit(self.sprite, destino)
        # nome em cima
        comum.texto(tela, self._fonte, self.nome, destino.centerx, destino.top - 16,
                    config.BRANCO, centro=True)
        if destacar:
            comum.texto(tela, self._fonte, "[E]", destino.centerx, destino.top - 4,
                        config.AMARELO, centro=True)
