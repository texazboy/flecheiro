# -*- coding: utf-8 -*-
"""
Ferraria - aqui o problema da MOCHILA 0/1 vira mecanica.

A bigorna aguenta um peso maximo de material por forja (capacidade). Cada
material tem peso e valor. Ao forjar, rodamos a mochila 0/1 (programacao
dinamica) pra escolher o subconjunto de materiais que maximiza o valor sem
estourar a capacidade - esse valor define a qualidade (e o tipo) do arco novo.

Tambem mostramos, lado a lado, o que a versao GULOSA escolheria, pra deixar
visivel o trade-off: a gulosa e mais rapida mas pode dar um arco pior.
"""

from collections import Counter

import pygame

import config
from core import som
from telas import comum
from algoritmos.mochila import resolver_mochila, mochila_gulosa
from core.mundo import arco_por_qualidade

CAPACIDADE_BIGORNA = 10


class Ferraria:
    def __init__(self, mundo, recursos):
        self.mundo = mundo
        self.recursos = recursos
        self.fonte = recursos.fonte(20)
        self.fonte_p = recursos.fonte(15)
        self.capacidade = CAPACIDADE_BIGORNA
        self.mensagem = "A mochila 0/1 ja separou a melhor combinacao."
        self._nasceu = pygame.time.get_ticks()
        self._recalcular()

    def _recalcular(self):
        unidades = self.mundo.inventario.expandir()
        self.otima = resolver_mochila(unidades, self.capacidade)
        self.gulosa = mochila_gulosa(unidades, self.capacidade)

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_ESCAPE, pygame.K_q):
                return True
            if evento.key in (pygame.K_f, pygame.K_RETURN):
                self._forjar()
        return False

    def _forjar(self):
        if self.otima.valor <= 0:
            self.mensagem = "Voce nao tem materiais para forjar."
            som.tocar("clique")
            return
        # consome os materiais escolhidos pela mochila
        contagem = Counter(m.chave for m in self.otima.selecionados)
        for chave, qtd in contagem.items():
            self.mundo.inventario.remover(chave, qtd)

        arco = arco_por_qualidade(self.otima.valor)
        self.mundo.arco = arco
        self.mundo.arcos_forjados += 1
        self.mensagem = f"Forjou: {arco.nome} (dano {arco.dano})!"
        som.tocar("forja")
        self._recalcular()

    def _resumo(self, resultado):
        contagem = Counter(m.nome for m in resultado.selecionados)
        if not contagem:
            return "nada"
        return ", ".join(f"{nome} x{qtd}" for nome, qtd in contagem.items())

    def desenhar(self, tela):
        comum.escurecer(tela, 175)
        desloc = int((1.0 - comum.surgimento(self._nasceu)) * 14)
        painel = pygame.Rect(24, 12 + desloc, config.LARGURA - 48, config.ALTURA - 24)
        comum.painel(tela, painel, cor_fundo=(44, 32, 26))

        comum.faixa_titulo(tela, self.fonte, "FERRARIA", painel.centerx,
                           painel.top + 14, config.LARANJA)

        # barra da bigorna: quanto da capacidade a selecao otima ocupa
        comum.texto(tela, self.fonte_p, "Bigorna", painel.left + 12, painel.top + 28,
                    config.CINZA)
        barra_rect = pygame.Rect(painel.left + 64, painel.top + 29, 130, 9)
        comum.barra(tela, barra_rect, self.otima.peso / self.capacidade, config.LARANJA)
        comum.texto(tela, self.fonte_p, f"{self.otima.peso}/{self.capacidade} de peso",
                    barra_rect.right + 8, painel.top + 28, config.BRANCO)

        comum.separador(tela, painel.left + 10, painel.right - 10, painel.top + 44)

        # materiais com seus icones
        y = painel.top + 52
        comum.texto(tela, self.fonte_p, "Materiais:", painel.left + 12, y, config.BRANCO)
        y += 16
        if self.mundo.inventario.vazio():
            comum.texto(tela, self.fonte_p, "(nenhum - derrote inimigos!)",
                        painel.left + 18, y, config.CINZA)
            y += 16
        else:
            for material, qtd in self.mundo.inventario.listar():
                sprite = self.recursos.sprite_item(material)
                tela.blit(sprite, (painel.left + 16, y))
                comum.texto(tela, self.fonte_p,
                            f"{material.nome} x{qtd}   peso {material.peso}  valor {material.valor}",
                            painel.left + 32, y, config.BRANCO)
                y += 15

        # cartao da solucao otima (mochila 0/1) com a previa do arco
        y += 4
        cartao = pygame.Rect(painel.left + 10, y, painel.width - 20, 48)
        comum.painel(tela, cartao, cor_fundo=(32, 46, 32), alpha=255)
        arco_previa = arco_por_qualidade(self.otima.valor) if self.otima.valor > 0 else self.mundo.arco
        comum.texto(tela, self.fonte_p, "Mochila 0/1 (otima):", cartao.left + 8,
                    cartao.top + 6, config.AMARELO)
        comum.texto(tela, self.fonte_p, self._resumo(self.otima),
                    cartao.left + 130, cartao.top + 6, config.BRANCO)
        pygame.draw.rect(tela, arco_previa.cor, (cartao.left + 8, cartao.top + 22, 8, 8))
        pygame.draw.rect(tela, config.PRETO, (cartao.left + 8, cartao.top + 22, 8, 8), 1)
        comum.texto(tela, self.fonte_p,
                    f"qualidade {self.otima.valor}  ->  {arco_previa.nome} (dano {arco_previa.dano})",
                    cartao.left + 22, cartao.top + 21, config.VERDE)
        comum.texto(tela, self.fonte_p,
                    f"gulosa daria: qualidade {self.gulosa.valor} (peso {self.gulosa.peso})",
                    cartao.left + 8, cartao.top + 34, config.CINZA)

        comum.texto(tela, self.fonte_p, self.mensagem, painel.centerx,
                    painel.bottom - 30, config.BRANCO, centro=True)
        comum.legenda_teclas(tela, self.fonte_p,
                             [("F", "forjar"), ("Q", "sair")],
                             painel.centerx, painel.bottom - 20)
