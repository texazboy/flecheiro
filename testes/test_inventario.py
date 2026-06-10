# -*- coding: utf-8 -*-
"""Testes da estrutura de dados do inventario e da ordenacao."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.inventario import Inventario
from entidades.item import MATERIAIS
from algoritmos.ordenacao import quicksort, ordenar_itens


class TestInventario(unittest.TestCase):
    def setUp(self):
        self.inv = Inventario()
        self.madeira = MATERIAIS["madeira"]
        self.ferro = MATERIAIS["ferro"]

    def test_adicionar_e_consultar(self):
        self.inv.adicionar(self.madeira, 3)
        self.assertEqual(self.inv.consultar(self.madeira), 3)
        self.inv.adicionar(self.madeira, 2)
        self.assertEqual(self.inv.consultar("madeira"), 5)

    def test_remover(self):
        self.inv.adicionar(self.ferro, 2)
        self.assertTrue(self.inv.remover(self.ferro, 1))
        self.assertEqual(self.inv.consultar(self.ferro), 1)
        self.assertFalse(self.inv.remover(self.ferro, 5))  # nao tem o suficiente
        self.assertTrue(self.inv.remover(self.ferro, 1))
        self.assertEqual(self.inv.consultar(self.ferro), 0)
        self.assertTrue(self.inv.vazio())

    def test_tem_e_totais(self):
        self.inv.adicionar(self.madeira, 4)
        self.inv.adicionar(self.ferro, 1)
        self.assertTrue(self.inv.tem(self.madeira, 4))
        self.assertFalse(self.inv.tem(self.madeira, 5))
        self.assertEqual(self.inv.total_unidades(), 5)
        self.assertEqual(self.inv.total_tipos(), 2)

    def test_expandir_para_mochila(self):
        self.inv.adicionar(self.madeira, 2)
        self.inv.adicionar(self.ferro, 1)
        unidades = self.inv.expandir()
        self.assertEqual(len(unidades), 3)
        self.assertEqual(sum(1 for u in unidades if u.chave == "madeira"), 2)


class TestOrdenacao(unittest.TestCase):
    def test_quicksort_igual_ao_sorted(self):
        import random
        random.seed(3)
        for _ in range(20):
            dados = [random.randint(0, 50) for _ in range(random.randint(0, 30))]
            self.assertEqual(quicksort(dados), sorted(dados))

    def test_quicksort_decrescente(self):
        self.assertEqual(quicksort([3, 1, 2], decrescente=True), [3, 2, 1])

    def test_ordenar_itens_por_valor(self):
        itens = [MATERIAIS["pena"], MATERIAIS["cristal"], MATERIAIS["madeira"]]
        ordenados = ordenar_itens(itens, por="valor")
        valores = [it.valor for it in ordenados]
        self.assertEqual(valores, sorted(valores, reverse=True))
        self.assertEqual(ordenados[0].chave, "cristal")  # maior valor


if __name__ == "__main__":
    unittest.main()
