# -*- coding: utf-8 -*-
"""
Loja do lojista.

Bem direta: vende os materiais coletados por ouro (cada um vale o seu 'valor') e
compra uma cura que recupera um coracao. Setas pra navegar, Enter pra vender.
"""

import pygame

import config
from core import som
from telas import comum

CUSTO_CURA = 6


class Loja:
    def __init__(self, mundo, recursos):
        self.mundo = mundo
        self.recursos = recursos
        self.fonte = recursos.fonte(20)
        self.fonte_p = recursos.fonte(15)
        self.selecao = 0
        self.mensagem = "Bem-vindo! O que vai querer hoje?"
        self._nasceu = pygame.time.get_ticks()

    def _itens(self):
        return self.mundo.inventario.listar()

    def tratar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return False
        if evento.key in (pygame.K_ESCAPE, pygame.K_q):
            return True

        itens = self._itens()
        if evento.key in (pygame.K_UP, pygame.K_w):
            self.selecao = max(0, self.selecao - 1)
        elif evento.key in (pygame.K_DOWN, pygame.K_s):
            self.selecao = min(max(0, len(itens) - 1), self.selecao + 1)
        elif evento.key in (pygame.K_RETURN, pygame.K_v):
            self._vender(itens)
        elif evento.key == pygame.K_c:
            self._comprar_cura()
        return False

    def _vender(self, itens):
        if not itens:
            self.mensagem = "Nao ha nada para vender."
            return
        self.selecao = min(self.selecao, len(itens) - 1)
        material, _ = itens[self.selecao]
        self.mundo.inventario.remover(material, 1)
        self.mundo.ouro += material.valor
        som.tocar("moeda")
        self.mensagem = f"Vendeu {material.nome} por {material.valor} de ouro."
        # ajusta selecao se o tipo acabou
        if self.selecao >= len(self._itens()):
            self.selecao = max(0, len(self._itens()) - 1)

    def _comprar_cura(self):
        if self.mundo.vida >= self.mundo.vida_max:
            self.mensagem = "Sua vida ja esta cheia."
        elif self.mundo.ouro < CUSTO_CURA:
            self.mensagem = f"Ouro insuficiente (precisa de {CUSTO_CURA})."
        else:
            self.mundo.ouro -= CUSTO_CURA
            self.mundo.vida += 1
            som.tocar("cura")
            self.mensagem = "Recuperou um coracao!"

    def desenhar(self, tela):
        comum.escurecer(tela, 175)
        desloc = int((1.0 - comum.surgimento(self._nasceu)) * 14)
        painel = pygame.Rect(28, 16 + desloc, config.LARGURA - 56, config.ALTURA - 32)
        comum.painel(tela, painel, cor_fundo=(26, 34, 48))

        comum.faixa_titulo(tela, self.fonte, "LOJA DA CILA", painel.centerx,
                           painel.top + 2, (150, 200, 240))

        # cabecalho: bolsa de ouro e oferta de cura
        pygame.draw.circle(tela, config.AMARELO, (painel.left + 18, painel.top + 33), 4)
        pygame.draw.circle(tela, (160, 130, 40), (painel.left + 18, painel.top + 33), 4, 1)
        comum.texto(tela, self.fonte_p, str(self.mundo.ouro), painel.left + 27,
                    painel.top + 28, config.AMARELO)
        r = comum.keycap(tela, self.fonte_p, "C", painel.right - 118, painel.top + 27)
        comum.texto(tela, self.fonte_p, f"cura ({CUSTO_CURA} ouro)", r.right + 4,
                    painel.top + 28, (255, 130, 130))

        comum.separador(tela, painel.left + 10, painel.right - 10, painel.top + 45)

        itens = self._itens()
        y = painel.top + 54
        if not itens:
            comum.texto(tela, self.fonte_p, "(sem materiais para vender)",
                        painel.centerx, painel.centery, config.CINZA, centro=True)
        else:
            for i, (material, qtd) in enumerate(itens):
                linha = pygame.Rect(painel.left + 10, y - 3, painel.width - 20, 20)
                if i == self.selecao:
                    s = pygame.Surface(linha.size, pygame.SRCALPHA)
                    s.fill((120, 170, 230, 38))
                    tela.blit(s, linha.topleft)
                    pygame.draw.rect(tela, (120, 170, 230), linha, 1)
                    comum.cursor_selecao(tela, linha.left + 4, y + 2)
                sprite = self.recursos.sprite_item(material)
                tela.blit(sprite, (linha.left + 14, y - 1))
                cor = config.BRANCO if i == self.selecao else config.CINZA
                comum.texto(tela, self.fonte_p, f"{material.nome} x{qtd}",
                            linha.left + 30, y, cor)
                comum.texto(tela, self.fonte_p, f"+{material.valor} ouro",
                            linha.right - 64, y, config.AMARELO)
                y += 21

        comum.texto(tela, self.fonte_p, self.mensagem, painel.centerx,
                    painel.bottom - 32, config.BRANCO, centro=True)
        comum.legenda_teclas(tela, self.fonte_p,
                             [("Enter", "vender"), ("C", "cura"), ("Q", "sair")],
                             painel.centerx, painel.bottom - 21)
