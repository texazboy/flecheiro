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

De quebra, o Jogo tambem aplica dois acabamentos globais: uma vinheta sutil
(escurece os cantos) e um fade rapido a cada troca de tela.
"""

import os

import pygame

import config
from core.recursos import Recursos
from core.mundo import Mundo
from core import som

DURACAO_FADE = 0.35


class Jogo:
    def __init__(self):
        pygame.mixer.pre_init(som.TAXA, -16, 1, 512)
        pygame.init()
        som.iniciar()
        pygame.display.set_caption(config.TITULO)
        self.janela = pygame.display.set_mode((config.LARGURA_JANELA, config.ALTURA_JANELA))
        self.tela = pygame.Surface((config.LARGURA, config.ALTURA))  # superficie interna
        self.clock = pygame.time.Clock()
        self.rodando = True

        pasta_assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        self.recursos = Recursos(pasta_assets)
        self.mundo = Mundo()

        self.vinheta = self._montar_vinheta()
        self._veu = pygame.Surface((config.LARGURA, config.ALTURA))
        self._veu.fill(config.PRETO)
        self.fade = 0.0

        from telas.menu import MenuState
        self.estado = MenuState(self)
        self.estado.entrar()

    # ------------------------------------------------- troca de estados
    def trocar_estado(self, novo_estado):
        self.estado.sair()
        self.estado = novo_estado
        self.estado.entrar()
        self.fade = DURACAO_FADE          # entra na tela nova vindo do escuro

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
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_m:
                    som.alternar_mudo()
                else:
                    self.estado.tratar_evento(evento)
            self.estado.atualizar(dt)
            if self.fade > 0:
                self.fade = max(0.0, self.fade - dt)
            self.estado.desenhar(self.tela)
            self._apresentar()
        pygame.quit()

    def _apresentar(self):
        self.tela.blit(self.vinheta, (0, 0))
        if self.fade > 0:
            self._veu.set_alpha(int(255 * self.fade / DURACAO_FADE))
            self.tela.blit(self._veu, (0, 0))
        pygame.transform.scale(self.tela, self.janela.get_size(), self.janela)
        pygame.display.flip()

    @staticmethod
    def _montar_vinheta():
        """Cantos levemente escuros. Gerada pequena e ampliada pra ficar macia."""
        pequena = pygame.Surface((96, 54), pygame.SRCALPHA)
        cx, cy = 48, 27
        for y in range(54):
            for x in range(96):
                dx = (x - cx) / cx
                dy = (y - cy) / cy
                d = (dx * dx + dy * dy) ** 0.5
                alfa = max(0, min(80, int((d - 0.72) * 230)))
                if alfa:
                    pequena.set_at((x, y), (0, 0, 0, alfa))
        return pygame.transform.smoothscale(pequena, (config.LARGURA, config.ALTURA))


def main():
    jogo = Jogo()
    jogo.rodar()


if __name__ == "__main__":
    main()
