# -*- coding: utf-8 -*-
"""
Ordenacao do inventario (problema computacional extra).

Quando o jogador abre o inventario, ele pode reordenar os itens por valor, peso
ou raridade. Em vez de usar o sorted() pronto da linguagem, implementamos o
Quicksort na mao pra ter o algoritmo classico explicito (e poder explicar a
complexidade media O(n log n) na documentacao).
"""


def quicksort(lista, chave=lambda x: x, decrescente=False):
    """
    Quicksort que devolve uma NOVA lista ordenada (nao altera a original).
    'chave' extrai o valor de comparacao de cada elemento, igual ao sorted().
    """
    if len(lista) <= 1:
        return list(lista)

    pivo = lista[len(lista) // 2]
    valor_pivo = chave(pivo)

    menores = [x for x in lista if chave(x) < valor_pivo]
    iguais = [x for x in lista if chave(x) == valor_pivo]
    maiores = [x for x in lista if chave(x) > valor_pivo]

    ordenada = quicksort(menores, chave) + iguais + quicksort(maiores, chave)
    if decrescente:
        ordenada.reverse()
    return ordenada


# Ordem de raridade pra conseguir comparar com numero (comum < ... < lendario).
_RANK_RARIDADE = {"comum": 0, "incomum": 1, "raro": 2, "epico": 3, "lendario": 4}


def ordenar_itens(itens, por="valor"):
    """
    Ordena uma lista de itens do inventario por um criterio.
    Aceita: 'valor', 'peso' ou 'raridade'. Retorna nova lista (decrescente).
    """
    if por == "peso":
        chave = lambda it: getattr(it, "peso", 0)
    elif por == "raridade":
        chave = lambda it: _RANK_RARIDADE.get(getattr(it, "raridade", "comum"), 0)
    else:  # valor (padrao)
        chave = lambda it: getattr(it, "valor", 0)

    return quicksort(itens, chave=chave, decrescente=True)
