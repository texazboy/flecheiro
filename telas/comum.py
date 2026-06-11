# -*- coding: utf-8 -*-
"""
Kit de interface compartilhado pelas telas.

Tudo que e "cara" do jogo mora aqui: o painel chanfrado com gradiente, a faixa
de titulo com os losanguinhos, as teclas desenhadas (keycap), a barrinha de
progresso e o cursor de selecao. Os overlays usam essas pecas e ficam todos com
a mesma identidade visual.

O texto renderizado fica num cache: a HUD escreve as mesmas frases todo frame
e o font.render do pygame nao e de graca.
"""

import math

import pygame

import config

_cache_texto = {}


def _render(fonte, msg, cor):
    chave = (id(fonte), msg, cor)
    img = _cache_texto.get(chave)
    if img is None:
        if len(_cache_texto) > 400:
            _cache_texto.clear()
        img = fonte.render(msg, True, cor)
        _cache_texto[chave] = img
    return img


def texto(tela, fonte, msg, x, y, cor=config.BRANCO, centro=False, sombra=True):
    img = _render(fonte, msg, cor)
    r = img.get_rect()
    if centro:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    if sombra:
        tela.blit(_render(fonte, msg, config.PRETO), (r.x + 1, r.y + 1))
    tela.blit(img, r)
    return r


# ---------------------------------------------------------------- paineis
def painel(tela, rect, cor_fundo=(30, 32, 48), cor_borda=None, alpha=235):
    """Painel estilo RPG: gradiente vertical, cantos chanfrados, borda dupla
    (escura por fora, um fio de luz por dentro no topo)."""
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    topo = (min(255, cor_fundo[0] + 14), min(255, cor_fundo[1] + 14),
            min(255, cor_fundo[2] + 18))
    h = rect.height
    for y in range(h):
        f = y / max(1, h - 1)
        cor = (int(topo[0] + (cor_fundo[0] - topo[0]) * f),
               int(topo[1] + (cor_fundo[1] - topo[1]) * f),
               int(topo[2] + (cor_fundo[2] - topo[2]) * f), alpha)
        s.fill(cor, (0, y, rect.width, 1))

    # chanfro: recorta 2px de cada canto
    vazio = (0, 0, 0, 0)
    w = rect.width
    for px, py in ((0, 0), (w - 2, 0), (0, h - 2), (w - 2, h - 2)):
        s.fill(vazio, (px, py, 2, 1) if py in (0, h - 2) else (px, py, 1, 2))
    s.fill(vazio, (0, 0, 1, 2))
    s.fill(vazio, (w - 1, 0, 1, 2))
    s.fill(vazio, (0, h - 2, 1, 2))
    s.fill(vazio, (w - 1, h - 2, 1, 2))

    # contorno chanfrado
    escura = cor_borda if cor_borda else (10, 10, 16)
    pontos = [(2, 0), (w - 3, 0), (w - 1, 2), (w - 1, h - 3),
              (w - 3, h - 1), (2, h - 1), (0, h - 3), (0, 2)]
    pygame.draw.lines(s, escura, True, pontos, 1)
    # fio de luz interno no topo (luz vindo de cima)
    pygame.draw.line(s, (255, 255, 255, 26), (2, 1), (w - 3, 1), 1)

    tela.blit(s, rect.topleft)


def faixa_titulo(tela, fonte, msg, cx, y, cor=config.AMARELO):
    """Titulo com linhas e losanguinhos dos lados:  ---<> TITULO <>---"""
    r = texto(tela, fonte, msg, cx, y, cor, centro=True)
    cy = r.centery
    for lado in (-1, 1):
        losango_x = (r.left - 11) if lado < 0 else (r.right + 11)
        inicio_x = losango_x + 5 * lado
        fim_x = inicio_x + 30 * lado
        pygame.draw.line(tela, cor, (inicio_x, cy), (fim_x, cy), 1)
        pygame.draw.polygon(tela, cor, [(losango_x - 3, cy), (losango_x, cy - 3),
                                        (losango_x + 3, cy), (losango_x, cy + 3)])
    return r


def keycap(tela, fonte, tecla_txt, x, y, ativa=False):
    """Desenha uma teclinha de teclado. Devolve o rect (pra encadear texto)."""
    w = fonte.size(tecla_txt)[0] + 8
    h = 13
    r = pygame.Rect(x, y, w, h)
    fundo = (210, 200, 120) if ativa else (52, 56, 74)
    pygame.draw.rect(tela, (14, 14, 20), r.move(0, 1))           # sombra da tecla
    pygame.draw.rect(tela, fundo, r)
    pygame.draw.line(tela, (255, 255, 255), (r.left + 1, r.top), (r.right - 2, r.top), 1)
    pygame.draw.rect(tela, (14, 14, 20), r, 1)
    cor_txt = (30, 28, 16) if ativa else config.BRANCO
    img = _render(fonte, tecla_txt, cor_txt)
    tela.blit(img, (r.centerx - img.get_width() // 2,
                    r.centery - img.get_height() // 2))
    return r


def legenda_teclas(tela, fonte, itens, cx, y):
    """Linha de '[tecla] acao' centralizada. itens = [(tecla, acao), ...]"""
    larguras = []
    for tecla_txt, acao in itens:
        larguras.append(fonte.size(tecla_txt)[0] + 8 + 4 + fonte.size(acao)[0] + 14)
    x = cx - sum(larguras) // 2
    for (tecla_txt, acao), w in zip(itens, larguras):
        r = keycap(tela, fonte, tecla_txt, x, y)
        texto(tela, fonte, acao, r.right + 4, y + 1, config.CINZA)
        x += w


def barra(tela, rect, frac, cor, cor_fundo=(18, 20, 30)):
    """Barrinha de progresso com miolo em dois tons."""
    frac = max(0.0, min(1.0, frac))
    pygame.draw.rect(tela, cor_fundo, rect)
    cheio = int((rect.width - 2) * frac)
    if cheio > 0:
        interno = pygame.Rect(rect.left + 1, rect.top + 1, cheio, rect.height - 2)
        pygame.draw.rect(tela, cor, interno)
        clara = (min(255, cor[0] + 50), min(255, cor[1] + 50), min(255, cor[2] + 50))
        pygame.draw.rect(tela, clara, (interno.left, interno.top, cheio, 1))
    pygame.draw.rect(tela, (10, 10, 16), rect, 1)


def cursor_selecao(tela, x, y):
    """Setinha de selecao que respira (pra listas de loja etc.)."""
    desloc = int((math.sin(pygame.time.get_ticks() * 0.008) + 1) * 1.5)
    pygame.draw.polygon(tela, config.AMARELO,
                        [(x + desloc, y), (x + desloc, y + 6), (x + 4 + desloc, y + 3)])


def separador(tela, x1, x2, y):
    """Linha divisoria dupla (escura + fio de luz)."""
    pygame.draw.line(tela, (12, 12, 18), (x1, y), (x2, y), 1)
    pygame.draw.line(tela, (255, 255, 255, 30), (x1, y + 1), (x2, y + 1), 1)


def surgimento(nasceu_ms, dur=160.0):
    """0..1 com ease-out desde que o overlay abriu; da o 'pop' de entrada."""
    t = (pygame.time.get_ticks() - nasceu_ms) / dur
    if t >= 1.0:
        return 1.0
    if t <= 0.0:
        return 0.0
    return 1.0 - (1.0 - t) ** 3


def escurecer(tela, alpha=150):
    """Cobre a tela toda com um veu escuro (pra destacar um overlay por cima)."""
    veu = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
    veu.fill((0, 0, 0, alpha))
    tela.blit(veu, (0, 0))
