# -*- coding: utf-8 -*-
"""Testes da camera: foco com limite de mundo e conversao de coordenadas."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.camera import Camera


class _Alvo:
    """Stub com so o que a camera usa do rect do alvo."""

    def __init__(self, centerx):
        self.centerx = centerx


class TestCamera(unittest.TestCase):
    def setUp(self):
        # tela 480 de largura, mundo de 2000 -> da pra rolar bastante
        self.cam = Camera(largura_tela=480, altura_tela=270, largura_mundo=2000)

    def test_segue_centralizando(self):
        self.cam.seguir(_Alvo(centerx=1000))
        self.assertEqual(self.cam.offset_x, 1000 - 240)

    def test_nao_passa_da_borda_esquerda(self):
        self.cam.seguir(_Alvo(centerx=10))
        self.assertEqual(self.cam.offset_x, 0)

    def test_nao_passa_da_borda_direita(self):
        self.cam.seguir(_Alvo(centerx=1999))
        self.assertEqual(self.cam.offset_x, 2000 - 480)

    def test_mundo_menor_que_tela_nao_rola(self):
        cam = Camera(480, 270, largura_mundo=300)
        cam.seguir(_Alvo(centerx=150))
        self.assertEqual(cam.offset_x, 0)

    def test_conversao_ida_e_volta(self):
        self.cam.seguir(_Alvo(centerx=1000))
        ponto_mundo = (1234, 88)
        na_tela = self.cam.aplicar_ponto(ponto_mundo)
        de_volta = self.cam.tela_para_mundo(na_tela)
        self.assertEqual(de_volta, ponto_mundo)

    def test_aplicar_ponto_subtrai_offset(self):
        self.cam.seguir(_Alvo(centerx=1000))   # offset_x = 760
        self.assertEqual(self.cam.aplicar_ponto((760, 50)), (0, 50))

    def test_origem_sem_tremor(self):
        self.cam.seguir(_Alvo(centerx=1000))
        self.assertEqual(self.cam.origem(), (-760, 0))


if __name__ == "__main__":
    unittest.main()
