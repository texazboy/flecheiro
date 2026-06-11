# -*- coding: utf-8 -*-
"""
Iluminacao 2D simples, do jeito classico de jogo de pixel art:

  1. desenhamos o mundo normalmente;
  2. montamos um "mapa de luz": uma superficie preenchida com a cor ambiente
     (escura, azulada de noite) onde cada fonte de luz SOMA um circulo com
     decaimento suave;
  3. multiplicamos o mapa por cima da tela (BLEND_MULT): onde nao ha luz o
     mundo escurece pro tom ambiente, onde ha luz ele volta a aparecer.

De dia nao tem mapa nenhum (ambiente None = nem escurece), entao o custo some.
As texturas de luz sao gigantes de gerar por pixel, por isso ficam em cache -
cada (raio, cor) e calculada uma unica vez.
"""

import pygame

import config

# cor ambiente por tema; None = claridade total (sem mapa de luz)
AMBIENTE = {
    "dia": None,
    "poente": (228, 206, 212),
    "noite": (122, 132, 180),
}

_cache_textura = {}


def _textura(raio, cor):
    chave = (raio, cor)
    tex = _cache_textura.get(chave)
    if tex is None:
        tam = raio * 2
        tex = pygame.Surface((tam, tam))
        for y in range(tam):
            for x in range(tam):
                dx = x - raio
                dy = y - raio
                d2 = dx * dx + dy * dy
                if d2 >= raio * raio:
                    continue
                forca = (1.0 - (d2 ** 0.5) / raio) ** 2
                tex.set_at((x, y), (int(cor[0] * forca), int(cor[1] * forca),
                                    int(cor[2] * forca)))
        _cache_textura[chave] = tex
    return tex


class Luzes:
    """Junta os pedidos de luz do frame e aplica tudo de uma vez."""

    def __init__(self, ambiente):
        self.ambiente = ambiente
        self._mapa = pygame.Surface((config.LARGURA, config.ALTURA)) if ambiente else None
        self._pedidos = []

    @property
    def ativa(self):
        return self.ambiente is not None

    def adicionar(self, x, y, raio, cor=(255, 228, 170)):
        """Pede uma luz em coordenadas de MUNDO para este frame.
        O raio e arredondado de 4 em 4 px pra luz tremulante (tocha) reusar as
        mesmas texturas do cache em vez de gerar uma nova a cada frame."""
        if self.ambiente is not None:
            raio = max(8, int(raio) // 4 * 4)
            self._pedidos.append((x, y, raio, cor))

    def aplicar(self, tela, camera):
        """Escurece a cena e abre as pocas de luz. Chamar depois das entidades
        e antes da HUD (a interface nao deve escurecer)."""
        if self.ambiente is None:
            self._pedidos.clear()
            return
        mapa = self._mapa
        mapa.fill(self.ambiente)
        for x, y, raio, cor in self._pedidos:
            px, py = camera.aplicar_ponto((x, y))
            if px < -raio or px > config.LARGURA + raio:
                continue
            if py < -raio or py > config.ALTURA + raio:
                continue
            mapa.blit(_textura(raio, cor), (int(px) - raio, int(py) - raio),
                      special_flags=pygame.BLEND_RGB_ADD)
        tela.blit(mapa, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        self._pedidos.clear()
