# -*- coding: utf-8 -*-
"""Testes da mochila 0/1 (ferraria)."""

import os
import sys
import random
import unittest
from collections import namedtuple
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algoritmos.mochila import mochila_dp, mochila_gulosa, resolver_mochila

Item = namedtuple("Item", ["nome", "peso", "valor"])


def otimo_forca_bruta(itens, capacidade):
    melhor = 0
    for r in range(len(itens) + 1):
        for combo in combinations(itens, r):
            peso = sum(i.peso for i in combo)
            if peso <= capacidade:
                melhor = max(melhor, sum(i.valor for i in combo))
    return melhor


class TestMochila(unittest.TestCase):
    def test_caso_classico(self):
        itens = [Item("a", 1, 1), Item("b", 3, 4), Item("c", 4, 5), Item("d", 5, 7)]
        resultado = mochila_dp(itens, 7)
        self.assertEqual(resultado.valor, 9)  # itens b + c (peso 7, valor 9)
        self.assertLessEqual(resultado.peso, 7)

    def test_dp_bate_forca_bruta(self):
        random.seed(123)
        for _ in range(30):
            n = random.randint(1, 9)
            itens = [Item(f"i{j}", random.randint(1, 6), random.randint(1, 10)) for j in range(n)]
            cap = random.randint(0, 15)
            self.assertEqual(mochila_dp(itens, cap).valor, otimo_forca_bruta(itens, cap))

    def test_respeita_capacidade(self):
        random.seed(5)
        itens = [Item(f"i{j}", random.randint(1, 5), random.randint(1, 9)) for j in range(8)]
        r = mochila_dp(itens, 10)
        self.assertLessEqual(r.peso, 10)
        self.assertEqual(r.peso, sum(i.peso for i in r.selecionados))
        self.assertEqual(r.valor, sum(i.valor for i in r.selecionados))

    def test_dp_nunca_pior_que_gulosa(self):
        random.seed(77)
        for _ in range(40):
            itens = [Item(f"i{j}", random.randint(1, 6), random.randint(1, 12)) for j in range(7)]
            cap = random.randint(1, 14)
            self.assertGreaterEqual(mochila_dp(itens, cap).valor, mochila_gulosa(itens, cap).valor)

    def test_gulosa_pode_errar(self):
        # caso onde o guloso (por razao) NAO acha o otimo
        itens = [Item("razao_alta", 1, 2), Item("pesado_bom", 3, 5), Item("medio", 3, 5)]
        # capacidade 6: otimo = pesado_bom + medio = 10
        self.assertEqual(mochila_dp(itens, 6).valor, 10)
        self.assertEqual(resolver_mochila(itens, 6).valor, 10)


if __name__ == "__main__":
    unittest.main()
