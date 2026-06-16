# -*- coding: utf-8 -*-
"""
Kit de interface compartilhado pelas telas - estilo "moldura dourada" de RPG.

Todo painel tem contorno escuro, moldura de ouro com bisel (clara em cima,
escura embaixo), rebites nos cantos e interior escuro com um leve brilho no
topo. Os titulos ficam em "faixas" (pilulas douradas) que cavalgam a borda do
painel, e as teclas viram botoezinhos dourados. Como todas as telas usam estas
mesmas pecas, o jogo inteiro fica com a mesma identidade.

O texto renderizado fica em cache: a HUD escreve as mesmas frases todo frame.
"""

import math

import pygame

import config

# paleta da moldura
OURO_CLARO = (238, 200, 124)
OURO = (198, 148, 70)
OURO_ESCURO = (130, 90, 42)
CONTORNO = (28, 20, 18)
FUNDO_PAINEL = (52, 46, 52)

_cache_texto = {}

# desligado quando a fonte pixel (monogram) esta ativa - pixel font fica nitida
# sem suavizacao. Definido pelo main na inicializacao.
ANTIALIAS = True


def _render(fonte, msg, cor):
    chave = (id(fonte), msg, cor)
    img = _cache_texto.get(chave)
    if img is None:
        if len(_cache_texto) > 400:
            _cache_texto.clear()
        img = fonte.render(msg, ANTIALIAS, cor)
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


def _rebite(s, cx, cy):
    pygame.draw.circle(s, CONTORNO, (cx, cy), 3)
    pygame.draw.circle(s, OURO, (cx, cy), 2)
    s.set_at((cx - 1, cy - 1), OURO_CLARO)


# ---------------------------------------------------------------- paineis
def painel(tela, rect, cor_fundo=None, cor_borda=None, alpha=238):
    """Painel com moldura dourada, bisel e rebites nos cantos."""
    base = cor_fundo if cor_fundo else FUNDO_PAINEL
    w, h = rect.width, rect.height
    raio = min(7, h // 2)
    s = pygame.Surface((w, h), pygame.SRCALPHA)

    pygame.draw.rect(s, CONTORNO, (0, 0, w, h), border_radius=raio)
    pygame.draw.rect(s, OURO, (1, 1, w - 2, h - 2), border_radius=max(2, raio - 1))
    # bisel da moldura: luz em cima, sombra embaixo
    pygame.draw.rect(s, OURO_CLARO, (1, 1, w - 2, h - 2), width=1,
                     border_radius=max(2, raio - 1))
    pygame.draw.line(s, OURO_ESCURO, (4, h - 3), (w - 5, h - 3), 1)

    # interior escuro (com a transparencia pedida) e brilho no topo
    interior = pygame.Rect(3, 3, w - 6, h - 6)
    pygame.draw.rect(s, (base[0], base[1], base[2], alpha), interior,
                     border_radius=max(2, raio - 2))
    pygame.draw.rect(s, (0, 0, 0, 90), interior, width=1,
                     border_radius=max(2, raio - 2))
    sheen = pygame.Rect(5, 4, w - 10, max(2, h // 7))
    pygame.draw.rect(s, (255, 255, 255, 12), sheen, border_radius=3)

    if w > 70 and h > 34:
        _rebite(s, 6, 6)
        _rebite(s, w - 7, 6)
        _rebite(s, 6, h - 7)
        _rebite(s, w - 7, h - 7)

    tela.blit(s, rect.topleft)


def faixa_titulo(tela, fonte, msg, cx, y, cor=OURO_CLARO):
    """Faixa-pilula dourada com o titulo dentro (cavalga a borda do painel)."""
    w = fonte.size(msg)[0] + 34
    h = 20
    r = pygame.Rect(0, 0, w, h)
    r.center = (cx, y)
    pygame.draw.rect(tela, CONTORNO, r.inflate(4, 4), border_radius=11)
    pygame.draw.rect(tela, OURO, r.inflate(2, 2), border_radius=10)
    pygame.draw.line(tela, OURO_CLARO, (r.left + 4, r.top - 0), (r.right - 4, r.top - 0), 1)
    interior = r.inflate(-4, -4)
    pygame.draw.rect(tela, (40, 34, 40), interior, border_radius=7)
    texto(tela, fonte, msg, cx, y, cor, centro=True)
    # pininhos nas pontas, como nos banners de referencia
    for px in (r.left - 1, r.right + 1):
        pygame.draw.circle(tela, CONTORNO, (px, r.centery), 3)
        pygame.draw.circle(tela, OURO, (px, r.centery), 2)
    return r


def keycap(tela, fonte, tecla_txt, x, y, ativa=False):
    """Botaozinho dourado com o nome da tecla. Devolve o rect."""
    w = fonte.size(tecla_txt)[0] + 9
    h = 13
    r = pygame.Rect(x, y, w, h)
    pygame.draw.rect(tela, CONTORNO, r.move(0, 1), border_radius=4)
    cor_corpo = OURO_CLARO if ativa else OURO
    pygame.draw.rect(tela, cor_corpo, r, border_radius=4)
    clara = (255, 232, 170) if ativa else OURO_CLARO
    pygame.draw.line(tela, clara, (r.left + 2, r.top), (r.right - 3, r.top), 1)
    pygame.draw.rect(tela, CONTORNO, r, width=1, border_radius=4)
    img = _render(fonte, tecla_txt, (46, 32, 16))
    tela.blit(img, (r.centerx - img.get_width() // 2,
                    r.centery - img.get_height() // 2))
    return r


def legenda_teclas(tela, fonte, itens, cx, y):
    """Linha de '[tecla] acao' centralizada. itens = [(tecla, acao), ...]"""
    larguras = []
    for tecla_txt, acao in itens:
        larguras.append(fonte.size(tecla_txt)[0] + 9 + 4 + fonte.size(acao)[0] + 14)
    x = cx - sum(larguras) // 2
    for (tecla_txt, acao), w in zip(itens, larguras):
        r = keycap(tela, fonte, tecla_txt, x, y)
        texto(tela, fonte, acao, r.right + 4, y + 1, config.CINZA)
        x += w


def barra(tela, rect, frac, cor, cor_fundo=(24, 20, 26)):
    """Barra de progresso com trilho escuro, recheio colorido e pinos de ouro
    nas pontas (igual aos slides da referencia)."""
    frac = max(0.0, min(1.0, frac))
    pygame.draw.rect(tela, CONTORNO, rect.inflate(2, 2), border_radius=5)
    pygame.draw.rect(tela, cor_fundo, rect, border_radius=4)
    cheio = int((rect.width - 2) * frac)
    if cheio > 1:
        interno = pygame.Rect(rect.left + 1, rect.top + 1, cheio, rect.height - 2)
        pygame.draw.rect(tela, cor, interno, border_radius=4)
        clara = (min(255, cor[0] + 55), min(255, cor[1] + 55), min(255, cor[2] + 55))
        pygame.draw.line(tela, clara, (interno.left + 2, interno.top),
                         (interno.right - 3, interno.top), 1)
    for px in (rect.left - 1, rect.right + 1):
        pygame.draw.circle(tela, CONTORNO, (px, rect.centery), 4)
        pygame.draw.circle(tela, OURO, (px, rect.centery), 3)
        tela.set_at((px - 1, rect.centery - 1), OURO_CLARO)


def cursor_selecao(tela, x, y):
    """Setinha de selecao que respira (pra listas de loja etc.)."""
    desloc = int((math.sin(pygame.time.get_ticks() * 0.008) + 1) * 1.5)
    pygame.draw.polygon(tela, OURO_CLARO,
                        [(x + desloc, y), (x + desloc, y + 6), (x + 4 + desloc, y + 3)])


def separador(tela, x1, x2, y):
    """Linha divisoria dourada com sombrinha."""
    pygame.draw.line(tela, OURO_ESCURO, (x1, y), (x2, y), 1)
    pygame.draw.line(tela, (0, 0, 0, 60), (x1, y + 1), (x2, y + 1), 1)
    for px in (x1, x2):
        pygame.draw.circle(tela, OURO, (px, y), 2)


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
