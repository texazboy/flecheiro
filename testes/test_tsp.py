# -*- coding: utf-8 -*-
"""Testes do TSP: confere o Held-Karp contra forca bruta e valida a heuristica."""

import os
import sys
import math
import random
import unittest
from itertools import permutations

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algoritmos.tsp import resolver_tsp, custo_rota, distancia


def forca_bruta(pontos):
    """Menor ciclo testando TODAS as ordens (so serve pra n pequeno)."""
    n = len(pontos)
    melhor = float("inf")
    for resto in permutations(range(1, n)):
        ordem = [0] + list(resto)
        melhor = min(melhor, custo_rota(ordem, pontos))
    return melhor


def eh_permutacao_valida(ordem, n):
    return sorted(ordem) == list(range(n)) and ordem[0] == 0


class TestTSP(unittest.TestCase):
    def test_held_karp_bate_com_forca_bruta(self):
        random.seed(42)
        for n in range(4, 9):
            pontos = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(n)]
            resultado = resolver_tsp(pontos)
            otimo = forca_bruta(pontos)
            self.assertTrue(resultado.metodo.startswith("exato") or resultado.metodo == "trivial")
            self.assertAlmostEqual(resultado.custo, otimo, places=6,
                                   msg=f"falhou para n={n}")

    def test_ordem_eh_permutacao(self):
        random.seed(7)
        pontos = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(10)]
        resultado = resolver_tsp(pontos)
        self.assertTrue(eh_permutacao_valida(resultado.ordem, len(pontos)))

    def test_heuristica_acima_do_limite(self):
        random.seed(1)
        pontos = [(random.uniform(0, 200), random.uniform(0, 200)) for _ in range(25)]
        resultado = resolver_tsp(pontos)
        self.assertEqual(resultado.metodo, "heuristica (2-opt)")
        self.assertTrue(eh_permutacao_valida(resultado.ordem, len(pontos)))

    def test_quadrado_perfeito(self):
        # 4 cantos de um quadrado 10x10: o ciclo otimo e o perimetro = 40.
        pontos = [(0, 0), (10, 0), (10, 10), (0, 10)]
        resultado = resolver_tsp(pontos)
        self.assertAlmostEqual(resultado.custo, 40.0, places=6)

    def test_dois_opt_nao_piora(self):
        # A heuristica nunca pode dar um custo melhor que o otimo exato.
        random.seed(99)
        for _ in range(5):
            pontos = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(12)]
            otimo = resolver_tsp(pontos, limite_exato=15).custo
            heur = resolver_tsp(pontos, limite_exato=0).custo
            self.assertGreaterEqual(heur + 1e-6, otimo)


if __name__ == "__main__":
    unittest.main()
