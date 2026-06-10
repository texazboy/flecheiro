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
from telas import comum
from algoritmos.mochila import resolver_mochila, mochila_gulosa
from core.mundo import arco_por_qualidade

CAPACIDADE_BIGORNA = 10


class Ferraria:
    def __init__(self, mundo, recursos):
        self.mundo = mundo
        self.recursos = recursos
        self.fonte = recursos.fonte(18)
        self.fonte_p = recursos.fonte(15)
        self.capacidade = CAPACIDADE_BIGORNA
        self.mensagem = "Escolha [F] para forjar com a selecao otima."
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
            return
        # consome os materiais escolhidos pela mochila
        contagem = Counter(m.chave for m in self.otima.selecionados)
        for chave, qtd in contagem.items():
            self.mundo.inventario.remover(chave, qtd)

        arco = arco_por_qualidade(self.otima.valor)
        self.mundo.arco = arco
        self.mundo.arcos_forjados += 1
        self.mensagem = f"Forjou: {arco.nome} (dano {arco.dano})!"
        self._recalcular()

    def _resumo(self, resultado):
        contagem = Counter(m.nome for m in resultado.selecionados)
        if not contagem:
            return "nada"
        return ", ".join(f"{nome} x{qtd}" for nome, qtd in contagem.items())

    def desenhar(self, tela):
        comum.escurecer(tela, 175)
        painel = pygame.Rect(24, 14, config.LARGURA - 48, config.ALTURA - 26)
        comum.painel(tela, painel, cor_fundo=(40, 30, 26))

        comum.texto(tela, self.fonte, "FERRARIA", painel.centerx, painel.top + 12,
                    config.LARANJA, centro=True)
        comum.texto(tela, self.fonte_p, f"Capacidade da bigorna: {self.capacidade} de peso",
                    painel.centerx, painel.top + 28, config.CINZA, centro=True)

        y = painel.top + 46
        comum.texto(tela, self.fonte_p, "Materiais disponiveis:", painel.left + 12, y, config.BRANCO)
        y += 16
        if self.mundo.inventario.vazio():
            comum.texto(tela, self.fonte_p, "  (nenhum)", painel.left + 12, y, config.CINZA)
            y += 16
        else:
            for material, qtd in self.mundo.inventario.listar():
                comum.texto(tela, self.fonte_p,
                            f"  {material.nome} x{qtd}  (peso {material.peso}, valor {material.valor})",
                            painel.left + 12, y, config.BRANCO)
                y += 15

        y += 6
        arco_previa = arco_por_qualidade(self.otima.valor) if self.otima.valor > 0 else self.mundo.arco
        comum.texto(tela, self.fonte_p, "Mochila 0/1 (otima):", painel.left + 12, y, config.AMARELO)
        y += 15
        comum.texto(tela, self.fonte_p,
                    f"  usa: {self._resumo(self.otima)}", painel.left + 12, y, config.BRANCO)
        y += 15
        comum.texto(tela, self.fonte_p,
                    f"  peso {self.otima.peso}/{self.capacidade}  qualidade {self.otima.valor}  ->  {arco_previa.nome}",
                    painel.left + 12, y, config.VERDE)
        y += 18
        comum.texto(tela, self.fonte_p,
                    f"Comparacao gulosa: qualidade {self.gulosa.valor} (peso {self.gulosa.peso})",
                    painel.left + 12, y, config.CINZA)

        y += 20
        comum.texto(tela, self.fonte_p, self.mensagem, painel.centerx, y,
                    config.BRANCO, centro=True)
        comum.texto(tela, self.fonte_p, "[F] forjar    [Q] sair", painel.centerx,
                    painel.bottom - 14, config.CINZA, centro=True)
