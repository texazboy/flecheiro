# -*- coding: utf-8 -*-
"""
O arqueiro controlado pelo jogador.

Movimento de plataforma 2D bem direto: gravidade + pulo + colisao AABB resolvida
eixo por eixo (primeiro horizontal, depois vertical). As plataformas "solidas"
(chao e paredes) bloqueiam dos dois lados; as plataformas de uma via (plataformas
flutuantes e as FLECHAS fincadas) so seguram o jogador por cima - e isso que
deixa o jogador subir escalando as proprias flechas.
"""

import math

import pygame

import config
from entidades.flecha import Flecha


class Jogador:
    ALTURA_DESENHO = 24  # altura do sprite desenhado (a hitbox e fixa, abaixo)

    def __init__(self, x, y, recursos):
        self.recursos = recursos
        # hitbox fixa: a fisica nao depende do tamanho da arte
        self.rect = pygame.Rect(x, y, 16, 24)
        self.vx = 0.0
        self.vy = 0.0
        self.no_chao = False
        self.virado_dir = True
        self.invul = 0.0          # invencibilidade temporaria apos tomar dano
        self.cooldown_tiro = 0.0
        # "coyote time" e "jump buffer": deixam o pulo mais gostoso de usar
        self.coyote = 0.0
        self.buffer_pulo = 0.0

        alt = self.ALTURA_DESENHO
        self.animacoes = {
            "parado": recursos.animacao("jogador", "parado", alt, fps=4),
            "andar": recursos.animacao("jogador", "andar", alt, fps=8),
            "atirar": recursos.animacao("jogador", "atirar", alt, fps=10, repetir=False),
            "pulo": recursos.animacao("jogador", "pulo", alt, fps=1),
        }
        self.estado_anim = "parado"

    # ------------------------------------------------------------- comandos
    def pular(self):
        # so registra a vontade de pular; quem decide e o update (coyote + buffer),
        # assim da pra pular um tiquinho depois de sair da plataforma ou um
        # tiquinho antes de encostar no chao.
        self.buffer_pulo = 0.12

    def criar_flecha(self, alvo_mundo, arco):
        """Cria uma flecha mirando em 'alvo_mundo' (coordenadas de mundo)."""
        if self.cooldown_tiro > 0:
            return None
        origem = (self.rect.centerx, self.rect.centery - 2)
        dx = alvo_mundo[0] - origem[0]
        dy = alvo_mundo[1] - origem[1]
        dist = math.hypot(dx, dy) or 1.0
        self.virado_dir = dx >= 0
        self.cooldown_tiro = 0.25
        return Flecha(origem[0], origem[1], dx / dist, dy / dist,
                      arco.dano, arco.velocidade, self.recursos)

    # ------------------------------------------------------------- update
    def atualizar(self, dt, fase):
        self._ler_teclado()

        # gravidade
        self.vy = min(self.vy + config.GRAVIDADE, config.VEL_MAX_QUEDA)

        # --- movimento horizontal ---
        self.rect.x += round(self.vx)
        self._colidir_horizontal(fase.solidos)

        # --- movimento vertical ---
        base_antes = self.rect.bottom
        self.rect.y += round(self.vy)
        self.no_chao = False
        self._colidir_vertical_solido(fase.solidos)
        self._colidir_uma_via(fase.plataformas_uma_via(), base_antes)

        # pulo com coyote time + jump buffer
        if self.no_chao:
            self.coyote = 0.1
        else:
            self.coyote = max(0.0, self.coyote - dt)
        self.buffer_pulo = max(0.0, self.buffer_pulo - dt)
        if self.buffer_pulo > 0 and self.coyote > 0:
            self.vy = -config.FORCA_PULO
            self.no_chao = False
            self.coyote = 0.0
            self.buffer_pulo = 0.0

        if self.invul > 0:
            self.invul = max(0.0, self.invul - dt)
        if self.cooldown_tiro > 0:
            self.cooldown_tiro = max(0.0, self.cooldown_tiro - dt)

        self._atualizar_animacao(dt)

    def _atualizar_animacao(self, dt):
        if self.cooldown_tiro > 0 and self.no_chao:
            novo = "atirar"
        elif not self.no_chao:
            novo = "pulo"
        elif abs(self.vx) > 0.1:
            novo = "andar"
        else:
            novo = "parado"
        if novo != self.estado_anim:
            self.estado_anim = novo
            self.animacoes[novo].reiniciar()
        self.animacoes[self.estado_anim].atualizar(dt)

    def _ler_teclado(self):
        teclas = pygame.key.get_pressed()
        self.vx = 0.0
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.vx = -config.VEL_ANDAR
            self.virado_dir = False
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.vx = config.VEL_ANDAR
            self.virado_dir = True

    # ------------------------------------------------------------- colisao
    def _colidir_horizontal(self, solidos):
        for s in solidos:
            if self.rect.colliderect(s):
                if self.vx > 0:
                    self.rect.right = s.left
                elif self.vx < 0:
                    self.rect.left = s.right
                self.vx = 0.0

    def _colidir_vertical_solido(self, solidos):
        for s in solidos:
            if self.rect.colliderect(s):
                if self.vy > 0:
                    self.rect.bottom = s.top
                    self.no_chao = True
                elif self.vy < 0:
                    self.rect.top = s.bottom
                self.vy = 0.0

    def _colidir_uma_via(self, plataformas, base_antes):
        for p in plataformas:
            if self.rect.colliderect(p) and self.vy >= 0 and base_antes <= p.top + 2:
                self.rect.bottom = p.top
                self.no_chao = True
                self.vy = 0.0

    # ------------------------------------------------------------- dano
    def levar_dano(self, mundo, quantidade=1, origem_x=None):
        if self.invul > 0:
            return False
        mundo.vida = max(0, mundo.vida - quantidade)
        self.invul = 1.0
        # empurraozinho pro lado contrario do inimigo
        if origem_x is not None:
            self.vx = 0
            self.rect.x += -6 if origem_x > self.rect.centerx else 6
        self.vy = -3.0
        return True

    # ------------------------------------------------------------- desenho
    def desenhar(self, tela, camera):
        # pisca quando esta invencivel (acabou de tomar dano)
        if self.invul > 0 and int(self.invul * 20) % 2 == 0:
            return
        quadro = self.animacoes[self.estado_anim].quadro()
        if not self.virado_dir:
            quadro = pygame.transform.flip(quadro, True, False)
        # alinha os "pes" do sprite na base da hitbox (sprite pode ser maior que a hitbox)
        destino = quadro.get_rect(midbottom=camera.aplicar(self.rect).midbottom)
        tela.blit(quadro, destino)
