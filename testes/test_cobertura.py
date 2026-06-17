# -*- coding: utf-8 -*-
"""Testes da cobertura de conjuntos (gulosa de Chvatal) e da cobertura maxima."""

import os
import sys
import random
import unittest
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algoritmos.cobertura import (
    cobertura_de_conjuntos,
    cobertura_maxima,
    planejar_cobertura,
)


def cobre_tudo(universo, subconjuntos, escolhidos):
    coberto = set()
    for i in escolhidos:
        coberto |= set(subconjuntos[i])
    return set(universo) <= coberto


def menor_cobertura_forca_bruta(universo, subconjuntos):
    """Menor numero de conjuntos que cobre o universo, testando combinacoes."""
    universo = set(universo)
    n = len(subconjuntos)
    for tamanho in range(0, n + 1):
        for combo in combinations(range(n), tamanho):
            if cobre_tudo(universo, subconjuntos, combo):
                return tamanho
    return n


class TestCoberturaMinima(unittest.TestCase):
    def test_cobre_o_universo(self):
        universo = {1, 2, 3, 4, 5}
        subconjuntos = [{1, 2, 3}, {2, 4}, {3, 4}, {4, 5}]
        res = cobertura_de_conjuntos(universo, subconjuntos)
        self.assertTrue(res.completa)
        self.assertTrue(cobre_tudo(universo, subconjuntos, res.escolhidos))

    def test_universo_vazio(self):
        res = cobertura_de_conjuntos(set(), [{1, 2}, {3}])
        self.assertEqual(res.escolhidos, [])
        self.assertTrue(res.completa)

    def test_impossivel_marca_incompleta(self):
        # ninguem cobre o elemento 3
        res = cobertura_de_conjuntos({1, 2, 3}, [{1}, {2}])
        self.assertFalse(res.completa)
        self.assertEqual(res.cobertos, {1, 2})

    def test_guloso_nunca_melhor_que_otimo(self):
        # a heuristica e valida e usa >= conjuntos que o otimo (nunca menos).
        random.seed(123)
        for _ in range(40):
            universo = set(range(1, random.randint(4, 9)))
            subconjuntos = []
            for _ in range(random.randint(3, 6)):
                tam = random.randint(1, len(universo))
                subconjuntos.append(set(random.sample(sorted(universo), tam)))
            # garante que o universo e coberto por todos juntos
            subconjuntos.append(set(universo))

            res = cobertura_de_conjuntos(universo, subconjuntos)
            self.assertTrue(res.completa)
            self.assertTrue(cobre_tudo(universo, subconjuntos, res.escolhidos))
            otimo = menor_cobertura_forca_bruta(universo, subconjuntos)
            self.assertGreaterEqual(len(res.escolhidos), otimo)


class TestCoberturaMaxima(unittest.TestCase):
    def test_orcamento_um_pega_o_maior(self):
        universo = {1, 2, 3, 4, 5}
        subconjuntos = [{1, 2, 3}, {4}, {5}]
        res = cobertura_maxima(universo, subconjuntos, k=1)
        self.assertEqual(res.cobertos, {1, 2, 3})
        self.assertEqual(len(res.escolhidos), 1)

    def test_orcamento_suficiente_cobre_tudo(self):
        universo = {1, 2, 3, 4, 5}
        subconjuntos = [{1, 2, 3}, {4}, {5}]
        res = cobertura_maxima(universo, subconjuntos, k=3)
        self.assertTrue(res.completa)


class TestPlanejarCobertura(unittest.TestCase):
    def test_rotulos(self):
        postos = {"A": {1, 2, 3}, "B": {2, 4}, "C": {3, 4}, "D": {4, 5}}
        escolhidos, completa = planejar_cobertura(postos)
        self.assertTrue(completa)
        coberto = set()
        for r in escolhidos:
            coberto |= postos[r]
        self.assertEqual(coberto, {1, 2, 3, 4, 5})


if __name__ == "__main__":
    unittest.main()
