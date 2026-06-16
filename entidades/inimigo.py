# -*- coding: utf-8 -*-
"""
Inimigos do jogo.

  - Inimigo        : o terrestre classico, patrulha de um lado pro outro.
  - InimigoVoador  : morcego que voa em "oito" no ar; gosta de ficar pairando
                     sobre os vaos da fase 3, bem onde o jogador quer pular.

Os dois falam a mesma "lingua" (atualizar / levar_dano / desenhar / rect /
morto / dropa), entao a Fase trata todo mundo igual.
"""

import math

import pygame

import config


class Inimigo:
    def __init__(self, x, y, recursos, dropa="madeira", alcance=48, vida=2, velocidade=0.7):
        # hitbox mais larga que alta: combina com o corpo achatado do slime
        self.rect = pygame.Rect(x, y, 20, 15)
        self.anim = recursos.animacao("inimigo", "andar", 15, fps=6)
        self.origem_x = x
        self.alcance = alcance
        self.vx = velocidade
        self.vy = 0.0
        self.vida = vida
        self.vida_max = vida
        self.morto = False
        self.dropa = dropa
        self.flash = 0.0   # pisca branco quando leva uma flechada
        self.cor_explosao = (124, 200, 96)   # gosma verde de slime

    def atualizar(self, dt, fase):
        # patrulha: vira quando passa do limite
        if self.rect.x > self.origem_x + self.alcance:
            self.vx = -abs(self.vx)
        elif self.rect.x < self.origem_x - self.alcance:
            self.vx = abs(self.vx)

        self.rect.x += round(self.vx)
        for s in fase.solidos:
            if self.rect.colliderect(s):
                if self.vx > 0:
                    self.rect.right = s.left
                else:
                    self.rect.left = s.right
                self.vx = -self.vx  # bateu na parede, volta

        # gravidade pra nao flutuar
        self.vy = min(self.vy + config.GRAVIDADE, config.VEL_MAX_QUEDA)
        self.rect.y += round(self.vy)
        for s in fase.solidos:
            if self.rect.colliderect(s):
                if self.vy > 0:
                    self.rect.bottom = s.top
                elif self.vy < 0:
                    self.rect.top = s.bottom
                self.vy = 0.0

        self.anim.atualizar(dt)
        if self.flash > 0:
            self.flash = max(0.0, self.flash - dt)

    def levar_dano(self, dano):
        self.vida -= dano
        self.flash = 0.12
        if self.vida <= 0:
            self.morto = True

    def desenhar(self, tela, camera):
        # convencao: o sprite-base olha para a DIREITA; espelha quando anda p/ esquerda
        quadro = self.anim.quadro()
        if self.vx < 0:
            quadro = pygame.transform.flip(quadro, True, False)
        if self.flash > 0:
            quadro = quadro.copy()
            quadro.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
        destino = quadro.get_rect(midbottom=camera.aplicar(self.rect).midbottom)
        tela.blit(quadro, destino)
        # barrinha de vida em cima quando ja tomou dano
        if not self.morto and self.vida < self.vida_max:
            r = camera.aplicar(self.rect)
            largura = int(self.rect.width * (self.vida / self.vida_max))
            pygame.draw.rect(tela, config.PRETO, (r.left, r.top - 4, self.rect.width, 2))
            pygame.draw.rect(tela, config.VERMELHO, (r.left, r.top - 4, max(0, largura), 2))


class InimigoCorredor:
    """Bicho rasteiro e rapido (rato): patrulha devagar, mas quando enxerga o
    jogador no mesmo nivel e perto, dispara uma INVESTIDA. Depois cansa um
    pouco antes de poder atacar de novo. Da um susto gostoso."""

    def __init__(self, x, y, recursos, dropa="couro", alcance=70, vida=2, velocidade=1.0):
        self.rect = pygame.Rect(x, y, 18, 14)
        self.anim = recursos.animacao("corredor", "andar", 16, fps=10)
        self.origem_x = x
        self.alcance = alcance
        self.vx = velocidade
        self.vel_patrulha = velocidade
        self.vy = 0.0
        self.vida = vida
        self.vida_max = vida
        self.morto = False
        self.dropa = dropa
        self.flash = 0.0
        self.cor_explosao = (150, 120, 96)   # poeira marrom
        self.investindo = 0.0
        self.cansaco = 0.0

    def atualizar(self, dt, fase):
        jog = fase.jogador
        mesmo_nivel = abs(jog.rect.bottom - self.rect.bottom) < 26
        dx = jog.rect.centerx - self.rect.centerx

        if self.cansaco > 0:
            self.cansaco -= dt
        if self.investindo > 0:
            self.investindo -= dt
        elif self.cansaco <= 0 and mesmo_nivel and abs(dx) < 140:
            self.investindo = 0.6           # dispara a investida
            self.cansaco = 1.6
            self.vx = (3.4 if dx > 0 else -3.4)

        if self.investindo <= 0:
            # patrulha normal
            if self.rect.x > self.origem_x + self.alcance:
                self.vx = -abs(self.vel_patrulha)
            elif self.rect.x < self.origem_x - self.alcance:
                self.vx = abs(self.vel_patrulha)
            elif abs(self.vx) > self.vel_patrulha:
                self.vx = self.vel_patrulha if self.vx > 0 else -self.vel_patrulha

        self.rect.x += round(self.vx)
        for s in fase.solidos:
            if self.rect.colliderect(s):
                if self.vx > 0:
                    self.rect.right = s.left
                else:
                    self.rect.left = s.right
                self.vx = -self.vx
                self.investindo = 0.0

        self.vy = min(self.vy + config.GRAVIDADE, config.VEL_MAX_QUEDA)
        self.rect.y += round(self.vy)
        for s in fase.solidos:
            if self.rect.colliderect(s):
                if self.vy > 0:
                    self.rect.bottom = s.top
                elif self.vy < 0:
                    self.rect.top = s.bottom
                self.vy = 0.0

        # corre a animacao mais rapido durante a investida
        self.anim.duracao = 1.0 / (18 if self.investindo > 0 else 10)
        self.anim.atualizar(dt)
        if self.flash > 0:
            self.flash = max(0.0, self.flash - dt)

    def levar_dano(self, dano):
        self.vida -= dano
        self.flash = 0.12
        if self.vida <= 0:
            self.morto = True

    def desenhar(self, tela, camera):
        quadro = self.anim.quadro()
        if self.vx > 0:
            quadro = pygame.transform.flip(quadro, True, False)
        if self.flash > 0:
            quadro = quadro.copy()
            quadro.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
        destino = quadro.get_rect(midbottom=camera.aplicar(self.rect).midbottom)
        tela.blit(quadro, destino)
        # rastro de poeira durante a investida
        if self.investindo > 0:
            r = camera.aplicar(self.rect)
            atras = r.right if self.vx < 0 else r.left
            pygame.draw.line(tela, (180, 160, 130), (atras, r.bottom - 2),
                             (atras - self.vx * 3, r.bottom - 2), 1)
        if not self.morto and self.vida < self.vida_max:
            r = camera.aplicar(self.rect)
            largura = int(self.rect.width * (self.vida / self.vida_max))
            pygame.draw.rect(tela, config.PRETO, (r.left, r.top - 4, self.rect.width, 2))
            pygame.draw.rect(tela, config.VERMELHO, (r.left, r.top - 4, max(0, largura), 2))


class InimigoVoador:
    """Morcego: paira fazendo um 'oito' em volta do ponto de origem."""

    def __init__(self, x, y, recursos, dropa="pena", raio=28, vida=1, velocidade=1.4):
        self.rect = pygame.Rect(0, 0, 14, 12)
        self.rect.center = (x, y)
        self.origem = (float(x), float(y))
        self.raio = raio
        self.velocidade = velocidade
        self.tempo = (x * 0.013) % math.tau   # defasagem pra nao voarem em sincronia
        self.vida = vida
        self.vida_max = vida
        self.morto = False
        self.dropa = dropa
        self.flash = 0.0
        self.cor_explosao = (150, 110, 180)   # poeira roxa de morcego
        self._x_anterior = float(x)
        self.anim = recursos.animacao("voador", "voar", 12, fps=9)

    def atualizar(self, dt, fase):
        self.tempo += dt * self.velocidade
        cx = self.origem[0] + math.cos(self.tempo) * self.raio * 2
        cy = self.origem[1] + math.sin(self.tempo * 2.0) * self.raio * 0.6
        self._x_anterior = self.rect.centerx
        self.rect.center = (int(cx), int(cy))
        self.anim.atualizar(dt)
        if self.flash > 0:
            self.flash = max(0.0, self.flash - dt)

    def levar_dano(self, dano):
        self.vida -= dano
        self.flash = 0.12
        if self.vida <= 0:
            self.morto = True

    def desenhar(self, tela, camera):
        quadro = self.anim.quadro()
        if self.rect.centerx < self._x_anterior:
            quadro = pygame.transform.flip(quadro, True, False)
        if self.flash > 0:
            quadro = quadro.copy()
            quadro.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
        destino = quadro.get_rect(center=camera.aplicar(self.rect).center)
        tela.blit(quadro, destino)
