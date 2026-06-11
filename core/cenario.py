# -*- coding: utf-8 -*-
"""
Cenario do jogo: ceu com gradiente, sol/lua, estrelas, nuvens, montanhas em
parallax e o chao montado em tiles com decoracao (grama, flores, pedrinhas).

Quase tudo aqui e PRE-RENDERIZADO uma unica vez quando a fase nasce: o ceu vira
uma imagem, cada camada de montanha vira uma imagem "emendavel" (a borda direita
casa com a esquerda, entao da pra rolar infinito), e o chao da fase inteira vira
uma unica superficie. No frame a frame sobra so meia duzia de blits - bem mais
leve que desenhar tile por tile, elipse por elipse, como era antes.

Temas disponiveis: "dia", "poente" e "noite". Cada fase usa um, entao o jogador
sente o tempo passando conforme avanca.
"""

import math
import random

import pygame

import config

TEMAS = {
    "dia": dict(
        ceu_topo=(88, 144, 208), ceu_base=(172, 212, 240),
        astro=(252, 240, 190), astro_pos=(356, 56), lua=False, estrelas=False,
        camadas=[(60, 108, 80), (78, 138, 94), (94, 164, 106)],
        nuvens=True, cor_nuvem=(245, 248, 252),
        tinta=None,
    ),
    "poente": dict(
        ceu_topo=(110, 76, 134), ceu_base=(244, 158, 92),
        astro=(255, 214, 140), astro_pos=(340, 150), lua=False, estrelas=False,
        camadas=[(78, 54, 92), (108, 70, 96), (140, 92, 100)],
        nuvens=True, cor_nuvem=(255, 206, 160),
        tinta=(255, 214, 178),
    ),
    "noite": dict(
        ceu_topo=(16, 20, 40), ceu_base=(46, 58, 96),
        astro=(232, 234, 222), astro_pos=(380, 48), lua=True, estrelas=True,
        camadas=[(28, 34, 58), (36, 44, 72), (46, 56, 88)],
        nuvens=False, cor_nuvem=(70, 80, 110),
        tinta=(150, 158, 210),
    ),
}


def _mistura(a, b, f):
    return (int(a[0] + (b[0] - a[0]) * f),
            int(a[1] + (b[1] - a[1]) * f),
            int(a[2] + (b[2] - a[2]) * f))


def _borrar(superficie, fator):
    """Desfoque barato: encolhe e amplia de volta (suaviza tudo).
    Usado nas camadas distantes pra dar profundidade de campo."""
    w, h = superficie.get_size()
    pequena = pygame.transform.smoothscale(superficie, (max(1, w // fator),
                                                        max(1, h // fator)))
    return pygame.transform.smoothscale(pequena, (w, h))


class Fundo:
    """Ceu + parallax. Criar uma vez por fase e chamar desenhar() por frame."""

    def __init__(self, recursos, tema="dia", semente=0):
        self.tema = TEMAS.get(tema, TEMAS["dia"])
        self.nome_tema = tema
        rnd = random.Random(semente * 31 + 7)
        self.ceu = self._montar_ceu(rnd)
        self.img_extra = recursos.fundo_img()   # fundo.png do usuario, se houver
        # camadas de montanha: (surface, fator de parallax). As distantes vao
        # desfocadas (profundidade de campo, estilo HD-2D).
        fatores = (0.22, 0.42, 0.65)
        bases = (148, 172, 198)
        amps = (24, 18, 12)
        borroes = (3, 2, 1)
        self.camadas = []
        for cor, fator, base, amp, borrao in zip(self.tema["camadas"], fatores,
                                                 bases, amps, borroes):
            img = self._montar_morros(cor, base, amp, rnd)
            if borrao > 1:
                img = _borrar(img, borrao)
            self.camadas.append((img, fator))
        self.nuvens = self._montar_nuvens(rnd) if self.tema["nuvens"] else []
        self.raios = self._montar_raios() if tema == "dia" else None

    # ------------------------------------------------------------ construcao
    def _montar_ceu(self, rnd):
        ceu = pygame.Surface((config.LARGURA, config.ALTURA))
        topo, base = self.tema["ceu_topo"], self.tema["ceu_base"]
        for y in range(config.ALTURA):
            cor = _mistura(topo, base, y / config.ALTURA)
            pygame.draw.line(ceu, cor, (0, y), (config.LARGURA, y))

        if self.tema["estrelas"]:
            for _ in range(70):
                x = rnd.randrange(config.LARGURA)
                y = rnd.randrange(0, 170)
                brilho = rnd.randint(120, 240)
                tam = 2 if rnd.random() < 0.12 else 1
                pygame.draw.rect(ceu, (brilho, brilho, min(255, brilho + 15)), (x, y, tam, tam))

        # sol (ou lua) com um halo suave
        ax, ay = self.tema["astro_pos"]
        cor = self.tema["astro"]
        raio = 13 if self.tema["lua"] else 16
        halo = pygame.Surface((raio * 6, raio * 6), pygame.SRCALPHA)
        for r, alfa in ((raio * 3, 18), (raio * 2, 32), (int(raio * 1.4), 50)):
            pygame.draw.circle(halo, (cor[0], cor[1], cor[2], alfa), (raio * 3, raio * 3), r)
        ceu.blit(halo, (ax - raio * 3, ay - raio * 3))
        pygame.draw.circle(ceu, cor, (ax, ay), raio)
        if self.tema["lua"]:
            # "mordida" da lua crescente, na cor do ceu local
            pygame.draw.circle(ceu, _mistura(self.tema["ceu_topo"], self.tema["ceu_base"], ay / config.ALTURA),
                               (ax + 5, ay - 3), raio - 3)
        return ceu

    def _montar_morros(self, cor, base_y, amp, rnd):
        """Silhueta de morros que emenda nas bordas (senos com ciclos inteiros)."""
        larg = config.LARGURA
        s = pygame.Surface((larg, config.ALTURA), pygame.SRCALPHA)
        k1 = rnd.choice((2, 3))
        k2 = rnd.choice((5, 7))
        p1 = rnd.uniform(0, math.tau)
        p2 = rnd.uniform(0, math.tau)
        pontos = []
        for x in range(0, larg + 1, 4):
            y = (base_y
                 + amp * math.sin(math.tau * k1 * x / larg + p1)
                 + amp * 0.45 * math.sin(math.tau * k2 * x / larg + p2))
            pontos.append((x, y))
        pygame.draw.polygon(s, cor, [(0, config.ALTURA)] + pontos + [(larg, config.ALTURA)])
        # pinheirinhos na camada mais proxima dao profundidade
        if base_y >= 190:
            escura = _mistura(cor, (0, 0, 0), 0.25)
            for _ in range(10):
                px = rnd.randrange(8, larg - 8)
                py = base_y + amp * math.sin(math.tau * k1 * px / larg + p1) \
                    + amp * 0.45 * math.sin(math.tau * k2 * px / larg + p2)
                h = rnd.randint(10, 18)
                pygame.draw.polygon(s, escura, [(px - 4, py + 2), (px + 4, py + 2), (px, py - h)])
        return s

    def _montar_raios(self):
        """Feixes de luz diagonais (god rays), bem suaves, pro tema de dia."""
        s = pygame.Surface((config.LARGURA, config.ALTURA))
        for x_topo, larg in ((40, 34), (150, 22), (270, 40), (390, 26)):
            pygame.draw.polygon(s, (16, 14, 9),
                                [(x_topo, -10), (x_topo + larg, -10),
                                 (x_topo + larg - 70, config.ALTURA + 10),
                                 (x_topo - 70, config.ALTURA + 10)])
        return _borrar(s, 4)

    def _montar_nuvens(self, rnd):
        nuvens = []
        cor = self.tema["cor_nuvem"]
        for _ in range(5):
            larg = rnd.randint(36, 64)
            alt = rnd.randint(10, 16)
            s = pygame.Surface((larg, alt), pygame.SRCALPHA)
            for _ in range(4):
                rx = rnd.randint(0, larg - 18)
                ry = rnd.randint(0, alt - 8)
                pygame.draw.ellipse(s, (cor[0], cor[1], cor[2], 80), (rx, ry, 18, 9))
            nuvens.append(dict(img=s, x=rnd.uniform(0, config.LARGURA),
                               y=rnd.randint(18, 90), vel=rnd.uniform(2.0, 5.0)))
        return nuvens

    # ------------------------------------------------------------ por frame
    def desenhar(self, tela, offset_x):
        tela.blit(self.ceu, (0, 0))
        agora = pygame.time.get_ticks() * 0.001

        for nuvem in self.nuvens:
            faixa = config.LARGURA + 90
            x = (nuvem["x"] + agora * nuvem["vel"] - offset_x * 0.12) % faixa - 80
            tela.blit(nuvem["img"], (int(x), nuvem["y"]))

        if self.img_extra is not None:
            larg = self.img_extra.get_width()
            dx = -int(offset_x * 0.3) % larg
            y = config.ALTURA - self.img_extra.get_height()
            tela.blit(self.img_extra, (dx - larg, y))
            tela.blit(self.img_extra, (dx, y))

        for img, fator in self.camadas:
            larg = img.get_width()
            dx = -int(offset_x * fator) % larg
            tela.blit(img, (dx - larg, 0))
            if dx < config.LARGURA:
                tela.blit(img, (dx, 0))

        if self.raios is not None:
            balanco = int(math.sin(agora * 0.25) * 5)
            tela.blit(self.raios, (balanco, 0), special_flags=pygame.BLEND_RGB_ADD)


# ---------------------------------------------------------------------------
# Terreno: a fase inteira (chao + plataformas + decoracao) numa superficie so.
# ---------------------------------------------------------------------------
def _arvore(sup, x, base_y, rnd):
    """Arvore de copa redonda em tres tons, com contorno (fica atras do jogo)."""
    alt = rnd.randint(40, 58)
    topo = base_y - alt
    contorno = (26, 42, 30)
    escuro = (46, 90, 56)
    medio = (64, 122, 66)
    claro = (92, 156, 80)
    # tronco
    pygame.draw.rect(sup, (62, 44, 30), (x - 3, base_y - 18, 6, 18))
    pygame.draw.rect(sup, (88, 62, 40), (x - 2, base_y - 18, 2, 18))
    # copa: tres bolhas empilhadas com luz vindo de cima/esquerda
    larg = rnd.randint(30, 40)
    pygame.draw.ellipse(sup, contorno, (x - larg // 2 - 1, topo - 1, larg + 2, alt - 12 + 2))
    pygame.draw.ellipse(sup, escuro, (x - larg // 2, topo, larg, alt - 12))
    pygame.draw.ellipse(sup, medio, (x - larg // 2 + 2, topo + 2, larg - 7, alt - 18))
    pygame.draw.ellipse(sup, claro, (x - larg // 2 + 4, topo + 3, larg // 2 - 2, (alt - 18) // 2))
def montar_terreno(largura_mundo, solidos, plataformas, recursos, semente=1, tema="dia"):
    """Pre-renderiza o chao da fase inteira. Devolve (superficie, luzes_fixas):
    as luzes sao a posicao dos cogumelos luminosos que nascem de noite, pra
    fase plugar no sistema de iluminacao."""
    sup = pygame.Surface((largura_mundo, config.ALTURA), pygame.SRCALPHA)
    grama = recursos.tile_grama()
    terra = recursos.tile_terra()
    tabua = recursos.tile_plataforma()
    rnd = random.Random(semente)
    luzes_fixas = []

    # duas variantes de cada tile (a espelhada sai de graca) quebram a repeticao
    gramas = (grama, pygame.transform.flip(grama, True, False))
    terras = (terra, pygame.transform.flip(terra, True, False))

    clip_antigo = sup.get_clip()
    for s in solidos:
        sup.set_clip(s)
        for tx in range(s.left - s.left % 16, s.right, 16):
            sup.blit(gramas[rnd.randint(0, 1)], (tx, s.top))
            ty = s.top + 16
            while ty < s.bottom:
                sup.blit(terras[rnd.randint(0, 1)], (tx, ty))
                ty += 16
    for p in plataformas:
        sup.set_clip(p)
        for tx in range(p.left - p.left % 16, p.right, 16):
            sup.blit(tabua, (tx, p.top))
    sup.set_clip(clip_antigo)

    # arvores ao fundo do caminho (densidade estilo cenario de RPG)
    for s in solidos:
        if s.width < 200:
            continue
        x = s.left + 130
        while x < s.right - 150:
            if rnd.random() < 0.6:
                _arvore(sup, x, s.top, rnd)
            x += rnd.randint(150, 300)

    # decoracao em cima do chao: tufos, flores, pedrinhas, arbustos e, de
    # noite, cogumelos que brilham (viram fonte de luz na fase)
    noite = (tema == "noite")
    for s in solidos:
        if s.width < 40:
            continue  # pilares e paredes ficam sem enfeite
        x = s.left + 6
        while x < s.right - 6:
            sorte = rnd.random()
            topo = s.top
            if sorte < 0.26:
                pygame.draw.line(sup, config.VERDE, (x, topo - 3), (x, topo), 1)
                pygame.draw.line(sup, config.VERDE, (x + 2, topo - 2), (x + 2, topo), 1)
            elif sorte < 0.36:
                cor_flor = rnd.choice(((232, 120, 140), (240, 220, 120), (170, 150, 230)))
                pygame.draw.line(sup, config.VERDE_ESCURO, (x, topo - 3), (x, topo), 1)
                pygame.draw.rect(sup, cor_flor, (x - 1, topo - 5, 3, 3))
            elif sorte < 0.44:
                pygame.draw.rect(sup, config.CINZA, (x, topo + 2, 2, 2))
            elif sorte < 0.52:
                # arbusto: dois montinhos de verde
                pygame.draw.ellipse(sup, config.VERDE_ESCURO, (x - 4, topo - 6, 12, 7))
                pygame.draw.ellipse(sup, config.VERDE, (x - 1, topo - 4, 7, 5))
            elif noite and sorte < 0.58:
                # cogumelo luminoso
                pygame.draw.rect(sup, (210, 230, 220), (x, topo - 3, 1, 3))
                pygame.draw.rect(sup, (130, 230, 200), (x - 2, topo - 5, 5, 3))
                pygame.draw.rect(sup, (200, 255, 240), (x - 1, topo - 5, 1, 1))
                luzes_fixas.append((x, topo - 4, 22, (110, 200, 180)))
            x += rnd.randint(10, 26)

    # tinta da hora do dia (deixa o chao combinar com o ceu)
    tinta = TEMAS.get(tema, TEMAS["dia"])["tinta"]
    if tinta:
        sup.fill(tinta, special_flags=pygame.BLEND_RGB_MULT)
    return sup, luzes_fixas
