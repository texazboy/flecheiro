# -*- coding: utf-8 -*-
"""Testes do A*: confere o custo otimo contra BFS e os casos de borda."""

import os
import sys
import random
import unittest
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algoritmos.pathfinding import a_estrela, alcancavel


def bfs_custo(grade, inicio, objetivo):
    """Menor numero de passos por BFS (referencia: grade nao ponderada)."""
    if grade[inicio[0]][inicio[1]] == 1 or grade[objetivo[0]][objetivo[1]] == 1:
        return None
    fila = deque([(inicio, 0)])
    visto = {inicio}
    linhas, colunas = len(grade), len(grade[0])
    while fila:
        (l, c), d = fila.popleft()
        if (l, c) == objetivo:
            return d
        for dl, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nl, nc = l + dl, c + dc
            if 0 <= nl < linhas and 0 <= nc < colunas and grade[nl][nc] == 0 and (nl, nc) not in visto:
                visto.add((nl, nc))
                fila.append(((nl, nc), d + 1))
    return None


class TestAEstrela(unittest.TestCase):
    def test_grade_aberta_custo_manhattan(self):
        grade = [[0] * 5 for _ in range(5)]
        r = a_estrela(grade, (0, 0), (4, 4))
        self.assertEqual(r.custo, 8)               # 4 + 4 passos
        self.assertEqual(r.caminho[0], (0, 0))
        self.assertEqual(r.caminho[-1], (4, 4))
        self.assertEqual(len(r.caminho), r.custo + 1)

    def test_desvia_de_parede(self):
        grade = [
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 1, 0],
            [1, 1, 0, 1, 0],
            [0, 0, 0, 0, 0],
        ]
        r = a_estrela(grade, (0, 0), (4, 0))
        self.assertIsNotNone(r.caminho)
        self.assertEqual(r.custo, bfs_custo(grade, (0, 0), (4, 0)))

    def test_sem_caminho(self):
        grade = [
            [0, 1, 0],
            [1, 1, 0],
            [0, 1, 0],
        ]
        r = a_estrela(grade, (0, 0), (0, 2))
        self.assertIsNone(r.caminho)
        self.assertIsNone(r.custo)
        self.assertFalse(alcancavel(grade, (0, 0), (0, 2)))

    def test_inicio_igual_objetivo(self):
        grade = [[0, 0], [0, 0]]
        r = a_estrela(grade, (1, 1), (1, 1))
        self.assertEqual(r.custo, 0)
        self.assertEqual(r.caminho, [(1, 1)])

    def test_objetivo_em_parede(self):
        grade = [[0, 0], [0, 1]]
        r = a_estrela(grade, (0, 0), (1, 1))
        self.assertIsNone(r.caminho)

    def test_caminho_e_continuo_e_livre(self):
        grade = [
            [0, 0, 0, 0],
            [1, 1, 0, 1],
            [0, 0, 0, 0],
        ]
        r = a_estrela(grade, (0, 0), (2, 0))
        self.assertIsNotNone(r.caminho)
        # cada passo anda exatamente uma celula em 4 direcoes, sempre livre
        for (l, c) in r.caminho:
            self.assertEqual(grade[l][c], 0)
        for (a, b) in zip(r.caminho, r.caminho[1:]):
            self.assertEqual(abs(a[0] - b[0]) + abs(a[1] - b[1]), 1)

    def test_otimo_igual_bfs_em_grades_aleatorias(self):
        random.seed(2024)
        for _ in range(60):
            linhas = random.randint(3, 7)
            colunas = random.randint(3, 7)
            grade = [[1 if random.random() < 0.25 else 0 for _ in range(colunas)]
                     for _ in range(linhas)]
            inicio = (0, 0)
            objetivo = (linhas - 1, colunas - 1)
            grade[0][0] = 0
            grade[linhas - 1][colunas - 1] = 0

            r = a_estrela(grade, inicio, objetivo)
            esperado = bfs_custo(grade, inicio, objetivo)
            if esperado is None:
                self.assertIsNone(r.custo)
            else:
                self.assertEqual(r.custo, esperado)


if __name__ == "__main__":
    unittest.main()
