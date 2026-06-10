# -*- coding: utf-8 -*-
"""
Carregamento de imagens, animacoes, tiles e fontes.

Filosofia: se o arquivo existir em assets/, usa ele; se nao, gera um placeholder
em codigo. Assim o jogo roda igual antes e depois de colocar a arte. Os sprites
sao escalados automaticamente para o tamanho logico esperado, entao a arte de
origem nao precisa ter o pixel exato (ver assets/LEIA-ME.txt).

Convencoes de nome em assets/:
  - sprite simples : flecha.png, item_madeira.png, npc_ferreiro.png ...
  - animacao       : <base>_<estado>_<qtd>.png  (tira horizontal com <qtd> quadros)
                     ex.: jogador_andar_6.png  (6 quadros lado a lado)
                     ou   <base>_<estado>.png   (quadros QUADRADOS, qtd deduzida)
  - tiles          : tile_grama.png, tile_terra.png, tile_plataforma.png (16x16)
  - fundo          : fundo.png (camada distante, opcional)
"""

import os
import glob

import pygame

import config
from core.animacao import Animacao, fatiar_tira


class Recursos:
    def __init__(self, pasta_assets):
        self.pasta = pasta_assets
        self._cache_img = {}
        self._cache_fonte = {}
        self._cache_frames = {}
        self._cache_tile = {}

    # ------------------------------------------------------------------ fontes
    def fonte(self, tamanho):
        if tamanho not in self._cache_fonte:
            self._cache_fonte[tamanho] = pygame.font.Font(None, tamanho)
        return self._cache_fonte[tamanho]

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _nova(largura, altura):
        return pygame.Surface((largura, altura), pygame.SRCALPHA)

    def _tentar_png(self, nome):
        caminho = os.path.join(self.pasta, nome + ".png")
        if os.path.exists(caminho):
            try:
                return pygame.image.load(caminho).convert_alpha()
            except pygame.error:
                return None
        return None

    @staticmethod
    def _escalar_para_altura(imagem, altura):
        """Escala mantendo a proporcao para a altura logica desejada (pixelado)."""
        if imagem.get_height() == altura:
            return imagem
        largura = max(1, round(imagem.get_width() * altura / imagem.get_height()))
        return pygame.transform.scale(imagem, (largura, altura))

    # ------------------------------------------------------------ sprites simples
    def sprite_flecha(self):
        if "flecha" not in self._cache_img:
            img = self._tentar_png("flecha") or self._placeholder_flecha()
            self._cache_img["flecha"] = self._escalar_para_altura(img, 4)
        return self._cache_img["flecha"]

    def sprite_item(self, material):
        chave = "item_" + material.chave
        if chave not in self._cache_img:
            img = self._tentar_png(chave) or self._placeholder_item(material.cor)
            self._cache_img[chave] = self._escalar_para_altura(img, 12)
        return self._cache_img[chave]

    def sprite_npc(self, tipo, cor):
        chave = "npc_" + tipo
        if chave not in self._cache_img:
            img = self._tentar_png(chave) or self._placeholder_npc(cor)
            self._cache_img[chave] = self._escalar_para_altura(img, 24)
        return self._cache_img[chave]

    # ------------------------------------------------------------ animacoes
    def animacao(self, base, estado, altura, fps=8, repetir=True):
        """Cria uma Animacao nova (estado proprio) reusando os quadros em cache."""
        return Animacao(self._quadros(base, estado, altura), fps=fps, repetir=repetir)

    def _quadros(self, base, estado, altura):
        chave = (base, estado, altura)
        if chave not in self._cache_frames:
            self._cache_frames[chave] = [self._escalar_para_altura(q, altura)
                                         for q in self._carregar_quadros(base, estado)]
        return self._cache_frames[chave]

    def _carregar_quadros(self, base, estado):
        # 1) tira com a quantidade no nome: base_estado_N.png
        achados = glob.glob(os.path.join(self.pasta, f"{base}_{estado}_*.png"))
        if achados:
            sheet = pygame.image.load(achados[0]).convert_alpha()
            nome = os.path.splitext(os.path.basename(achados[0]))[0]
            try:
                qtd = int(nome.rsplit("_", 1)[1])
            except ValueError:
                qtd = 1
            return fatiar_tira(sheet, qtd)
        # 2) tira com quadros quadrados: base_estado.png
        img = self._tentar_png(f"{base}_{estado}")
        if img is not None:
            qtd = max(1, img.get_width() // img.get_height())
            return fatiar_tira(img, qtd)
        # 3) placeholder animado
        return self._placeholder_anim(base, estado)

    # ------------------------------------------------------------ tiles
    def tile_grama(self):
        return self._tile("tile_grama", self._placeholder_tile_grama)

    def tile_terra(self):
        return self._tile("tile_terra", self._placeholder_tile_terra)

    def tile_plataforma(self):
        return self._tile("tile_plataforma", self._placeholder_tile_plataforma)

    def _tile(self, nome, gerador):
        if nome not in self._cache_tile:
            img = self._tentar_png(nome)
            if img is not None:
                img = pygame.transform.scale(img, (16, 16))
            else:
                img = gerador()
            self._cache_tile[nome] = img
        return self._cache_tile[nome]

    def fundo_img(self):
        if "fundo" not in self._cache_img:
            self._cache_img["fundo"] = self._tentar_png("fundo")  # pode ser None
        return self._cache_img["fundo"]

    # =================================================================
    # Geradores de placeholder (usados quando nao ha arte na pasta)
    # =================================================================
    def _placeholder_flecha(self):
        s = self._nova(config.COMP_FLECHA, 4)
        pygame.draw.rect(s, config.MARROM_CLARO, (0, 1, config.COMP_FLECHA - 3, 2))
        pygame.draw.polygon(s, config.CINZA, [(config.COMP_FLECHA - 4, 0),
                                              (config.COMP_FLECHA, 2),
                                              (config.COMP_FLECHA - 4, 4)])
        pygame.draw.rect(s, config.BRANCO, (0, 0, 2, 4))
        return s

    def _placeholder_item(self, cor):
        s = self._nova(12, 12)
        pygame.draw.polygon(s, cor, [(6, 0), (12, 6), (6, 12), (0, 6)])
        pygame.draw.polygon(s, config.BRANCO, [(6, 0), (12, 6), (6, 12), (0, 6)], 1)
        pygame.draw.rect(s, config.BRANCO, (5, 3, 2, 2))
        return s

    def _placeholder_npc(self, cor):
        s = self._nova(16, 24)
        pele = (224, 178, 140)
        pygame.draw.rect(s, pele, (5, 1, 6, 6))
        pygame.draw.rect(s, cor, (4, 7, 8, 11))
        pygame.draw.rect(s, (60, 50, 40), (4, 18, 3, 6))
        pygame.draw.rect(s, (60, 50, 40), (9, 18, 3, 6))
        return s

    # --- animacoes placeholder ---
    def _placeholder_anim(self, base, estado):
        if base == "jogador":
            return self._frames_jogador(estado)
        if base == "inimigo":
            return self._frames_inimigo(estado)
        return [self._nova(16, 16)]

    def _frames_jogador(self, estado):
        pele = (224, 178, 140)
        tunica = config.VERDE_ESCURO
        capuz = config.MARROM

        def corpo():
            s = self._nova(16, 24)
            pygame.draw.rect(s, capuz, (5, 0, 6, 2))      # capuz
            pygame.draw.rect(s, pele, (5, 2, 6, 5))       # cabeca
            pygame.draw.rect(s, tunica, (4, 7, 8, 10))    # tronco
            return s

        def pernas(s, a, b):
            pygame.draw.rect(s, capuz, (4 + a, 17, 3, 7 - abs(a)))
            pygame.draw.rect(s, capuz, (9 + b, 17, 3, 7 - abs(b)))

        quadros = []
        if estado == "andar":
            for a, b in [(0, 0), (2, -1), (0, 0), (-1, 2)]:
                s = corpo()
                pernas(s, a, b)
                pygame.draw.rect(s, pele, (11, 9, 4, 2))  # braco
                quadros.append(s)
        elif estado == "atirar":
            for ext in (5, 2):
                s = corpo()
                pernas(s, 0, 0)
                pygame.draw.rect(s, pele, (11, 8, ext, 2))                 # braco
                pygame.draw.line(s, capuz, (11 + ext, 5), (11 + ext, 12), 1)  # arco
                quadros.append(s)
        elif estado == "pulo":
            s = corpo()
            pygame.draw.rect(s, capuz, (5, 17, 3, 5))
            pygame.draw.rect(s, capuz, (9, 17, 3, 5))
            pygame.draw.rect(s, pele, (11, 7, 4, 2))
            quadros.append(s)
        else:  # parado
            for dy in (0, 1):
                base = corpo()
                pygame.draw.rect(base, capuz, (4, 17, 3, 7))
                pygame.draw.rect(base, capuz, (9, 17, 3, 7))
                pygame.draw.rect(base, pele, (11, 9, 3, 2))
                s = self._nova(16, 24)
                s.blit(base, (0, dy))
                quadros.append(s)
        return quadros

    def _frames_inimigo(self, estado):
        quadros = []
        for sq in (0, 1, 0, -1):  # leve "squash" pra parecer vivo
            s = self._nova(16, 18)
            altura = 12 - sq
            topo = 4 + sq
            pygame.draw.rect(s, config.VERMELHO, (2, topo, 12, altura))
            pygame.draw.rect(s, (120, 40, 40), (2, topo, 12, altura), 1)
            pygame.draw.rect(s, config.BRANCO, (5, topo + 3, 2, 2))
            pygame.draw.rect(s, config.BRANCO, (9, topo + 3, 2, 2))
            pygame.draw.rect(s, config.PRETO, (5, topo + 3, 1, 1))
            pygame.draw.rect(s, config.PRETO, (9, topo + 3, 1, 1))
            quadros.append(s)
        return quadros

    # --- tiles placeholder ---
    def _placeholder_tile_terra(self):
        s = pygame.Surface((16, 16))
        s.fill((96, 68, 46))
        for px, py in [(3, 4), (10, 7), (6, 11), (13, 13), (1, 9)]:
            pygame.draw.rect(s, (78, 54, 36), (px, py, 2, 2))
        return s

    def _placeholder_tile_grama(self):
        s = self._placeholder_tile_terra().copy()
        pygame.draw.rect(s, config.VERDE_ESCURO, (0, 0, 16, 5))
        pygame.draw.rect(s, config.VERDE, (0, 0, 16, 2))
        for px in (2, 7, 12):
            pygame.draw.rect(s, config.VERDE, (px, 2, 1, 2))
        return s

    def _placeholder_tile_plataforma(self):
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.rect(s, config.MARROM_CLARO, (0, 0, 16, 6))
        pygame.draw.rect(s, config.MARROM, (0, 0, 16, 6), 1)
        pygame.draw.line(s, config.MARROM, (8, 1), (8, 5), 1)
        return s
