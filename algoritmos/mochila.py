# -*- coding: utf-8 -*-
"""
Problema da Mochila 0/1 (Knapsack) - usado na FERRARIA do jogo.

Na hora de forjar um arco novo, a bigorna tem uma capacidade maxima de peso de
material. Cada material recolhido tem um peso e um valor (o quanto ele agrega de
qualidade ao arco). O ferreiro precisa escolher QUAIS materiais usar pra
maximizar a qualidade do arco sem estourar a capacidade -> isso e exatamente a
mochila 0/1 (cada material entra ou nao, nao da pra usar "meio material").

Implementamos duas abordagens pra comparar (e justificar na documentacao):

  - mochila_dp     : programacao dinamica, resposta OTIMA -> O(n * W)
  - mochila_gulosa : escolhe por melhor razao valor/peso, RAPIDA mas pode errar

O jogo usa a versao DP (otima). A gulosa fica disponivel pra demonstrar o
trade-off entre garantia de otimo e velocidade.
"""

from collections import namedtuple

# selecionados = lista dos itens escolhidos (os mesmos objetos recebidos)
ResultadoMochila = namedtuple("ResultadoMochila", ["valor", "peso", "selecionados", "metodo"])


def _peso(item):
    return int(getattr(item, "peso", item[0] if isinstance(item, tuple) else 0))


def _valor(item):
    return int(getattr(item, "valor", item[1] if isinstance(item, tuple) else 0))


def resolver_mochila(itens, capacidade):
    """Entrada usada pelo jogo: resolve de forma OTIMA via programacao dinamica."""
    return mochila_dp(itens, capacidade)


def mochila_dp(itens, capacidade):
    """
    Mochila 0/1 classica por programacao dinamica.

    dp[i][c] = melhor valor usando os primeiros i itens com capacidade c.
    Depois fazemos o "backtracking" na tabela pra descobrir quais itens entraram.
    """
    capacidade = int(capacidade)
    n = len(itens)
    if n == 0 or capacidade <= 0:
        return ResultadoMochila(0, 0, [], "dp (otimo)")

    # Tabela (n+1) x (capacidade+1)
    dp = [[0] * (capacidade + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        peso_i = _peso(itens[i - 1])
        valor_i = _valor(itens[i - 1])
        for c in range(capacidade + 1):
            # nao usar o item i
            dp[i][c] = dp[i - 1][c]
            # usar o item i (se couber) e ficar com o melhor dos dois casos
            if peso_i <= c:
                com_item = dp[i - 1][c - peso_i] + valor_i
                if com_item > dp[i][c]:
                    dp[i][c] = com_item

    # Reconstroi quais itens foram escolhidos.
    selecionados = []
    c = capacidade
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            item = itens[i - 1]
            selecionados.append(item)
            c -= _peso(item)
    selecionados.reverse()

    peso_total = sum(_peso(it) for it in selecionados)
    return ResultadoMochila(dp[n][capacidade], peso_total, selecionados, "dp (otimo)")


def mochila_gulosa(itens, capacidade):
    """
    Heuristica gulosa: ordena por razao valor/peso e vai pegando enquanto cabe.
    Rapida, mas NAO garante o otimo no caso 0/1 (existe pra comparacao).
    """
    capacidade = int(capacidade)
    ordenados = sorted(
        itens,
        key=lambda it: (_valor(it) / _peso(it)) if _peso(it) > 0 else float("inf"),
        reverse=True,
    )
    selecionados = []
    peso_total = 0
    valor_total = 0
    for item in ordenados:
        if peso_total + _peso(item) <= capacidade:
            selecionados.append(item)
            peso_total += _peso(item)
            valor_total += _valor(item)
    return ResultadoMochila(valor_total, peso_total, selecionados, "gulosa (heuristica)")
