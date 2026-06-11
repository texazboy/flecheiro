# -*- coding: utf-8 -*-
"""
Telas de menu inicial, vitoria e game over.

O menu virou uma "vitrine" do jogo: o ceu do poente rola devagar ao fundo, o
arqueiro fica parado respirando no canto e o titulo balanca. A vitoria solta
confete e mostra as estatisticas da partida.
"""

import math
import random

import pygame

import config
from core.estados import Estado
from core.camera import Camera
from core.cenario import Fundo, montar_terreno
from core.mundo import Mundo
from core import som
from entidades.efeitos import Particula
from telas import comum

_CORES_CONFETE = [(232, 196, 92), (96, 178, 102), (138, 92, 168),
                  (220, 138, 64), (104, 156, 204), (196, 76, 72)]


def _terreno_de_tela(recursos, tema):
    """Faixa de chao do tamanho da tela, so pra apoiar as telas de menu."""
    chao = [pygame.Rect(0, 238, config.LARGURA, 32)]
    sup, _ = montar_terreno(config.LARGURA, chao, [], recursos, semente=9, tema=tema)
    return sup


class MenuState(Estado):
    def __init__(self, jogo):
        super().__init__(jogo)
        self.fonte_g = jogo.recursos.fonte(52)
        self.fonte = jogo.recursos.fonte(20)
        self.fonte_p = jogo.recursos.fonte(16)
        self.fundo = Fundo(jogo.recursos, "poente", semente=3)
        self.terreno = _terreno_de_tela(jogo.recursos, "poente")
        self.anim = jogo.recursos.animacao("jogador", "parado", 24, fps=3)
        self.tempo = 0.0

    def entrar(self):
        som.musica("menu")

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                som.tocar("porta")
                self.jogo.mundo = Mundo()          # comeca uma partida nova
                from fases.fase import Fase
                self.jogo.trocar_estado(Fase(self.jogo, 1))
            elif evento.key == pygame.K_ESCAPE:
                self.jogo.rodando = False

    def atualizar(self, dt):
        self.tempo += dt
        self.anim.atualizar(dt)

    def desenhar(self, tela):
        self.fundo.desenhar(tela, self.tempo * 10)   # parallax rolando sozinho
        tela.blit(self.terreno, (0, 0))
        tela.blit(self.anim.quadro(), (52, 238 - 24))

        bob = math.sin(self.tempo * 2.0) * 3
        comum.texto(tela, self.fonte_g, "FLECHEIRO", config.LARGURA // 2,
                    int(66 + bob), config.AMARELO, centro=True)
        # uma flecha sublinhando o titulo
        y = int(92 + bob)
        pygame.draw.line(tela, config.BRANCO, (150, y), (322, y), 1)
        pygame.draw.polygon(tela, config.BRANCO, [(322, y - 3), (330, y), (322, y + 3)])
        comum.texto(tela, self.fonte_p, "um arqueiro, algoritmos e muitas flechas",
                    config.LARGURA // 2, 106, config.BRANCO, centro=True)

        if int(self.tempo * 1.6) % 2 == 0:
            comum.texto(tela, self.fonte, "ENTER  -  comecar", config.LARGURA // 2, 146,
                        config.VERDE, centro=True)

        painel = pygame.Rect(120, 164, config.LARGURA - 240, 64)
        comum.painel(tela, painel, alpha=170)
        comum.texto(tela, self.fonte_p, "Mover: A/D    Pular: Espaco    Atirar: segure e solte o mouse",
                    painel.centerx, painel.top + 14, config.CINZA, centro=True)
        comum.texto(tela, self.fonte_p, "Coletar: E    Rota otima (TSP): T    Inventario: I",
                    painel.centerx, painel.top + 30, config.CINZA, centro=True)
        comum.texto(tela, self.fonte_p, "Pausa: Esc    Som: M",
                    painel.centerx, painel.top + 46, config.CINZA, centro=True)

        comum.texto(tela, self.fonte_p, "ESC para sair", config.LARGURA // 2,
                    config.ALTURA - 14, config.CINZA, centro=True)


class VitoriaState(Estado):
    def __init__(self, jogo):
        super().__init__(jogo)
        self.fonte_g = jogo.recursos.fonte(46)
        self.fonte = jogo.recursos.fonte(18)
        self.fundo = Fundo(jogo.recursos, "dia", semente=2)
        self.terreno = _terreno_de_tela(jogo.recursos, "dia")
        self.camera = Camera(config.LARGURA, config.ALTURA, config.LARGURA)
        self.confetes = []
        self.tempo = 0.0

    def entrar(self):
        som.musica("vila")
        som.tocar("cura")

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_ESCAPE):
            self.jogo.trocar_estado(MenuState(self.jogo))

    def atualizar(self, dt):
        self.tempo += dt
        for _ in range(2):
            self.confetes.append(Particula(random.uniform(0, config.LARGURA), -4,
                                           random.choice(_CORES_CONFETE),
                                           espalhar=0.8, sobe=-0.3, gravidade=0.04,
                                           vida=(1.6, 2.6), tam=(1, 2)))
        for p in self.confetes:
            p.atualizar(dt)
        self.confetes = [p for p in self.confetes if not p.morta]

    def desenhar(self, tela):
        self.fundo.desenhar(tela, self.tempo * 6)
        tela.blit(self.terreno, (0, 0))
        m = self.jogo.mundo

        comum.texto(tela, self.fonte_g, "VITORIA!", config.LARGURA // 2, 58,
                    config.AMARELO, centro=True)

        painel = pygame.Rect(130, 92, config.LARGURA - 260, 102)
        comum.painel(tela, painel, alpha=200)
        minutos = int(m.tempo // 60)
        segundos = int(m.tempo % 60)
        linhas = [
            f"Tempo de jornada: {minutos}m {segundos:02d}s",
            f"Inimigos vencidos: {m.abatidos}    Itens coletados: {m.coletados}",
            f"Arcos forjados: {m.arcos_forjados}    Ouro: {m.ouro}",
            f"Arco final: {m.arco.nome}",
        ]
        y = painel.top + 14
        for linha in linhas:
            comum.texto(tela, self.fonte, linha, painel.centerx, y, config.BRANCO, centro=True)
            y += 21

        comum.texto(tela, self.fonte, "ENTER para voltar ao menu", config.LARGURA // 2,
                    config.ALTURA - 26, config.CINZA, centro=True)

        for p in self.confetes:
            p.desenhar(tela, self.camera)


class GameOverState(Estado):
    def __init__(self, jogo, numero):
        super().__init__(jogo)
        self.numero = numero
        self.fonte_g = jogo.recursos.fonte(44)
        self.fonte = jogo.recursos.fonte(18)
        self.fundo = Fundo(jogo.recursos, "noite", semente=8)

    def entrar(self):
        som.musica(None)

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_r, pygame.K_RETURN):
                self.jogo.mundo.vida = self.jogo.mundo.vida_max
                from fases.fase import Fase
                self.jogo.trocar_estado(Fase(self.jogo, self.numero))
            elif evento.key == pygame.K_ESCAPE:
                self.jogo.trocar_estado(MenuState(self.jogo))

    def desenhar(self, tela):
        self.fundo.desenhar(tela, 0)
        comum.escurecer(tela, 90)
        comum.texto(tela, self.fonte_g, "VOCE CAIU", config.LARGURA // 2, 90,
                    config.VERMELHO, centro=True)
        comum.texto(tela, self.fonte, f"A fase {self.numero} ainda espera por voce.",
                    config.LARGURA // 2, 130, config.BRANCO, centro=True)
        comum.texto(tela, self.fonte, "R - tentar de novo     ESC - menu",
                    config.LARGURA // 2, 160, config.CINZA, centro=True)
