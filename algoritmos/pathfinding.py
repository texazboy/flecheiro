# -*- coding: utf-8 -*-
"""
Busca de caminho minimo em grade com A* (A-estrela).

E o caminho mais curto entre duas celulas de uma grade evitando paredes. A* e
o Dijkstra "com palpite": alem do custo ja gasto g(n), soma uma heuristica h(n)
que estima o quanto falta ate o objetivo. Enquanto a heuristica nunca
SUPERESTIMA a distancia real (heuristica admissivel), o A* garante o caminho
otimo - e costuma visitar bem menos celulas que o Dijkstra puro.

Usamos a distancia de Manhattan como heuristica (movimentos em 4 direcoes), que
e admissivel nesse tipo de grade. Sem heuristica (h = 0), o A* vira o proprio
Dijkstra; por isso da pra comparar com uma BFS em grade nao ponderada nos testes.

Serve pra navegacao de inimigos/NPCs e pra validar se uma fase continua
"alcancavel" depois que o jogador altera o cenario. Nao depende de pygame.
"""

import heapq
from collections import namedtuple

# caminho : lista de celulas (linha, coluna) do inicio ao objetivo (inclusive)
# custo   : numero de passos (None se nao existe caminho)
ResultadoCaminho = namedtuple("ResultadoCaminho", ["caminho", "custo"])

# vizinhanca em 4 direcoes (cima, baixo, esquerda, direita)
_VIZINHOS = ((-1, 0), (1, 0), (0, -1), (0, 1))


def _distancia_manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _livre(grade, linha, coluna):
    """True se (linha, coluna) esta dentro da grade e nao e parede (0 = livre)."""
    if linha < 0 or linha >= len(grade):
        return False
    if coluna < 0 or coluna >= len(grade[linha]):
        return False
    return grade[linha][coluna] == 0


def a_estrela(grade, inicio, objetivo):
    """
    Caminho minimo de 'inicio' ate 'objetivo' numa grade de 0 (livre) e 1 (parede).

      grade    : lista de listas com 0/1 (grade[linha][coluna])
      inicio   : (linha, coluna) de partida
      objetivo : (linha, coluna) de destino

    Devolve ResultadoCaminho(caminho, custo). Se nao houver caminho, devolve
    ResultadoCaminho(None, None).
    """
    if not _livre(grade, *inicio) or not _livre(grade, *objetivo):
        return ResultadoCaminho(None, None)
    if inicio == objetivo:
        return ResultadoCaminho([inicio], 0)

    # fila de prioridade por f = g + h; o contador desempata e mantem estabilidade
    contador = 0
    aberto = [(_distancia_manhattan(inicio, objetivo), 0, contador, inicio)]
    veio_de = {}
    melhor_g = {inicio: 0}
    fechado = set()

    while aberto:
        _, g, _, atual = heapq.heappop(aberto)
        if atual == objetivo:
            return ResultadoCaminho(_reconstruir(veio_de, atual), g)
        if atual in fechado:
            continue
        fechado.add(atual)

        linha, coluna = atual
        for dl, dc in _VIZINHOS:
            viz = (linha + dl, coluna + dc)
            if not _livre(grade, *viz) or viz in fechado:
                continue
            novo_g = g + 1
            if novo_g < melhor_g.get(viz, float("inf")):
                melhor_g[viz] = novo_g
                veio_de[viz] = atual
                f = novo_g + _distancia_manhattan(viz, objetivo)
                contador += 1
                heapq.heappush(aberto, (f, novo_g, contador, viz))

    return ResultadoCaminho(None, None)


def _reconstruir(veio_de, atual):
    caminho = [atual]
    while atual in veio_de:
        atual = veio_de[atual]
        caminho.append(atual)
    caminho.reverse()
    return caminho


def alcancavel(grade, inicio, objetivo):
    """Atalho: True se existe caminho de 'inicio' ate 'objetivo'."""
    return a_estrela(grade, inicio, objetivo).caminho is not None


if __name__ == "__main__":
    # 0 = livre, 1 = parede; o caminho desvia da coluna de paredes no meio
    mapa = [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 1, 0],
        [1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0],
    ]
    r = a_estrela(mapa, (0, 0), (4, 0))
    print("custo :", r.custo)
    print("passos:", r.caminho)
