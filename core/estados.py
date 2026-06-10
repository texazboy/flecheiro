# -*- coding: utf-8 -*-
"""
Base da maquina de estados (telas) do jogo.

Cada tela grande (menu, fase, vila, vitoria) herda de Estado. As "telinhas"
menores que aparecem por cima (inventario, dialogo, ferraria, loja) sao tratadas
como sobreposicoes DENTRO do estado que as abriu - assim nao precisamos de uma
pilha de estados complicada pra um jogo desse tamanho.

A classe Jogo (em main.py) guarda o estado atual e chama estes metodos no loop.
"""


class Estado:
    def __init__(self, jogo):
        self.jogo = jogo

    def entrar(self):
        """Chamado uma vez quando este estado vira o estado atual."""

    def sair(self):
        """Chamado quando saimos deste estado."""

    def tratar_evento(self, evento):
        """Recebe cada evento do pygame (teclado, mouse, fechar janela)."""

    def atualizar(self, dt):
        """Atualiza a logica. dt = tempo do frame em segundos."""

    def desenhar(self, tela):
        """Desenha na superficie interna (baixa resolucao)."""
