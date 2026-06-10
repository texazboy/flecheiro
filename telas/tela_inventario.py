# -*- coding: utf-8 -*-
"""
Sobreposicao do inventario (tecla I / Tab).

Mostra os itens coletados e deixa reordenar por valor, peso ou raridade. A
ordenacao usa o Quicksort implementado em algoritmos/ordenacao.py (o problema
computacional extra do projeto).
"""

import pygame

import config
from telas import comum
from algoritmos.ordenacao import quicksort

_RANK_RARIDADE = {"comum": 0, "incomum": 1, "raro": 2, "epico": 3, "lendario": 4}


class TelaInventario:
    def __init__(self, mundo, recursos):
        self.mundo = mundo
        self.recursos = recursos
        self.fonte = recursos.fonte(18)
        self.fonte_p = recursos.fonte(15)
        self.ordenar_por = "valor"

    def tratar_evento(self, evento):
        """Retorna True quando o inventario deve fechar."""
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_i, pygame.K_TAB, pygame.K_ESCAPE):
                return True
            if evento.key in (pygame.K_1, pygame.K_KP1):
                self.ordenar_por = "valor"
            elif evento.key in (pygame.K_2, pygame.K_KP2):
                self.ordenar_por = "peso"
            elif evento.key in (pygame.K_3, pygame.K_KP3):
                self.ordenar_por = "raridade"
        return False

    def _chave_ordenacao(self):
        if self.ordenar_por == "peso":
            return lambda par: par[0].peso
        if self.ordenar_por == "raridade":
            return lambda par: _RANK_RARIDADE.get(par[0].raridade, 0)
        return lambda par: par[0].valor

    def desenhar(self, tela):
        comum.escurecer(tela, 170)
        painel = pygame.Rect(40, 24, config.LARGURA - 80, config.ALTURA - 48)
        comum.painel(tela, painel)

        comum.texto(tela, self.fonte, "INVENTARIO", painel.centerx, painel.top + 14,
                    config.AMARELO, centro=True)
        comum.texto(tela, self.fonte_p,
                    "[1] valor  [2] peso  [3] raridade   -   ordenando por: " + self.ordenar_por,
                    painel.centerx, painel.top + 30, config.CINZA, centro=True)

        pares = self.mundo.inventario.listar()
        pares = quicksort(pares, chave=self._chave_ordenacao(), decrescente=True)

        if not pares:
            comum.texto(tela, self.fonte_p, "(vazio - derrote inimigos pra coletar itens)",
                        painel.centerx, painel.centery, config.CINZA, centro=True)
        else:
            y = painel.top + 48
            peso_total = 0
            for material, qtd in pares:
                sprite = self.recursos.sprite_item(material)
                tela.blit(sprite, (painel.left + 16, y))
                comum.texto(tela, self.fonte_p, f"{material.nome} x{qtd}",
                            painel.left + 36, y, config.BRANCO)
                comum.texto(tela, self.fonte_p,
                            f"peso {material.peso}  valor {material.valor}  ({material.raridade})",
                            painel.left + 150, y, config.CINZA)
                peso_total += material.peso * qtd
                y += 18
            comum.texto(tela, self.fonte_p, f"Peso total: {peso_total}",
                        painel.left + 16, painel.bottom - 18, config.VERDE)

        comum.texto(tela, self.fonte_p, "[I] fechar", painel.right - 70,
                    painel.bottom - 18, config.CINZA)
