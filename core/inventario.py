# -*- coding: utf-8 -*-
"""
Estrutura de dados do inventario.

Requisito 2.2: guardar os itens coletaveis com operacoes de adicionar, remover e
consultar. Por dentro usamos um dicionario (chave do material -> [material, qtd]),
o que da O(1) pra essas tres operacoes. Como e so dado puro (nao depende de
pygame), da pra testar tudo no terminal.
"""


def _chave(material_ou_chave):
    """Aceita tanto o objeto Material quanto a string da chave."""
    return getattr(material_ou_chave, "chave", material_ou_chave)


class Inventario:
    def __init__(self):
        # chave -> [Material, quantidade]
        self._itens = {}

    # ---- operacoes principais (requisito 2.2) ----
    def adicionar(self, material, qtd=1):
        """Adiciona 'qtd' unidades de um material."""
        if qtd <= 0:
            return
        ch = _chave(material)
        if ch in self._itens:
            self._itens[ch][1] += qtd
        else:
            self._itens[ch] = [material, qtd]

    def remover(self, material, qtd=1):
        """Remove 'qtd' unidades. Devolve True se conseguiu, False se nao tinha."""
        ch = _chave(material)
        if ch not in self._itens or self._itens[ch][1] < qtd:
            return False
        self._itens[ch][1] -= qtd
        if self._itens[ch][1] <= 0:
            del self._itens[ch]
        return True

    def consultar(self, material):
        """Quantidade de um material especifico (0 se nao tiver)."""
        ch = _chave(material)
        if ch in self._itens:
            return self._itens[ch][1]
        return 0

    # alias com nome mais "de jogo"
    quantidade = consultar

    def tem(self, material, qtd=1):
        return self.consultar(material) >= qtd

    # ---- consultas auxiliares ----
    def total_unidades(self):
        return sum(par[1] for par in self._itens.values())

    def total_tipos(self):
        return len(self._itens)

    def vazio(self):
        return len(self._itens) == 0

    def listar(self):
        """Lista de tuplas (Material, quantidade)."""
        return [(par[0], par[1]) for par in self._itens.values()]

    def materiais(self):
        """So os objetos Material (um por tipo presente)."""
        return [par[0] for par in self._itens.values()]

    def expandir(self):
        """
        Devolve uma unidade por item (lista achatada).
        Usado pela mochila da ferraria, onde cada unidade pode entrar ou nao.
        """
        unidades = []
        for material, qtd in self._itens.values():
            unidades.extend([material] * qtd)
        return unidades

    def __len__(self):
        return self.total_tipos()

    def __iter__(self):
        return iter(self.listar())
