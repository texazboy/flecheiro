# -*- coding: utf-8 -*-
"""
Camera do side-scroller.

So rola na horizontal (o classico de jogo de plataforma 2D). O ponto importante
e que TODA conversao entre coordenadas de mundo e de tela passa por aqui - assim
a gente nunca aplica o offset duas vezes por engano (aquele bug chato de
"conversao" de coordenada em jogo com camera).

  mundo  -> tela : subtrai o offset      (aplicar / aplicar_ponto)
  tela   -> mundo : soma o offset         (tela_para_mundo)
"""


import random


class Camera:
    def __init__(self, largura_tela, altura_tela, largura_mundo):
        self.largura_tela = largura_tela
        self.altura_tela = altura_tela
        self.largura_mundo = largura_mundo
        self.offset_x = 0
        # "tremor" da camera (screen shake) nos impactos
        self._tremor = 0.0
        self._sx = 0
        self._sy = 0

    def seguir(self, alvo_rect):
        """Centraliza o alvo na horizontal, sem deixar aparecer fora do mundo."""
        desejado = alvo_rect.centerx - self.largura_tela // 2
        limite = max(0, self.largura_mundo - self.largura_tela)
        self.offset_x = max(0, min(desejado, limite))

    def sacudir(self, intensidade):
        self._tremor = max(self._tremor, float(intensidade))

    def atualizar(self, dt):
        if self._tremor > 0.2:
            self._tremor = max(0.0, self._tremor - 28 * dt)
            self._sx = random.randint(-int(self._tremor), int(self._tremor))
            self._sy = random.randint(-int(self._tremor), int(self._tremor))
        else:
            self._tremor = 0.0
            self._sx = self._sy = 0

    def aplicar(self, rect):
        """Rect do mundo -> Rect na tela."""
        return rect.move(-self.offset_x + self._sx, self._sy)

    def aplicar_ponto(self, ponto):
        """(x, y) do mundo -> (x, y) na tela."""
        return (ponto[0] - self.offset_x + self._sx, ponto[1] + self._sy)

    def tela_para_mundo(self, ponto):
        """
        (x, y) da tela (ja na resolucao interna) -> (x, y) no mundo.
        De proposito NAO inclui o tremor: o tremor e so visual, a mira do mouse
        nao pode ficar tremendo junto.
        """
        return (ponto[0] + self.offset_x, ponto[1])
