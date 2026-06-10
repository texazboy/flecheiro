# -*- coding: utf-8 -*-
"""
Pacote com os algoritmos classicos usados como mecanica do jogo.

Ficam separados de proposito: nao dependem de pygame nem de nada grafico,
entao da pra testar no terminal e justificar na documentacao sem amarra com a
parte visual. Quem usa esses algoritmos sao as telas/fases do jogo.
"""

from .tsp import resolver_tsp, custo_rota, ResultadoTSP
from .mochila import resolver_mochila, mochila_dp, mochila_gulosa, ResultadoMochila
from .ordenacao import quicksort, ordenar_itens

__all__ = [
    "resolver_tsp", "custo_rota", "ResultadoTSP",
    "resolver_mochila", "mochila_dp", "mochila_gulosa", "ResultadoMochila",
    "quicksort", "ordenar_itens",
]
