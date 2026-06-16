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
            elif evento.key == pygame.K_c:
                som.tocar("clique")
                self.jogo.trocar_estado(CreditosState(self.jogo))
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
        cx = config.LARGURA // 2
        # titulo com contorno: quatro sombras em volta + cara dourada
        ty = int(66 + bob)
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            comum.texto(tela, self.fonte_g, "FLECHEIRO", cx + dx, ty + dy,
                        (60, 40, 10), centro=True, sombra=False)
        comum.texto(tela, self.fonte_g, "FLECHEIRO", cx, ty, config.AMARELO, centro=True)
        # uma flecha sublinhando o titulo
        y = int(92 + bob)
        pygame.draw.line(tela, config.BRANCO, (150, y), (322, y), 1)
        pygame.draw.polygon(tela, config.BRANCO, [(322, y - 3), (330, y), (322, y + 3)])
        pygame.draw.rect(tela, config.VERMELHO, (148, y - 2, 2, 5))
        comum.texto(tela, self.fonte_p, "um arqueiro, algoritmos e muitas flechas",
                    cx, 106, config.BRANCO, centro=True)

        if int(self.tempo * 1.6) % 2 == 0:
            r = comum.keycap(tela, self.fonte_p, "Enter", cx - 44, 140)
            comum.texto(tela, self.fonte, "comecar", r.right + 6, 139, config.VERDE)

        painel = pygame.Rect(82, 164, config.LARGURA - 164, 64)
        comum.painel(tela, painel, alpha=185)
        comum.legenda_teclas(tela, self.fonte_p,
                             [("A/D", "mover"), ("Espaco", "pular"),
                              ("Mouse", "segurar/soltar atira")],
                             painel.centerx, painel.top + 9)
        comum.legenda_teclas(tela, self.fonte_p,
                             [("E", "coletar"), ("T", "rota TSP"), ("I", "inventario")],
                             painel.centerx, painel.top + 26)
        comum.legenda_teclas(tela, self.fonte_p,
                             [("Esc", "pausa"), ("M", "som")],
                             painel.centerx, painel.top + 43)

        r = comum.keycap(tela, self.fonte_p, "C", cx - 64, config.ALTURA - 20)
        comum.texto(tela, self.fonte_p, "creditos", r.right + 4, config.ALTURA - 19, config.CINZA)
        comum.texto(tela, self.fonte_p, "ESC sair", cx + 20, config.ALTURA - 19, config.CINZA)


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

    def _medalha(self, tela, cx, cy):
        """Medalhinha de ouro com fita, coroando o painel de vitoria."""
        pygame.draw.polygon(tela, (190, 60, 70), [(cx - 6, cy - 14), (cx - 1, cy - 4),
                                                  (cx - 9, cy - 4)])
        pygame.draw.polygon(tela, (150, 45, 60), [(cx + 6, cy - 14), (cx + 9, cy - 4),
                                                  (cx + 1, cy - 4)])
        pygame.draw.circle(tela, config.AMARELO, (cx, cy), 8)
        pygame.draw.circle(tela, (170, 135, 40), (cx, cy), 8, 1)
        pygame.draw.circle(tela, (255, 240, 170), (cx - 2, cy - 2), 2)
        comum.texto(tela, self.fonte, "1", cx, cy + 1, (120, 92, 20),
                    centro=True, sombra=False)

    def desenhar(self, tela):
        self.fundo.desenhar(tela, self.tempo * 6)
        tela.blit(self.terreno, (0, 0))
        m = self.jogo.mundo

        comum.faixa_titulo(tela, self.fonte_g, "VITORIA!", config.LARGURA // 2, 52)

        painel = pygame.Rect(130, 92, config.LARGURA - 260, 104)
        comum.painel(tela, painel, alpha=215)
        self._medalha(tela, painel.centerx, painel.top + 2)
        minutos = int(m.tempo // 60)
        segundos = int(m.tempo % 60)
        linhas = [
            f"Tempo de jornada: {minutos}m {segundos:02d}s",
            f"Inimigos vencidos: {m.abatidos}    Itens coletados: {m.coletados}",
            f"Arcos forjados: {m.arcos_forjados}    Ouro: {m.ouro}",
        ]
        y = painel.top + 20
        for linha in linhas:
            comum.texto(tela, self.fonte, linha, painel.centerx, y, config.BRANCO, centro=True)
            y += 21
        comum.texto(tela, self.fonte, f"Arco final: {m.arco.nome}",
                    painel.centerx, y, config.VERDE, centro=True)

        comum.legenda_teclas(tela, self.fonte, [("Enter", "voltar ao menu")],
                             config.LARGURA // 2, config.ALTURA - 30)

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
        painel = pygame.Rect(140, 70, config.LARGURA - 280, 110)
        comum.painel(tela, painel, cor_fundo=(40, 22, 26), alpha=225)
        comum.texto(tela, self.fonte_g, "VOCE CAIU", painel.centerx,
                    painel.top + 24, config.VERMELHO, centro=True)
        comum.texto(tela, self.fonte, f"A fase {self.numero} ainda espera por voce.",
                    painel.centerx, painel.top + 52, config.BRANCO, centro=True)
        comum.legenda_teclas(tela, self.fonte,
                             [("R", "tentar de novo"), ("Esc", "menu")],
                             painel.centerx, painel.bottom - 28)


class CreditosState(Estado):
    """Tela de creditos, com os icones de redes sociais (Cryo's Mini GUI)."""

    LINHAS = [
        ("Flecheiro", config.AMARELO),
        ("Codigo: Jose, Pedro, Matheus S. e Matheus V.", config.BRANCO),
        ("", config.BRANCO),
        ("Arte: LuizMelo, Pixel Frog, vnitti,", config.CINZA),
        ("Cainos, GandalfHardcore e Cryo", config.CINZA),
        ("Fonte: monogram (datagoblin)", config.CINZA),
        ("Som e musica: gerados em codigo", config.CINZA),
        ("Feito com Python + pygame-ce", config.CINZA),
    ]

    def __init__(self, jogo):
        super().__init__(jogo)
        self.fonte = jogo.recursos.fonte(24)
        self.fonte_p = jogo.recursos.fonte(16)
        self.fundo = Fundo(jogo.recursos, "noite", semente=4)
        self.socials = jogo.recursos.sprite_opcional("socials")   # grade 16x16
        self.tempo = 0.0

    def entrar(self):
        som.musica("menu")

    def tratar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            self.jogo.trocar_estado(MenuState(self.jogo))

    def atualizar(self, dt):
        self.tempo += dt

    def desenhar(self, tela):
        self.fundo.desenhar(tela, self.tempo * 8)
        comum.escurecer(tela, 120)
        painel = pygame.Rect(60, 28, config.LARGURA - 120, config.ALTURA - 56)
        comum.painel(tela, painel)
        comum.faixa_titulo(tela, self.fonte, "CREDITOS", painel.centerx, painel.top + 2)

        y = painel.top + 26
        for txt, cor in self.LINHAS:
            if txt:
                comum.texto(tela, self.fonte_p, txt, painel.centerx, y, cor, centro=True)
            y += 16

        # fileira de icones sociais (decorativa) recortada da grade 16x16
        if self.socials is not None:
            n = 8
            larg = n * 18
            ix = painel.centerx - larg // 2
            iy = painel.bottom - 40
            for i in range(n):
                icone = self.socials.subsurface((i * 16, 0, 16, 16))
                tela.blit(icone, (ix + i * 18, iy))

        comum.legenda_teclas(tela, self.fonte_p, [("Esc", "voltar")],
                             painel.centerx, painel.bottom - 18)
