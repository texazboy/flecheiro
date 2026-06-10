# -*- coding: utf-8 -*-
"""
Importador de sprites do pacote "Pixel Adventure" (Pixel Frog, CC0).

O que ele faz: copia o heroi e um inimigo do pacote para a pasta assets/ com os
nomes que o jogo espera. Os quadros do Pixel Adventure sao 32x32 QUADRADOS, entao
o jogo deduz a quantidade de quadros sozinho (nao precisa por numero no nome).

COMO USAR
---------
1) Baixe e extraia o pacote (gratis, CC0):
   https://pixelfrog-assets.itch.io/pixel-adventure-1
2) Rode apontando para a pasta extraida:
   python assets/importar_sprites.py "C:\\caminho\\para\\Pixel Adventure 1"
3) Rode o jogo:
   python main.py

Quer outro personagem/inimigo? Troque as constantes PERSONAGEM / INIMIGO abaixo
(nomes das pastas dentro do pacote, ex.: "Mask Dude", "Pink Man", "Virtual Guy"
para o heroi; "Mushroom", "Chicken", "Slime", etc. para o inimigo). Se o inimigo
escolhido nao existir, o script pega o primeiro inimigo que encontrar.
"""

import os
import sys
import glob
import shutil

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

# --- escolha do heroi e do inimigo (nomes de pasta dentro do pacote) ---
PERSONAGEM = "Ninja Frog"
INIMIGO = "Mushroom"

# Os inimigos do Pixel Adventure costumam olhar para a ESQUERDA; o jogo espera
# arte virada para a DIREITA. Se o inimigo aparecer invertido no jogo, troque
# este valor para False.
ESPELHAR_INIMIGO = True

PASTA_ASSETS = os.path.dirname(os.path.abspath(__file__))


def achar(raiz, *partes):
    """Procura recursivamente um arquivo (tolera nomes com espacos/parenteses)."""
    achados = glob.glob(os.path.join(raiz, "**", *partes), recursive=True)
    return achados[0] if achados else None


def copiar(origem, destino):
    shutil.copyfile(origem, destino)
    print(f"  OK  {os.path.basename(destino)}  <-  {os.path.basename(origem)}")


def copiar_espelhado(origem, destino):
    """Copia uma tira horizontal espelhando CADA quadro (mantendo a ordem)."""
    sheet = pygame.image.load(origem)
    h = sheet.get_height()
    n = max(1, sheet.get_width() // h)  # quadros quadrados
    nova = pygame.Surface((sheet.get_width(), h), pygame.SRCALPHA)
    for i in range(n):
        quadro = sheet.subsurface((i * h, 0, h, h))
        nova.blit(pygame.transform.flip(quadro, True, False), (i * h, 0))
    pygame.image.save(nova, destino)
    print(f"  OK  {os.path.basename(destino)}  <-  {os.path.basename(origem)}  (espelhado)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("ERRO: informe a pasta do pacote. Ex.:")
        print('  python assets/importar_sprites.py "C:\\...\\Pixel Adventure 1"')
        return
    raiz = sys.argv[1]
    if not os.path.isdir(raiz):
        print(f"ERRO: pasta nao encontrada: {raiz}")
        return

    pygame.init()
    pygame.display.set_mode((1, 1))

    # --- heroi (ja vem virado para a direita) ---
    print(f"Heroi: {PERSONAGEM}")
    mapa_heroi = {
        "jogador_parado.png": ("Main Characters", PERSONAGEM, "Idle*.png"),
        "jogador_andar.png":  ("Main Characters", PERSONAGEM, "Run*.png"),
        "jogador_pulo.png":   ("Main Characters", PERSONAGEM, "Jump*.png"),
        "jogador_atirar.png": ("Main Characters", PERSONAGEM, "Idle*.png"),  # sem "atirar" no pacote
    }
    for destino, partes in mapa_heroi.items():
        origem = achar(raiz, *partes)
        if origem:
            copiar(origem, os.path.join(PASTA_ASSETS, destino))
        else:
            print(f"  --  nao achei {partes[-1]} para {PERSONAGEM} (vai usar placeholder)")

    # --- inimigo (com fallback: se nao achar o escolhido, pega qualquer um) ---
    print(f"Inimigo: {INIMIGO}")
    origem = achar(raiz, "Enemies", INIMIGO, "Run*.png") or achar(raiz, "Enemies", INIMIGO, "Idle*.png")
    if not origem:
        alt = (glob.glob(os.path.join(raiz, "**", "Enemies", "*", "Run*.png"), recursive=True)
               or glob.glob(os.path.join(raiz, "**", "Enemies", "*", "Idle*.png"), recursive=True))
        if alt:
            origem = alt[0]
            print(f"  (nao achei '{INIMIGO}'; usando '{os.path.basename(os.path.dirname(origem))}')")

    destino = os.path.join(PASTA_ASSETS, "inimigo_andar.png")
    if origem:
        if ESPELHAR_INIMIGO:
            copiar_espelhado(origem, destino)
        else:
            copiar(origem, destino)
    else:
        print("  --  nenhum inimigo encontrado no pacote (vai usar placeholder)")

    pygame.quit()
    print("\nPronto! Agora rode:  python main.py")
    print("Dica: se o heroi ficar pequeno, aumente ALTURA_DESENHO em entidades/jogador.py")


if __name__ == "__main__":
    main()
