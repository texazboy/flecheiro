# -*- coding: utf-8 -*-
"""
Configuracoes globais do jogo "Flecheiro".

Mantemos tudo num lugar so pra ficar facil ajustar resolucao, fisica e cores
sem sair cacando numero magico no meio do codigo. A resolucao interna e baixa
(estilo pixel art) e depois e ampliada pela ESCALA na hora de jogar na tela.
"""

# --- Janela / resolucao ---
# Render interno em baixa resolucao e depois ampliado -> visual pixelado.
LARGURA = 480
ALTURA = 270
ESCALA = 3                       # janela final = 1440 x 810
LARGURA_JANELA = LARGURA * ESCALA
ALTURA_JANELA = ALTURA * ESCALA

TITULO = "Flecheiro - Algoritmos em Acao"
FPS = 60

# --- Fisica do mundo ---
GRAVIDADE = 0.45
VEL_MAX_QUEDA = 9.0
VEL_ANDAR = 2.2
FORCA_PULO = 8.5

# --- Flecha ---
FORCA_FLECHA = 9.0               # velocidade inicial do disparo
GRAVIDADE_FLECHA = 0.22
MAX_FLECHAS_FINCADAS = 12        # limite de plataformas-flecha simultaneas
COMP_FLECHA = 14                 # comprimento visual da flecha

# --- Cores (paleta simples) ---
PRETO = (18, 18, 24)
BRANCO = (240, 240, 245)
CINZA = (120, 124, 138)
CINZA_ESCURO = (54, 58, 74)
VERDE = (96, 178, 102)
VERDE_ESCURO = (58, 110, 70)
MARROM = (120, 86, 56)
MARROM_CLARO = (164, 122, 78)
AZUL_CEU = (104, 156, 204)
AZUL_NOITE = (52, 64, 102)
VERMELHO = (196, 76, 72)
AMARELO = (232, 196, 92)
ROXO = (138, 92, 168)
LARANJA = (220, 138, 64)

# Cor usada como "transparencia" nos placeholders gerados em codigo.
COR_CHAVE = (255, 0, 255)
