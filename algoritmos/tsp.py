# -*- coding: utf-8 -*-
"""
Problema do Caixeiro Viajante (TSP) - menor rota que passa por todos os pontos
de coleta e volta ao ponto de partida (ciclo fechado).

No jogo isso vira um "overlay" que mostra ao jogador a ordem otima de pegar os
itens dropados na fase. Como o TSP e NP-dificil, a gente usa duas estrategias e
escolhe conforme a quantidade de pontos:

  - n <= LIMITE_EXATO : solucao EXATA com Held-Karp  -> O(n^2 * 2^n)
  - n  > LIMITE_EXATO : HEURISTICA (vizinho mais proximo + melhoria 2-opt) -> ~O(n^2)

A ideia de ter os dois e justamente mostrar o trade-off classico:
exato da a resposta perfeita mas explode com o tamanho; a heuristica e rapida e
costuma chegar bem perto do otimo.
"""

import math
from collections import namedtuple

# Ate este numero de pontos resolvemos de forma exata. Acima disso, heuristica.
# (o enunciado sugere 15; Held-Karp ainda roda numa boa nesse limite)
LIMITE_EXATO = 15

ResultadoTSP = namedtuple("ResultadoTSP", ["ordem", "custo", "metodo"])


def distancia(a, b):
    """Distancia euclidiana entre dois pontos (x, y)."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def custo_rota(ordem, pontos):
    """Custo total de um ciclo fechado: soma das arestas + volta ao inicio."""
    if len(ordem) < 2:
        return 0.0
    total = 0.0
    for i in range(len(ordem)):
        atual = pontos[ordem[i]]
        prox = pontos[ordem[(i + 1) % len(ordem)]]
        total += distancia(atual, prox)
    return total


def resolver_tsp(pontos, limite_exato=LIMITE_EXATO):
    """
    Ponto de entrada usado pelo jogo.

    Recebe uma lista de coordenadas [(x, y), ...] e devolve um ResultadoTSP com:
      - ordem  : lista de indices na ordem de visita (sempre comeca em 0)
      - custo  : comprimento total do ciclo
      - metodo : "exato (Held-Karp)" ou "heuristica (2-opt)"
    """
    n = len(pontos)
    if n <= 1:
        return ResultadoTSP(list(range(n)), 0.0, "trivial")
    if n <= 3:
        # Com 2 ou 3 pontos qualquer ordem da no mesmo ciclo; nem precisa pensar.
        ordem = list(range(n))
        return ResultadoTSP(ordem, custo_rota(ordem, pontos), "trivial")

    if n <= limite_exato:
        ordem, custo = _held_karp(pontos)
        return ResultadoTSP(ordem, custo, "exato (Held-Karp)")

    ordem = _vizinho_mais_proximo(pontos)
    ordem = _dois_opt(ordem, pontos)
    return ResultadoTSP(ordem, custo_rota(ordem, pontos), "heuristica (2-opt)")


# ---------------------------------------------------------------------------
# Solucao exata: programacao dinamica de Held-Karp
# ---------------------------------------------------------------------------
def _held_karp(pontos):
    n = len(pontos)
    dist = [[distancia(pontos[i], pontos[j]) for j in range(n)] for i in range(n)]

    total_mascaras = 1 << n
    INF = float("inf")
    # dp[mascara][j] = menor custo saindo de 0, visitando exatamente os
    # vertices marcados em "mascara" e terminando no vertice j.
    dp = [[INF] * n for _ in range(total_mascaras)]
    pai = [[-1] * n for _ in range(total_mascaras)]
    dp[1][0] = 0.0  # so o vertice 0 visitado, parado nele

    for mascara in range(total_mascaras):
        if not (mascara & 1):
            continue  # toda rota comeca no vertice 0
        for j in range(n):
            if dp[mascara][j] == INF:
                continue
            custo_ate_j = dp[mascara][j]
            for k in range(n):
                if mascara & (1 << k):
                    continue  # k ja foi visitado
                nova_mascara = mascara | (1 << k)
                novo_custo = custo_ate_j + dist[j][k]
                if novo_custo < dp[nova_mascara][k]:
                    dp[nova_mascara][k] = novo_custo
                    pai[nova_mascara][k] = j

    cheia = total_mascaras - 1
    melhor_custo = INF
    ultimo = 0
    for j in range(n):
        custo_total = dp[cheia][j] + dist[j][0]  # fecha o ciclo voltando ao 0
        if custo_total < melhor_custo:
            melhor_custo = custo_total
            ultimo = j

    # Reconstroi a ordem andando pelos "pais".
    ordem = []
    mascara = cheia
    j = ultimo
    while j != -1:
        ordem.append(j)
        anterior = pai[mascara][j]
        mascara ^= (1 << j)
        j = anterior
    ordem.reverse()
    return ordem, melhor_custo


# ---------------------------------------------------------------------------
# Heuristicas (para n grande)
# ---------------------------------------------------------------------------
def _vizinho_mais_proximo(pontos):
    """Comeca no 0 e sempre vai pro ponto mais perto ainda nao visitado."""
    n = len(pontos)
    visitado = [False] * n
    ordem = [0]
    visitado[0] = True
    atual = 0
    for _ in range(n - 1):
        melhor = -1
        melhor_dist = float("inf")
        for k in range(n):
            if visitado[k]:
                continue
            d = distancia(pontos[atual], pontos[k])
            if d < melhor_dist:
                melhor_dist = d
                melhor = k
        ordem.append(melhor)
        visitado[melhor] = True
        atual = melhor
    return ordem


def _dois_opt(ordem, pontos):
    """
    Melhora uma rota desfazendo cruzamentos: inverte trechos enquanto isso
    diminuir o custo. Usa calculo de delta (so as 4 arestas que mudam) pra
    nao recalcular a rota inteira a cada tentativa.
    """
    n = len(ordem)
    melhorou = True
    while melhorou:
        melhorou = False
        for i in range(n - 1):
            a = ordem[i]
            b = ordem[i + 1]
            for k in range(i + 2, n):
                c = ordem[k]
                d = ordem[(k + 1) % n]
                if i == 0 and (k + 1) % n == 0:
                    continue  # mesma aresta, nao faz sentido trocar
                atual = distancia(pontos[a], pontos[b]) + distancia(pontos[c], pontos[d])
                trocado = distancia(pontos[a], pontos[c]) + distancia(pontos[b], pontos[d])
                if trocado + 1e-9 < atual:
                    ordem[i + 1:k + 1] = reversed(ordem[i + 1:k + 1])
                    melhorou = True
                    b = ordem[i + 1]
    return ordem
