# -*- coding: utf-8 -*-
"""
Smoke test do jogo: roda tudo sem abrir janela (driver de video "dummy") pra
garantir que nenhuma tela quebra em tempo de execucao. Nao testa jogabilidade
fina (isso e no olho), so que update/desenho de cada estado nao estoura erro.

Uso:  python testes/smoke_jogo.py
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from main import Jogo  # noqa: E402
from fases.fase import Fase  # noqa: E402
from fases.vila import Vila  # noqa: E402
from telas.menu import VitoriaState, GameOverState  # noqa: E402


def tecla(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k, mod=0, unicode="", scancode=0)


def clique(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)


def rodar_frames(jogo, n):
    for _ in range(n):
        jogo.estado.atualizar(1 / 60)
        jogo.estado.desenhar(jogo.tela)


def main():
    jogo = Jogo()

    # --- menu ---
    jogo.estado.desenhar(jogo.tela)
    jogo.estado.tratar_evento(tecla(pygame.K_RETURN))
    assert isinstance(jogo.estado, Fase), "Enter no menu deveria iniciar a fase 1"
    fase = jogo.estado

    # --- fase 1: atira, abre overlays, coleta, mostra rota ---
    for i in range(6):
        fase.tratar_evento(clique((200 + i * 20, 80 + i * 10)))
    fase.tratar_evento(tecla(pygame.K_t))   # liga rota do TSP
    fase.tratar_evento(tecla(pygame.K_i))   # abre inventario
    fase.tratar_evento(tecla(pygame.K_i))   # fecha
    fase.tratar_evento(tecla(pygame.K_e))   # coleta proximos
    fase.tratar_evento(tecla(pygame.K_SPACE))
    rodar_frames(jogo, 180)

    # forca a chegada na porta pra testar a transicao fase -> vila
    jogo.estado.jogador.rect.topleft = jogo.estado.porta.topleft
    jogo.estado.atualizar(1 / 60)
    assert isinstance(jogo.estado, Vila), "porta da fase 1 deveria levar a vila"
    vila = jogo.estado
    vila.desenhar(jogo.tela)

    # --- vila: ferreiro -> dialogo -> ferraria -> forja ---
    vila.jogador.rect.centerx = 200
    vila.tratar_evento(tecla(pygame.K_e))                 # abre dialogo
    for _ in range(4):
        vila.tratar_evento(tecla(pygame.K_e))             # passa o dialogo -> ferraria
    vila.desenhar(jogo.tela)
    vila.tratar_evento(tecla(pygame.K_f))                 # forja (mochila)
    vila.desenhar(jogo.tela)
    vila.tratar_evento(tecla(pygame.K_q))                 # sai da ferraria

    # --- vila: lojista -> dialogo -> loja -> vende/compra ---
    vila.jogador.rect.centerx = 430
    vila.tratar_evento(tecla(pygame.K_e))
    for _ in range(4):
        vila.tratar_evento(tecla(pygame.K_e))             # -> loja
    vila.desenhar(jogo.tela)
    vila.tratar_evento(tecla(pygame.K_RETURN))            # vende
    vila.tratar_evento(tecla(pygame.K_c))                 # compra cura
    vila.tratar_evento(tecla(pygame.K_q))

    # --- vila: aldeao (so dialogo) ---
    vila.jogador.rect.centerx = 640
    vila.tratar_evento(tecla(pygame.K_e))     # abre
    for _ in range(3):
        vila.tratar_evento(tecla(pygame.K_e))  # passa as 3 falas e fecha
    vila.desenhar(jogo.tela)
    assert vila.overlay is None, "dialogo do aldeao deveria ter fechado"

    # --- vila -> fase 2 pela porta ---
    vila.jogador.rect.x = vila.porta.x
    vila.tratar_evento(tecla(pygame.K_e))
    assert isinstance(jogo.estado, Fase) and jogo.estado.numero == 2, "porta da vila -> fase 2"
    fase2 = jogo.estado
    for i in range(8):
        fase2.tratar_evento(clique((150 + i * 15, 120)))
    fase2.tratar_evento(tecla(pygame.K_t))
    rodar_frames(jogo, 120)

    # --- fase 2 -> vitoria ---
    jogo.estado.jogador.rect.topleft = jogo.estado.porta.topleft
    jogo.estado.atualizar(1 / 60)
    assert isinstance(jogo.estado, VitoriaState), "porta da fase 2 -> vitoria"
    jogo.estado.desenhar(jogo.tela)

    # --- desenha o game over so pra garantir que nao quebra ---
    GameOverState(jogo, 1).desenhar(jogo.tela)

    pygame.quit()
    print("SMOKE OK - todos os estados rodaram sem erro")


if __name__ == "__main__":
    main()
