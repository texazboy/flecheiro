# -*- coding: utf-8 -*-
"""
Smoke test do jogo: roda tudo sem abrir janela (driver de video "dummy") pra
garantir que nenhuma tela quebra em tempo de execucao. Nao testa jogabilidade
fina (isso e no olho), so que update/desenho de cada estado nao estoura erro.

Percorre o fluxo inteiro: menu -> fase 1 -> vila -> fase 2 -> vila -> fase 3
-> vitoria, passando por pausa, inventario, dialogo, ferraria e loja.

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


def rodar_frames(jogo, n):
    for _ in range(n):
        jogo.estado.atualizar(1 / 60)
        jogo.estado.desenhar(jogo.tela)


def atirar(jogo, fase, pos):
    """Tiro carregado: aperta, segura uns frames e solta."""
    fase.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
    rodar_frames(jogo, 8)
    fase.tratar_evento(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos))


def passar_dialogo(vila, falas):
    """Cada fala pede dois E: um revela o texto (maquina de escrever), outro avanca."""
    for _ in range(falas * 2):
        vila.tratar_evento(tecla(pygame.K_e))


def main():
    jogo = Jogo()

    # --- menu ---
    jogo.estado.desenhar(jogo.tela)
    jogo.estado.tratar_evento(tecla(pygame.K_RETURN))
    assert isinstance(jogo.estado, Fase), "Enter no menu deveria iniciar a fase 1"
    fase = jogo.estado

    # --- fase 1: atira, pausa, abre overlays, coleta, mostra rota ---
    for i in range(4):
        atirar(jogo, fase, (200 + i * 30, 80 + i * 10))
    fase.tratar_evento(tecla(pygame.K_ESCAPE))   # pausa
    fase.desenhar(jogo.tela)
    fase.tratar_evento(tecla(pygame.K_ESCAPE))   # despausa
    assert fase.overlay is None, "Esc duas vezes deveria pausar e voltar"
    fase.tratar_evento(tecla(pygame.K_t))        # liga rota do TSP
    fase.tratar_evento(tecla(pygame.K_i))        # abre inventario
    fase.tratar_evento(tecla(pygame.K_i))        # fecha
    fase.tratar_evento(tecla(pygame.K_e))        # coleta proximos
    fase.tratar_evento(tecla(pygame.K_SPACE))
    rodar_frames(jogo, 180)

    # forca a chegada na porta pra testar a transicao fase -> vila
    jogo.estado.jogador.rect.topleft = jogo.estado.porta.topleft
    jogo.estado.atualizar(1 / 60)
    assert isinstance(jogo.estado, Vila), "porta da fase 1 deveria levar a vila"
    vila = jogo.estado
    assert vila.proxima_fase == 2, "primeira vila deveria apontar pra fase 2"
    rodar_frames(jogo, 30)

    # --- vila: ferreiro -> dialogo -> ferraria -> forja ---
    vila.jogador.rect.centerx = 200
    vila.tratar_evento(tecla(pygame.K_e))        # abre o dialogo
    passar_dialogo(vila, 3)                      # 3 falas -> vira ferraria
    vila.desenhar(jogo.tela)
    vila.tratar_evento(tecla(pygame.K_f))        # forja (mochila)
    vila.desenhar(jogo.tela)
    vila.tratar_evento(tecla(pygame.K_q))        # sai da ferraria

    # --- vila: lojista -> dialogo -> loja -> vende/compra ---
    vila.jogador.rect.centerx = 430
    vila.tratar_evento(tecla(pygame.K_e))
    passar_dialogo(vila, 3)
    vila.desenhar(jogo.tela)
    vila.tratar_evento(tecla(pygame.K_RETURN))   # vende
    vila.tratar_evento(tecla(pygame.K_c))        # compra cura
    vila.tratar_evento(tecla(pygame.K_q))

    # --- vila: aldeao (so dialogo) ---
    vila.jogador.rect.centerx = 640
    vila.tratar_evento(tecla(pygame.K_e))        # abre
    passar_dialogo(vila, 3)                      # 3 falas e fecha
    vila.desenhar(jogo.tela)
    assert vila.overlay is None, "dialogo do aldeao deveria ter fechado"

    # --- vila -> fase 2 pela porta ---
    vila.jogador.rect.x = vila.porta.x
    vila.tratar_evento(tecla(pygame.K_e))
    assert isinstance(jogo.estado, Fase) and jogo.estado.numero == 2, "porta da vila -> fase 2"
    fase2 = jogo.estado
    for i in range(4):
        atirar(jogo, fase2, (150 + i * 25, 120))
    fase2.tratar_evento(tecla(pygame.K_t))
    rodar_frames(jogo, 120)

    # --- fase 2 -> vila de novo -> fase 3 ---
    jogo.estado.jogador.rect.topleft = jogo.estado.porta.topleft
    jogo.estado.atualizar(1 / 60)
    assert isinstance(jogo.estado, Vila) and jogo.estado.proxima_fase == 3, \
        "depois da fase 2 a vila deveria apontar pra fase 3"
    rodar_frames(jogo, 30)
    jogo.estado.jogador.rect.x = jogo.estado.porta.x
    jogo.estado.tratar_evento(tecla(pygame.K_e))
    assert isinstance(jogo.estado, Fase) and jogo.estado.numero == 3, "porta da vila -> fase 3"
    rodar_frames(jogo, 90)

    # --- fase 3 -> vitoria ---
    jogo.estado.jogador.rect.topleft = jogo.estado.porta.topleft
    jogo.estado.atualizar(1 / 60)
    assert isinstance(jogo.estado, VitoriaState), "porta da fase 3 -> vitoria"
    rodar_frames(jogo, 30)

    # --- desenha o game over so pra garantir que nao quebra ---
    GameOverState(jogo, 1).desenhar(jogo.tela)

    pygame.quit()
    print("SMOKE OK - menu, 3 fases, vila, overlays e vitoria rodaram sem erro")


if __name__ == "__main__":
    main()
