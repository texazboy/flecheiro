# -*- coding: utf-8 -*-
"""
Fluxo maximo em rede - modela a ECONOMIA da vila.

A ideia: a vila recebe materiais (madeira, ferro, couro...) que sao consumidos
por dois destinos, a ferraria e a loja. Cada ligacao tem uma capacidade (quanto
material passa por ali). A pergunta "quanto material a vila consegue, no maximo,
escoar de uma vez?" e um problema de FLUXO MAXIMO classico.

Montamos a rede assim (cada material alimenta os dois destinos):

    fonte --(estoque)--> material --(oferta)--> ferraria --(cap. forja)--> sumidouro
    fonte --(estoque)--> material --(oferta)--> loja     --(cap. venda)--> sumidouro

Resolvemos com Edmonds-Karp: e o metodo de Ford-Fulkerson usando BFS pra achar
o caminho aumentante mais curto a cada passo. Isso garante terminacao e custo
O(V * E^2), sem depender da magnitude das capacidades.

O modulo nao depende de pygame: da pra rodar e testar no terminal.
"""

from collections import namedtuple, deque

# valor   : valor do fluxo maximo (fonte -> sumidouro)
# fluxo   : matriz fluxo[u][v] com o fluxo que passou em cada aresta
ResultadoFluxo = namedtuple("ResultadoFluxo", ["valor", "fluxo"])


def fluxo_maximo(num_vertices, arestas, fonte, sumidouro):
    """
    Fluxo maximo por Edmonds-Karp.

      num_vertices : quantidade de vertices (rotulados de 0 a num_vertices-1)
      arestas      : lista de (u, v, capacidade) com capacidade >= 0
      fonte        : vertice de origem
      sumidouro    : vertice de destino

    Devolve um ResultadoFluxo(valor, fluxo).
    """
    n = num_vertices
    # matriz de capacidade (acumula arestas paralelas entre os mesmos vertices)
    cap = [[0] * n for _ in range(n)]
    for u, v, c in arestas:
        if c < 0:
            raise ValueError("capacidade nao pode ser negativa")
        cap[u][v] += c

    fluxo = [[0] * n for _ in range(n)]

    if fonte == sumidouro:
        return ResultadoFluxo(0, fluxo)

    valor = 0
    while True:
        # BFS no grafo residual: acha o caminho aumentante com menos arestas
        pai = [-1] * n
        pai[fonte] = fonte
        fila = deque([fonte])
        while fila and pai[sumidouro] == -1:
            u = fila.popleft()
            for v in range(n):
                residual = cap[u][v] - fluxo[u][v]
                if residual > 0 and pai[v] == -1:
                    pai[v] = u
                    fila.append(v)

        if pai[sumidouro] == -1:
            break  # nao ha mais caminho aumentante: chegamos no maximo

        # gargalo: menor residual ao longo do caminho encontrado
        gargalo = float("inf")
        v = sumidouro
        while v != fonte:
            u = pai[v]
            gargalo = min(gargalo, cap[u][v] - fluxo[u][v])
            v = u

        # empurra o gargalo pela frente e devolve pela aresta reversa
        v = sumidouro
        while v != fonte:
            u = pai[v]
            fluxo[u][v] += gargalo
            fluxo[v][u] -= gargalo
            v = u

        valor += gargalo

    return ResultadoFluxo(valor, fluxo)


# nome dos papeis na rede da vila, pra deixar a modelagem legivel
RedeVila = namedtuple("RedeVila", ["resultado", "rotulos"])


def rede_economia_vila(estoque, cap_ferraria, cap_loja, oferta=None):
    """
    Monta e resolve a rede de fluxo da economia da vila.

      estoque      : dict {nome_material: quantidade disponivel}
      cap_ferraria : quanto material a ferraria consegue processar
      cap_loja     : quanto material a loja consegue absorver
      oferta       : capacidade de cada material -> destino (default: o estoque
                     inteiro pode ir pra qualquer destino)

    Devolve RedeVila(resultado, rotulos): o resultado do fluxo_maximo e a lista
    de rotulos por indice de vertice (util pra inspecionar/depurar).
    """
    materiais = list(estoque.keys())
    # vertices: 0 = fonte, 1..m = materiais, m+1 = ferraria, m+2 = loja, m+3 = sumidouro
    fonte = 0
    base_mat = 1
    ferraria = base_mat + len(materiais)
    loja = ferraria + 1
    sumidouro = loja + 1
    n = sumidouro + 1

    arestas = []
    for i, mat in enumerate(materiais):
        v_mat = base_mat + i
        arestas.append((fonte, v_mat, int(estoque[mat])))
        limite = int(oferta) if oferta is not None else int(estoque[mat])
        arestas.append((v_mat, ferraria, limite))
        arestas.append((v_mat, loja, limite))
    arestas.append((ferraria, sumidouro, int(cap_ferraria)))
    arestas.append((loja, sumidouro, int(cap_loja)))

    rotulos = ["fonte"] + materiais + ["ferraria", "loja", "sumidouro"]
    resultado = fluxo_maximo(n, arestas, fonte, sumidouro)
    return RedeVila(resultado, rotulos)


if __name__ == "__main__":
    # demonstracao rapida: estoque farto, mas os destinos sao o gargalo
    rede = rede_economia_vila(
        estoque={"madeira": 8, "ferro": 5, "couro": 4},
        cap_ferraria=6,
        cap_loja=5,
    )
    print("rotulos :", rede.rotulos)
    print("vazao maxima da vila:", rede.resultado.valor)  # limitado por 6 + 5 = 11
