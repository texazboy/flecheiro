# -*- coding: utf-8 -*-
"""
Importador de sprites: pega os pacotes baixados (gratis) e copia tudo pra
assets/ com os nomes que o jogo espera. Um comando por pacote:

  python assets/importar_sprites.py huntress "C:\\...\\Huntress"
      heroi arqueira de verdade (LuizMelo, CC0). Recorta a borda vazia dos
      quadros automaticamente e gera jogador_parado/andar/pulo/atirar.

  python assets/importar_sprites.py pa1 "C:\\...\\Pixel Adventure 1"
      heroi alternativo (Ninja Frog e cia, Pixel Frog, CC0).

  python assets/importar_sprites.py pa2 "C:\\...\\Pixel Adventure 2"
      inimigos: Slime -> terrestre, Bat -> voador (espelhados pra direita).

  python assets/importar_sprites.py tesouro "C:\\...\\Treasure Hunters"
      bau fechado/aberto e moeda (Pixel Frog, CC0).

Fundo em camadas (vnitti etc.): nao precisa de comando - renomeie as camadas
pra fundo1.png, fundo2.png, fundo3.png (da mais distante pra mais proxima).
Props (Cainos etc.): renomeie pra casa.png, poste.png, arvore.png, barril.png,
caixote.png, placa.png. O jogo pega tudo sozinho.
"""

import os
import re
import sys
import glob
import shutil

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

PASTA_ASSETS = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------------ ajudantes
def achar(raiz, *partes):
    achados = glob.glob(os.path.join(raiz, "**", *partes), recursive=True)
    return sorted(achados)[0] if achados else None


def fatiar(sheet, larg_quadro):
    alt = sheet.get_height()
    n = max(1, sheet.get_width() // larg_quadro)
    return [sheet.subsurface((i * larg_quadro, 0, larg_quadro, alt)).copy()
            for i in range(n)]


def largura_do_nome(caminho, sheet):
    """Pixel Frog poe o tamanho no nome: 'Run (32x32).png'. Sem isso, assume
    quadros quadrados."""
    m = re.search(r"\((\d+)x(\d+)\)", os.path.basename(caminho))
    if m:
        return int(m.group(1))
    return sheet.get_height()


def salvar_tira(quadros, destino, espelhar=False):
    larg = quadros[0].get_width()
    alt = quadros[0].get_height()
    tira = pygame.Surface((larg * len(quadros), alt), pygame.SRCALPHA)
    for i, q in enumerate(quadros):
        if espelhar:
            q = pygame.transform.flip(q, True, False)
        tira.blit(q, (i * larg, 0))
    nome = f"{destino}_{len(quadros)}.png"
    pygame.image.save(tira, os.path.join(PASTA_ASSETS, nome))
    print(f"  OK  {nome}")


def importar_tira(origem, destino, espelhar=False):
    if origem is None:
        print(f"  --  nao achei a animacao de {destino} (fica o placeholder)")
        return False
    sheet = pygame.image.load(origem).convert_alpha()
    quadros = fatiar(sheet, largura_do_nome(origem, sheet))
    salvar_tira(quadros, destino, espelhar)
    return True


def recortar_quadros(quadros):
    """Tira a borda transparente comum a todos os quadros (mantem o alinhamento).
    Essencial pros personagens do LuizMelo, que vem com muito espaco vazio."""
    uniao = None
    for q in quadros:
        r = q.get_bounding_rect()
        uniao = r if uniao is None else uniao.union(r)
    if uniao is None or uniao.width == 0:
        return quadros
    return [q.subsurface(uniao).copy() for q in quadros]


# ------------------------------------------------------------------ pacotes
def pacote_huntress(raiz):
    """Importante: TODAS as animacoes sao recortadas pela MESMA caixa (uniao
    dos corpos em idle/run/jump). Se cada uma tiver caixa propria, a escala da
    personagem muda a cada troca de estado e ela parece vibrar no jogo. O
    Attack1 usa a mesma caixa - a lanca arremessada e cortada de proposito,
    porque o projetil de verdade quem desenha e o jogo."""
    print("Huntress (LuizMelo, CC0) -> heroi arqueira")
    mapa = [("Idle*.png", "jogador_parado"), ("Run*.png", "jogador_andar"),
            ("Jump*.png", "jogador_pulo"), ("Attack1*.png", "jogador_atirar")]
    anims = {}
    for padrao, destino in mapa:
        origem = achar(raiz, padrao)
        if origem is None:
            print(f"  --  nao achei {padrao}")
            continue
        sheet = pygame.image.load(origem).convert_alpha()
        anims[destino] = fatiar(sheet, largura_do_nome(origem, sheet))

    caixa = None
    for destino in ("jogador_parado", "jogador_andar", "jogador_pulo"):
        for q in anims.get(destino, []):
            r = q.get_bounding_rect()
            caixa = r if caixa is None else caixa.union(r)
    if caixa is None:
        print("  --  nenhuma animacao encontrada")
        return

    for destino, quadros in anims.items():
        cortados = [q.subsurface(caixa).copy() for q in quadros]
        salvar_tira(cortados, destino)

    # limpa os nomes antigos sem contagem, se existirem (senao tem dois jogadores)
    for velho in ("jogador_parado.png", "jogador_andar.png",
                  "jogador_pulo.png", "jogador_atirar.png"):
        caminho = os.path.join(PASTA_ASSETS, velho)
        if os.path.exists(caminho):
            os.remove(caminho)
            print(f"  (removi o antigo {velho})")


def pacote_pa1(raiz, personagem="Ninja Frog"):
    print(f"Pixel Adventure 1 (CC0) -> heroi {personagem}")
    mapa = [("Idle*.png", "jogador_parado"), ("Run*.png", "jogador_andar"),
            ("Jump*.png", "jogador_pulo"), ("Idle*.png", "jogador_atirar")]
    for padrao, destino in mapa:
        importar_tira(achar(raiz, "Main Characters", personagem, padrao), destino)


def pacote_pa2(raiz):
    print("Pixel Adventure 2 (CC0) -> inimigos")
    origem = achar(raiz, "Enemies", "Slime", "Idle-Run*.png") or \
        achar(raiz, "Enemies", "Slime", "*.png")
    importar_tira(origem, "inimigo_andar", espelhar=True)
    origem = achar(raiz, "Enemies", "Bat", "Flying*.png") or \
        achar(raiz, "Enemies", "Bat", "*.png")
    importar_tira(origem, "voador_voar", espelhar=True)


def pacote_monstros(raiz):
    """Monsters Creatures Fantasy 2: Slime -> inimigo, Bat -> voador.
    Aqui o recorte por animacao e seguro: cada bicho tem UMA animacao so,
    entao nao existe troca de estado pra escala variar."""
    print("Monsters Creatures Fantasy 2 -> inimigos")
    origem = achar(raiz, "Slime", "walk.png")
    if origem:
        sheet = pygame.image.load(origem).convert_alpha()
        quadros = recortar_quadros(fatiar(sheet, largura_do_nome(origem, sheet)))
        salvar_tira(quadros, "inimigo_andar", espelhar=True)
    origem = achar(raiz, "Bat", "fly.png")
    if origem:
        sheet = pygame.image.load(origem).convert_alpha()
        quadros = recortar_quadros(fatiar(sheet, largura_do_nome(origem, sheet)))
        salvar_tira(quadros, "voador_voar", espelhar=True)


def pacote_tesouro(raiz):
    print("Treasure Hunters (Pixel Frog, CC0) -> bau e moeda")
    origem = achar(raiz, "*Chest*.png")
    if origem:
        sheet = pygame.image.load(origem).convert_alpha()
        quadros = fatiar(sheet, largura_do_nome(origem, sheet))
        pygame.image.save(quadros[0], os.path.join(PASTA_ASSETS, "bau_fechado.png"))
        pygame.image.save(quadros[-1], os.path.join(PASTA_ASSETS, "bau_aberto.png"))
        print("  OK  bau_fechado.png / bau_aberto.png")
    else:
        print("  --  nao achei *Chest*.png")
    origem = achar(raiz, "*Gold Coin*.png") or achar(raiz, "*Coin*.png")
    if origem:
        sheet = pygame.image.load(origem).convert_alpha()
        quadros = fatiar(sheet, largura_do_nome(origem, sheet))
        pygame.image.save(quadros[0], os.path.join(PASTA_ASSETS, "moeda.png"))
        print("  OK  moeda.png")
    else:
        print("  --  nao achei *Coin*.png")


PACOTES = {"huntress": pacote_huntress, "pa1": pacote_pa1, "pa2": pacote_pa2,
           "monstros": pacote_monstros, "tesouro": pacote_tesouro}


def main():
    if len(sys.argv) < 3 or sys.argv[1].lower() not in PACOTES:
        print(__doc__)
        return
    raiz = sys.argv[2]
    if not os.path.isdir(raiz):
        print(f"ERRO: pasta nao encontrada: {raiz}")
        return
    pygame.init()
    pygame.display.set_mode((1, 1))
    PACOTES[sys.argv[1].lower()](raiz)
    pygame.quit()
    print("\nPronto! Rode: python main.py")


if __name__ == "__main__":
    main()
