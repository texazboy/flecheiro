# -*- coding: utf-8 -*-
"""
Caixa de dialogo dos NPCs, com retrato e efeito maquina-de-escrever.

O texto vai aparecendo letra por letra; apertar E no meio revela a fala
inteira de uma vez, e apertar E com a fala completa passa pra proxima
(o padrao classico dos RPGs). Quando a fala termina de digitar, uma setinha
pulsa no canto avisando que pode continuar.
"""

import math

import pygame

import config
from core import som
from telas import comum

VELOCIDADE = 0.045   # caracteres por milissegundo (= 45 por segundo)


def quebrar_linhas(fonte, texto_fala, largura_max):
    """Quebra um texto em varias linhas pra caber na largura do balao."""
    palavras = texto_fala.split(" ")
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
    def __init__(self, nome, falas, recursos, retrato=None):
        self.nome = nome
        self.falas = falas
        self.indice = 0
        self.retrato = retrato            # sprite do NPC (opcional)
        self.fonte = recursos.fonte(18)
        self.fonte_nome = recursos.fonte(17)
        self._nasceu = pygame.time.get_ticks()
        self._inicio_fala = pygame.time.get_ticks()

    def _fala_atual(self):
        return self.falas[min(self.indice, len(self.falas) - 1)]

    def _visiveis(self):
        """Quantos caracteres da fala atual ja apareceram."""
        decorrido = pygame.time.get_ticks() - self._inicio_fala
        return int(decorrido * VELOCIDADE)

    def tratar_evento(self, evento):
        """Retorna True quando o dialogo terminou."""
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
                som.tocar("clique")
                if self._visiveis() < len(self._fala_atual()):
                    # ainda digitando: primeiro aperto revela a fala inteira
                    self._inicio_fala = -10 ** 9
                else:
                    self.indice += 1
                    self._inicio_fala = pygame.time.get_ticks()
                    if self.indice >= len(self.falas):
                        return True
            elif evento.key == pygame.K_ESCAPE:
                return True
        return False

    def desenhar(self, tela):
        desloc = int((1.0 - comum.surgimento(self._nasceu)) * 12)
        caixa = pygame.Rect(20, config.ALTURA - 80 + desloc, config.LARGURA - 40, 68)
        comum.painel(tela, caixa, cor_fundo=(26, 28, 42))

        # retrato do NPC numa molduria a esquerda
        margem_texto = caixa.left + 10
        if self.retrato is not None:
            moldura = pygame.Rect(caixa.left + 8, caixa.top + 10, 34, 40)
            pygame.draw.rect(tela, (16, 18, 28), moldura)
            r = self.retrato.get_rect(midbottom=(moldura.centerx, moldura.bottom - 3))
            tela.blit(self.retrato, r)
            pygame.draw.rect(tela, (70, 74, 96), moldura, 1)
            margem_texto = moldura.right + 10

        # nome numa plaquinha em cima da caixa
        larg_nome = self.fonte_nome.size(self.nome)[0]
        placa = pygame.Rect(caixa.left + 6, caixa.top - 9, larg_nome + 14, 16)
        comum.painel(tela, placa, cor_fundo=(52, 44, 28), alpha=255)
        comum.texto(tela, self.fonte_nome, self.nome, placa.centerx, placa.centery,
                    config.AMARELO, centro=True)

        # fala com efeito de digitacao
        fala = self._fala_atual()
        visiveis = min(len(fala), self._visiveis())
        parcial = fala[:visiveis]
        largura_util = caixa.right - 12 - margem_texto
        y = caixa.top + 16
        for linha in quebrar_linhas(self.fonte, parcial, largura_util)[:3]:
            comum.texto(tela, self.fonte, linha, margem_texto, y, config.BRANCO)
            y += 15

        # quando a fala completou, a setinha pulsa convidando a continuar
        if visiveis >= len(fala):
            salto = int((math.sin(pygame.time.get_ticks() * 0.008) + 1) * 1.5)
            px = caixa.right - 16
            py = caixa.bottom - 12 + salto
            pygame.draw.polygon(tela, config.AMARELO,
                                [(px - 4, py), (px + 4, py), (px, py + 5)])
        # progresso das falas (bolinhas no rodape)
        for i in range(len(self.falas)):
            cor = config.AMARELO if i <= self.indice else (70, 74, 96)
            pygame.draw.circle(tela, cor, (caixa.left + 14 + i * 8, caixa.bottom - 8), 2)
