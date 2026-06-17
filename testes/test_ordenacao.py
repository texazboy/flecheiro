# -*- coding: utf-8 -*-
"""Testes do Quicksort e da ordenacao do inventario."""

import os
import sys
import random
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algoritmos.ordenacao import quicksort, ordenar_itens


class _Item:
    """Item simplificado do inventario, so com o que a ordenacao olha."""

    def __init__(self, nome, valor, peso, raridade="comum"):
        self.nome = nome
        self.valor = valor
        self.peso = peso
        self.raridade = raridade

    def __repr__(self):
        return self.nome


class TestQuicksort(unittest.TestCase):
    def test_bate_com_sorted(self):
        random.seed(10)
        for _ in range(50):
            lista = [random.randint(-50, 50) for _ in range(random.randint(0, 30))]
            self.assertEqual(quicksort(lista), sorted(lista))

    def test_decrescente(self):
        lista = [3, 1, 4, 1, 5, 9, 2, 6]
        self.assertEqual(quicksort(lista, decrescente=True), sorted(lista, reverse=True))

    def test_nao_altera_a_lista_original(self):
        original = [5, 2, 8, 1]
        copia = list(original)
        quicksort(original)
        self.assertEqual(original, copia)

    def test_chave_personalizada(self):
        palavras = ["bbb", "a", "cc"]
        self.assertEqual(quicksort(palavras, chave=len), ["a", "cc", "bbb"])

    def test_lista_vazia_e_unitaria(self):
        self.assertEqual(quicksort([]), [])
        self.assertEqual(quicksort([42]), [42])


class TestOrdenarItens(unittest.TestCase):
    def setUp(self):
        self.itens = [
            _Item("madeira", valor=2, peso=1, raridade="comum"),
            _Item("cristal", valor=12, peso=2, raridade="lendario"),
            _Item("ferro", valor=6, peso=3, raridade="raro"),
        ]

    def test_por_valor_decrescente(self):
        nomes = [it.nome for it in ordenar_itens(self.itens, por="valor")]
        self.assertEqual(nomes, ["cristal", "ferro", "madeira"])

    def test_por_peso_decrescente(self):
        nomes = [it.nome for it in ordenar_itens(self.itens, por="peso")]
        self.assertEqual(nomes, ["ferro", "cristal", "madeira"])

    def test_por_raridade_decrescente(self):
        nomes = [it.nome for it in ordenar_itens(self.itens, por="raridade")]
        self.assertEqual(nomes, ["cristal", "ferro", "madeira"])


if __name__ == "__main__":
    unittest.main()
