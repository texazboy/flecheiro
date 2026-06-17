# -*- coding: utf-8 -*-
"""Testes do fluxo maximo (Edmonds-Karp) e da rede da economia da vila."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algoritmos.fluxo import fluxo_maximo, rede_economia_vila


class TestFluxoMaximo(unittest.TestCase):
    def test_exemplo_classico_clrs(self):
        # Grafo classico do CLRS (fig. 26.1): o fluxo maximo conhecido e 23.
        arestas = [
            (0, 1, 16), (0, 2, 13),
            (1, 2, 10), (2, 1, 4),
            (1, 3, 12), (3, 2, 9),
            (2, 4, 14), (4, 3, 7),
            (3, 5, 20), (4, 5, 4),
        ]
        resultado = fluxo_maximo(6, arestas, fonte=0, sumidouro=5)
        self.assertEqual(resultado.valor, 23)

    def test_caminho_em_serie_limita_pelo_menor(self):
        # 0 -> 1 (5) -> 2 (3): o gargalo manda, fluxo = 3.
        resultado = fluxo_maximo(3, [(0, 1, 5), (1, 2, 3)], fonte=0, sumidouro=2)
        self.assertEqual(resultado.valor, 3)

    def test_arestas_paralelas_somam(self):
        # duas arestas 0->1 (3 e 2) viram capacidade 5; depois 1->2 (10).
        arestas = [(0, 1, 3), (0, 1, 2), (1, 2, 10)]
        resultado = fluxo_maximo(3, arestas, fonte=0, sumidouro=2)
        self.assertEqual(resultado.valor, 5)

    def test_sem_caminho_da_zero(self):
        # sumidouro isolado: nao da pra mandar nada.
        resultado = fluxo_maximo(3, [(0, 1, 7)], fonte=0, sumidouro=2)
        self.assertEqual(resultado.valor, 0)

    def test_fonte_igual_sumidouro(self):
        resultado = fluxo_maximo(2, [(0, 1, 4)], fonte=0, sumidouro=0)
        self.assertEqual(resultado.valor, 0)

    def test_conservacao_de_fluxo(self):
        # o que sai da fonte tem que ser o valor; e todo no intermediario
        # precisa ter entrada igual a saida (lei de conservacao).
        arestas = [
            (0, 1, 16), (0, 2, 13),
            (1, 2, 10), (2, 1, 4),
            (1, 3, 12), (3, 2, 9),
            (2, 4, 14), (4, 3, 7),
            (3, 5, 20), (4, 5, 4),
        ]
        n, fonte, sumidouro = 6, 0, 5
        resultado = fluxo_maximo(n, arestas, fonte, sumidouro)
        fluxo = resultado.fluxo

        saida_fonte = sum(max(0, fluxo[fonte][v]) for v in range(n))
        self.assertEqual(saida_fonte, resultado.valor)

        for u in range(n):
            if u in (fonte, sumidouro):
                continue
            entra = sum(max(0, fluxo[v][u]) for v in range(n))
            sai = sum(max(0, fluxo[u][v]) for v in range(n))
            self.assertEqual(entra, sai, msg=f"no {u} nao conserva fluxo")


class TestRedeEconomiaVila(unittest.TestCase):
    def test_gargalo_nos_destinos(self):
        # estoque farto; o limite e a soma das capacidades dos destinos (6 + 5).
        rede = rede_economia_vila(
            estoque={"madeira": 20, "ferro": 20, "couro": 20},
            cap_ferraria=6, cap_loja=5,
        )
        self.assertEqual(rede.resultado.valor, 11)

    def test_gargalo_no_estoque(self):
        # destinos enormes; agora o limite e o estoque total (3 + 2 + 1).
        rede = rede_economia_vila(
            estoque={"madeira": 3, "ferro": 2, "couro": 1},
            cap_ferraria=100, cap_loja=100,
        )
        self.assertEqual(rede.resultado.valor, 6)

    def test_estoque_vazio(self):
        rede = rede_economia_vila(estoque={}, cap_ferraria=10, cap_loja=10)
        self.assertEqual(rede.resultado.valor, 0)


if __name__ == "__main__":
    unittest.main()
