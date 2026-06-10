# -*- coding: utf-8 -*-
"""
Loja do lojista.

Bem direta: vende os materiais coletados por ouro (cada um vale o seu 'valor') e
compra uma cura que recupera um coracao. Setas pra navegar, Enter pra vender.
"""

import pygame

import config
from telas import comum

CUSTO_CURA = 6


class Loja:
    def __init__(self, mundo, recursos):
        self.mundo = mundo
        self.recursos = recursos
        self.fonte = recursos.fonte(18)
        self.fonte_p = recursos.fonte(15)
        self.selecao = 0
        self.mensagem = "Setas: escolher  |  Enter: vender  |  C: comprar cura"

    def _itens(self):
        return self.mundo.inventario.listar()

    def tratar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return False
        if evento.key in (pygame.K_ESCAPE, pygame.K_q):
            return True

        itens = self._itens()
        if evento.key in (pygame.K_UP, pygame.K_w):
            self.selecao = max(0, self.selecao - 1)
        elif evento.key in (pygame.K_DOWN, pygame.K_s):
            self.selecao = min(max(0, len(itens) - 1), self.selecao + 1)
        elif evento.key in (pygame.K_RETURN, pygame.K_v):
            self._vender(itens)
        elif evento.key == pygame.K_c:
            self._comprar_cura()
        return False

    def _vender(self, itens):
        if not itens:
            self.mensagem = "Nao ha nada para vender."
            return
        self.selecao = min(self.selecao, len(itens) - 1)
        material, _ = itens[self.selecao]
        self.mundo.inventario.remover(material, 1)
        self.mundo.ouro += material.valor
        self.mensagem = f"Vendeu {material.nome} por {material.valor} de ouro."
        # ajusta selecao se o tipo acabou
        if self.selecao >= len(self._itens()):
            self.selecao = max(0, len(self._itens()) - 1)

    def _comprar_cura(self):
        if self.mundo.vida >= self.mundo.vida_max:
            self.mensagem = "Sua vida ja esta cheia."
        elif self.mundo.ouro < CUSTO_CURA:
            self.mensagem = f"Ouro insuficiente (precisa de {CUSTO_CURA})."
        else:
            self.mundo.ouro -= CUSTO_CURA
            self.mundo.vida += 1
            self.mensagem = "Recuperou um coracao!"

    def desenhar(self, tela):
        comum.escurecer(tela, 175)
        painel = pygame.Rect(28, 20, config.LARGURA - 56, config.ALTURA - 40)
        comum.painel(tela, painel, cor_fundo=(26, 34, 46))

        comum.texto(tela, self.fonte, "LOJA", painel.centerx, painel.top + 12,
                    config.AZUL_CEU, centro=True)
        comum.texto(tela, self.fonte_p, f"Ouro: {self.mundo.ouro}    Cura: {CUSTO_CURA} ouro [C]",
                    painel.centerx, painel.top + 28, config.AMARELO, centro=True)

        itens = self._itens()
        y = painel.top + 48
        if not itens:
            comum.texto(tela, self.fonte_p, "(sem materiais para vender)",
                        painel.centerx, painel.centery, config.CINZA, centro=True)
        else:
            for i, (material, qtd) in enumerate(itens):
                cor = config.AMARELO if i == self.selecao else config.BRANCO
                marcador = ">" if i == self.selecao else " "
                comum.texto(tela, self.fonte_p,
                            f"{marcador} {material.nome} x{qtd}  -  vende por {material.valor}",
                            painel.left + 16, y, cor)
                y += 17

        comum.texto(tela, self.fonte_p, self.mensagem, painel.centerx, painel.bottom - 30,
                    config.BRANCO, centro=True)
        comum.texto(tela, self.fonte_p, "[Q] sair", painel.centerx, painel.bottom - 14,
                    config.CINZA, centro=True)
