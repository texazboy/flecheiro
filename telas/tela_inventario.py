# -*- coding: utf-8 -*-
"""
Sobreposicao do inventario (tecla I / Tab).

Mostra os itens em linhas com slot + icone, nome colorido pela raridade e
abas de ordenacao em cima (valor / peso / raridade). A ordenacao usa o
Quicksort implementado em algoritmos/ordenacao.py (o problema computacional
extra do projeto).
"""

import pygame

import config
from telas import comum
from algoritmos.ordenacao import quicksort

_RANK_RARIDADE = {"comum": 0, "incomum": 1, "raro": 2, "epico": 3, "lendario": 4}
_COR_RARIDADE = {
    "comum": (208, 208, 214),
    "incomum": (118, 205, 128),
    "raro": (178, 128, 235),
    "epico": (235, 150, 80),
    "lendario": (240, 205, 90),
}
_ABAS = [("valor", pygame.K_1), ("peso", pygame.K_2), ("raridade", pygame.K_3)]


class TelaInventario:
    def __init__(self, mundo, recursos):
        self.mundo = mundo
        self.recursos = recursos
        self.fonte = recursos.fonte(20)
        self.fonte_p = recursos.fonte(15)
        self.ordenar_por = "valor"
        self._nasceu = pygame.time.get_ticks()

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
        desloc = int((1.0 - comum.surgimento(self._nasceu)) * 14)
        painel = pygame.Rect(40, 22 + desloc, config.LARGURA - 80, config.ALTURA - 44)
        comum.painel(tela, painel)

        comum.faixa_titulo(tela, self.fonte, "INVENTARIO", painel.centerx, painel.top + 2)

        # abas de ordenacao (a ativa fica acesa, como tecla pressionada)
        ax = painel.centerx - 92
        for numero, (nome, _tecla) in enumerate(_ABAS, start=1):
            ativa = (nome == self.ordenar_por)
            r = comum.keycap(tela, self.fonte_p, str(numero), ax, painel.top + 28, ativa)
            comum.texto(tela, self.fonte_p, nome, r.right + 4, painel.top + 29,
                        config.BRANCO if ativa else config.CINZA)
            ax = r.right + 4 + self.fonte_p.size(nome)[0] + 12

        comum.separador(tela, painel.left + 10, painel.right - 10, painel.top + 46)

        pares = self.mundo.inventario.listar()
        pares = quicksort(pares, chave=self._chave_ordenacao(), decrescente=True)

        if not pares:
            comum.texto(tela, self.fonte_p, "(vazio - derrote inimigos pra coletar itens)",
                        painel.centerx, painel.centery, config.CINZA, centro=True)
        else:
            y = painel.top + 54
            peso_total = 0
            for i, (material, qtd) in enumerate(pares):
                linha = pygame.Rect(painel.left + 8, y - 2, painel.width - 16, 20)
                if i % 2 == 0:
                    s = pygame.Surface(linha.size, pygame.SRCALPHA)
                    s.fill((255, 255, 255, 10))
                    tela.blit(s, linha.topleft)

                # slot com o icone
                slot = pygame.Rect(linha.left + 2, y - 1, 18, 18)
                pygame.draw.rect(tela, (16, 18, 28), slot)
                pygame.draw.rect(tela, (60, 64, 84), slot, 1)
                sprite = self.recursos.sprite_item(material)
                tela.blit(sprite, (slot.centerx - sprite.get_width() // 2,
                                   slot.centery - sprite.get_height() // 2))

                cor_nome = _COR_RARIDADE.get(material.raridade, config.BRANCO)
                comum.texto(tela, self.fonte_p, material.nome, slot.right + 6, y + 2, cor_nome)
                comum.texto(tela, self.fonte_p, f"x{qtd}", slot.right + 70, y + 2, config.BRANCO)
                comum.texto(tela, self.fonte_p,
                            f"peso {material.peso}   valor {material.valor}",
                            painel.left + 160, y + 2, config.CINZA)
                comum.texto(tela, self.fonte_p, material.raridade,
                            painel.right - 14 - self.fonte_p.size(material.raridade)[0],
                            y + 2, cor_nome)
                peso_total += material.peso * qtd
                y += 21

            comum.separador(tela, painel.left + 10, painel.right - 10, painel.bottom - 26)
            comum.texto(tela, self.fonte_p, f"Peso total: {peso_total}",
                        painel.left + 14, painel.bottom - 19, config.VERDE)

        r = comum.keycap(tela, self.fonte_p, "I", painel.right - 64, painel.bottom - 21)
        comum.texto(tela, self.fonte_p, "fechar", r.right + 4, painel.bottom - 20, config.CINZA)
