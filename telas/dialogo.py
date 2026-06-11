# -*- coding: utf-8 -*-
"""Caixa de dialogo dos NPCs. Avanca com E / Espaco / Enter."""

import pygame

import config
from core import som
from telas import comum


def quebrar_linhas(fonte, texto, largura_max):
    """Quebra um texto em varias linhas pra caber na largura do balao."""
    palavras = texto.split(" ")
    linhas = []
    atual = ""
    for p in palavras:
        teste = (atual + " " + p).strip()
        if fonte.size(teste)[0] <= largura_max:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


class Dialogo:
    def __init__(self, nome, falas, recursos):
        self.nome = nome
        self.falas = falas
        self.indice = 0
        self.fonte = recursos.fonte(18)
        self.fonte_nome = recursos.fonte(18)

    def tratar_evento(self, evento):
        """Retorna True quando o dialogo terminou."""
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
                som.tocar("clique")
                self.indice += 1
                if self.indice >= len(self.falas):
                    return True
            elif evento.key == pygame.K_ESCAPE:
                return True
        return False

    def desenhar(self, tela):
        caixa = pygame.Rect(20, config.ALTURA - 78, config.LARGURA - 40, 64)
        comum.painel(tela, caixa, cor_fundo=(24, 26, 40))

        comum.texto(tela, self.fonte_nome, self.nome, caixa.left + 8, caixa.top + 6,
                    config.AMARELO)

        fala = self.falas[min(self.indice, len(self.falas) - 1)]
        linhas = quebrar_linhas(self.fonte, fala, caixa.width - 20)
        y = caixa.top + 24
        for linha in linhas[:2]:
            comum.texto(tela, self.fonte, linha, caixa.left + 8, y, config.BRANCO)
            y += 16

        comum.texto(tela, self.fonte, "[E] continuar", caixa.right - 96,
                    caixa.bottom - 16, config.CINZA)
