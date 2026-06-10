# -*- coding: utf-8 -*-
"""
Ponto de entrada do jogo "Flecheiro".

Roda assim:
    python main.py

A classe Jogo cuida do loop principal, da janela e de uma coisa importante num
jogo de pixel art com camera: a conversao de coordenadas. A gente desenha tudo
numa superficie interna pequena (config.LARGURA x config.ALTURA) e so no final
amplia pra janela (x ESCALA). Por isso a posicao do mouse vinda do pygame (que
esta na escala da janela) precisa ser dividida pela ESCALA antes de virar
coordenada de mundo - quem faz isso e mouse_para_interno/mouse_interno.
"""

import os
import sys

import pygame

import config
from core.recursos import Recursos
from core.mundo import Mundo


class Jogo:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(config.TITULO)
        self.janela = pygame.display.set_mode((config.LARGURA_JANELA, config.ALTURA_JANELA))
        self.tela = pygame.Surface((config.LARGURA, config.ALTURA))  # superficie interna
        self.clock = pygame.time.Clock()
        self.rodando = True

        pasta_assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        self.recursos = Recursos(pasta_assets)
        self.mundo = Mundo()

        from telas.menu import MenuState
        self.estado = MenuState(self)
        self.estado.entrar()

    # ------------------------------------------------- troca de estados
    def trocar_estado(self, novo_estado):
        self.estado.sair()
        self.estado = novo_estado
        self.estado.entrar()

    # ------------------------------------------------- conversao de mouse
    def mouse_para_interno(self, pos_janela):
        return (pos_janela[0] // config.ESCALA, pos_janela[1] // config.ESCALA)

    def mouse_interno(self):
        return self.mouse_para_interno(pygame.mouse.get_pos())

    # ------------------------------------------------- loop principal
    def rodar(self):
        while self.rodando:
            dt = self.clock.tick(config.FPS) / 1000.0
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                else:
                    self.estado.tratar_evento(evento)
            self.estado.atualizar(dt)
            self.estado.desenhar(self.tela)
            self._apresentar()
        pygame.quit()

    def _apresentar(self):
        pygame.transform.scale(self.tela, self.janela.get_size(), self.janela)
        pygame.display.flip()


def main():
    jogo = Jogo()
    jogo.rodar()


if __name__ == "__main__":
    main()
