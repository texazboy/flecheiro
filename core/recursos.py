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
                     bases usadas: jogador, inimigo, voador
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
            img = self._tentar_png(chave) or self._placeholder_item(material)
            self._cache_img[chave] = self._escalar_para_altura(img, 12)
        return self._cache_img[chave]

    def sprite_npc(self, tipo, cor):
        chave = "npc_" + tipo
        if chave not in self._cache_img:
            img = self._tentar_png(chave) or self._placeholder_npc(tipo, cor)
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
        pygame.draw.rect(s, config.VERMELHO, (0, 0, 1, 4))
        pygame.draw.rect(s, config.BRANCO, (1, 0, 1, 4))
        return s

    def _placeholder_item(self, material):
        """Cada material tem uma forma propria, pra dar pra reconhecer de longe."""
        s = self._nova(12, 12)
        ch = material.chave
        if ch == "madeira":
            # tora deitada com aneis
            pygame.draw.rect(s, config.MARROM, (1, 4, 10, 5))
            pygame.draw.rect(s, config.MARROM_CLARO, (0, 4, 2, 5))
            pygame.draw.rect(s, (84, 58, 38), (10, 4, 2, 5))
            pygame.draw.line(s, (84, 58, 38), (4, 5), (4, 8), 1)
            pygame.draw.line(s, (84, 58, 38), (7, 5), (7, 8), 1)
        elif ch == "ferro":
            # lingote
            pygame.draw.polygon(s, config.CINZA, [(2, 9), (4, 4), (10, 4), (12, 9)])
            pygame.draw.line(s, config.BRANCO, (4, 5), (9, 5), 1)
            pygame.draw.line(s, (70, 74, 86), (2, 9), (12, 9), 1)
        elif ch == "couro":
            # pele dobrada com costura
            pygame.draw.rect(s, config.MARROM_CLARO, (1, 4, 10, 6))
            pygame.draw.rect(s, config.MARROM, (1, 4, 10, 2))
            for px in (3, 6, 9):
                pygame.draw.rect(s, (84, 58, 38), (px, 8, 1, 1))
        elif ch == "pena":
            # pena na diagonal
            pygame.draw.polygon(s, config.BRANCO, [(2, 10), (8, 2), (10, 4), (4, 11)])
            pygame.draw.line(s, config.CINZA, (3, 10), (9, 3), 1)
        elif ch == "cristal":
            # gema lapidada
            pygame.draw.polygon(s, config.ROXO, [(6, 0), (11, 5), (9, 11), (3, 11), (1, 5)])
            pygame.draw.line(s, (200, 170, 235), (6, 0), (6, 11), 1)
            pygame.draw.line(s, (200, 170, 235), (1, 5), (11, 5), 1)
            pygame.draw.rect(s, config.BRANCO, (4, 2, 2, 2))
        else:
            pygame.draw.polygon(s, material.cor, [(6, 0), (12, 6), (6, 12), (0, 6)])
            pygame.draw.polygon(s, config.BRANCO, [(6, 0), (12, 6), (6, 12), (0, 6)], 1)
        return s

    def _placeholder_npc(self, tipo, cor):
        s = self._nova(16, 24)
        pele = (224, 178, 140)
        pygame.draw.rect(s, pele, (5, 1, 6, 6))            # cabeca
        pygame.draw.rect(s, cor, (4, 7, 8, 11))            # roupa
        pygame.draw.rect(s, (60, 50, 40), (4, 18, 3, 6))   # pernas
        pygame.draw.rect(s, (60, 50, 40), (9, 18, 3, 6))
        if tipo == "ferreiro":
            pygame.draw.rect(s, (70, 70, 78), (5, 10, 6, 7))     # avental
            pygame.draw.rect(s, config.MARROM, (13, 8, 1, 7))    # cabo do martelo
            pygame.draw.rect(s, config.CINZA, (12, 6, 3, 3))     # cabeca do martelo
        elif tipo == "lojista":
            pygame.draw.rect(s, config.MARROM, (3, 1, 10, 1))    # aba do chapeu
            pygame.draw.rect(s, config.MARROM, (5, 0, 6, 2))     # copa
        elif tipo == "aldeao":
            pygame.draw.rect(s, config.BRANCO, (5, 6, 6, 2))     # barba
            pygame.draw.rect(s, config.MARROM, (14, 12, 1, 12))  # bengala
        return s

    # --- animacoes placeholder ---
    def _placeholder_anim(self, base, estado):
        if base == "jogador":
            return self._frames_jogador(estado)
        if base == "inimigo":
            return self._frames_inimigo(estado)
        if base == "voador":
            return self._frames_voador()
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
                base_img = corpo()
                pygame.draw.rect(base_img, capuz, (4, 17, 3, 7))
                pygame.draw.rect(base_img, capuz, (9, 17, 3, 7))
                pygame.draw.rect(base_img, pele, (11, 9, 3, 2))
                s = self._nova(16, 24)
                s.blit(base_img, (0, dy))
                quadros.append(s)
        return quadros

    def _frames_inimigo(self, estado):
        """Slime: gota arredondada com contorno, brilho e carinha."""
        corpo = (198, 78, 70)
        escuro = (118, 38, 38)
        quadros = []
        for sq in (0, 1, 0, -1):  # leve "squash" pra parecer vivo
            s = self._nova(16, 18)
            alt = 13 - sq
            topo = 5 + sq
            corpo_rect = pygame.Rect(1, topo, 14, alt)
            pygame.draw.ellipse(s, escuro, corpo_rect)                      # contorno
            pygame.draw.ellipse(s, corpo, corpo_rect.inflate(-2, -2))
            pygame.draw.ellipse(s, (224, 120, 104),
                                (corpo_rect.left + 2, corpo_rect.top + 1, 6, 4))  # brilho
            olho_y = topo + alt // 2 - 2
            pygame.draw.rect(s, config.BRANCO, (5, olho_y, 2, 3))
            pygame.draw.rect(s, config.BRANCO, (10, olho_y, 2, 3))
            pygame.draw.rect(s, config.PRETO, (5, olho_y + 1, 1, 1))
            pygame.draw.rect(s, config.PRETO, (10, olho_y + 1, 1, 1))
            pygame.draw.line(s, escuro, (7, olho_y + 4), (9, olho_y + 4), 1)  # boca
            quadros.append(s)
        return quadros

    def _frames_voador(self):
        """Morcego: corpo redondo, orelhinhas e asas batendo (2 quadros)."""
        quadros = []
        corpo_cor = (118, 86, 150)
        asa_cor = (82, 60, 108)
        contorno = (44, 30, 60)
        for asas_cima in (True, False):
            s = self._nova(16, 12)
            if asas_cima:
                asas = [[(0, 1), (6, 6), (3, 8)], [(16, 1), (10, 6), (13, 8)]]
            else:
                asas = [[(0, 10), (6, 5), (3, 4)], [(16, 10), (10, 5), (13, 4)]]
            for poly in asas:
                pygame.draw.polygon(s, asa_cor, poly)
                pygame.draw.polygon(s, contorno, poly, 1)
            pygame.draw.ellipse(s, contorno, (4, 2, 8, 9))     # contorno do corpo
            pygame.draw.ellipse(s, corpo_cor, (5, 3, 6, 7))
            pygame.draw.polygon(s, corpo_cor, [(5, 4), (6, 1), (7, 4)])   # orelha
            pygame.draw.polygon(s, corpo_cor, [(9, 4), (10, 1), (11, 4)])
            pygame.draw.rect(s, config.BRANCO, (6, 5, 1, 1))
            pygame.draw.rect(s, config.BRANCO, (9, 5, 1, 1))
            quadros.append(s)
        return quadros

    # --- coisas do mundo: bau, moeda e placa ---
    def sprite_bau(self, aberto):
        chave = "bau_aberto" if aberto else "bau_fechado"
        if chave not in self._cache_img:
            img = self._tentar_png(chave) or self._placeholder_bau(aberto)
            self._cache_img[chave] = self._escalar_para_altura(img, 13)
        return self._cache_img[chave]

    def _placeholder_bau(self, aberto):
        s = self._nova(16, 13)
        madeira = (134, 92, 52)
        escuro = (74, 48, 28)
        ouro = (224, 178, 80)
        if aberto:
            pygame.draw.rect(s, escuro, (1, 0, 14, 4))           # tampa levantada
            pygame.draw.rect(s, madeira, (2, 0, 12, 3))
            pygame.draw.rect(s, (24, 18, 14), (2, 5, 12, 3))     # interior escuro
            pygame.draw.rect(s, ouro, (4, 5, 2, 2))              # tesouro brilhando
            pygame.draw.rect(s, ouro, (9, 6, 2, 2))
            pygame.draw.rect(s, escuro, (1, 4, 14, 9), 1)
            pygame.draw.rect(s, madeira, (2, 8, 12, 4))
        else:
            pygame.draw.rect(s, escuro, (1, 2, 14, 11))          # contorno
            pygame.draw.rect(s, madeira, (2, 3, 12, 9))
            pygame.draw.rect(s, escuro, (2, 6, 12, 1))           # vinco da tampa
            pygame.draw.rect(s, ouro, (7, 5, 2, 4))              # fecho
            pygame.draw.rect(s, (160, 120, 70), (2, 3, 12, 1))   # luz na tampa
        return s

    def sprite_moeda(self):
        if "moeda" not in self._cache_img:
            img = self._tentar_png("moeda") or self._placeholder_moeda()
            self._cache_img["moeda"] = self._escalar_para_altura(img, 7)
        return self._cache_img["moeda"]

    def _placeholder_moeda(self):
        s = self._nova(7, 7)
        pygame.draw.circle(s, (150, 110, 40), (3, 3), 3)
        pygame.draw.circle(s, config.AMARELO, (3, 3), 2)
        s.set_at((2, 2), (255, 240, 180))
        return s

    def sprite_placa(self):
        if "placa" not in self._cache_img:
            img = self._tentar_png("placa") or self._placeholder_placa()
            self._cache_img["placa"] = self._escalar_para_altura(img, 16)
        return self._cache_img["placa"]

    def _placeholder_placa(self):
        s = self._nova(16, 16)
        madeira = (134, 92, 52)
        escuro = (74, 48, 28)
        pygame.draw.rect(s, escuro, (7, 8, 2, 8))                # poste
        pygame.draw.rect(s, escuro, (1, 1, 14, 8))               # contorno da tabua
        pygame.draw.rect(s, madeira, (2, 2, 12, 6))
        pygame.draw.line(s, escuro, (4, 4), (11, 4), 1)          # "escrita"
        pygame.draw.line(s, escuro, (4, 6), (9, 6), 1)
        return s

    # --- tiles placeholder ---
    def _placeholder_tile_terra(self):
        s = pygame.Surface((16, 16))
        s.fill((96, 68, 46))
        # salpicos em dois tons + uma pedrinha clara, pra dar textura
        for px, py in [(3, 4), (10, 7), (6, 11), (13, 13), (1, 9)]:
            pygame.draw.rect(s, (78, 54, 36), (px, py, 2, 2))
        for px, py in [(8, 2), (2, 14), (12, 10)]:
            pygame.draw.rect(s, (110, 80, 56), (px, py, 1, 1))
        pygame.draw.rect(s, (122, 96, 74), (5, 7, 2, 1))
        return s

    def _placeholder_tile_grama(self):
        s = self._placeholder_tile_terra().copy()
        pygame.draw.rect(s, (50, 96, 60), (0, 3, 16, 3))         # transicao escura
        pygame.draw.rect(s, config.VERDE_ESCURO, (0, 1, 16, 3))
        pygame.draw.rect(s, config.VERDE, (0, 0, 16, 2))
        pygame.draw.rect(s, (138, 208, 130), (0, 0, 16, 1))      # fio de luz no topo
        for px in (2, 7, 12):
            pygame.draw.rect(s, config.VERDE, (px, 2, 1, 3))
        for px in (5, 10, 14):
            s.set_at((px, 1), (138, 208, 130))
        return s

    def _placeholder_tile_plataforma(self):
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.rect(s, config.MARROM_CLARO, (0, 0, 16, 6))
        pygame.draw.rect(s, config.MARROM, (0, 0, 16, 6), 1)
        pygame.draw.line(s, config.MARROM, (8, 1), (8, 5), 1)
        return s
