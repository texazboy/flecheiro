# -*- coding: utf-8 -*-
"""
"Mundo": tudo que precisa sobreviver entre uma fase e outra.

O inventario, o ouro e o arco equipado nao podem zerar quando o jogador troca de
tela (fase -> vila -> fase). Entao a gente guarda isso aqui e passa a mesma
instancia de Mundo pra cada estado novo.
"""

from dataclasses import dataclass

import config
from core.inventario import Inventario


@dataclass
class Arco:
    nome: str
    dano: int
    velocidade: float   # multiplica a velocidade da flecha
    cor: tuple


# Arco que o jogador comeca segurando.
ARCO_INICIAL = Arco("Arco Simples", 1, 1.0, config.MARROM_CLARO)

# Faixas de qualidade -> resultado da forja. A "qualidade" vem do valor que a
# mochila 0/1 conseguiu montar com os materiais escolhidos (ver telas/ferraria).
_FAIXAS_ARCO = [
    (22, Arco("Arco Lendario", 5, 1.6, config.AMARELO)),
    (15, Arco("Arco Elfico", 4, 1.4, config.VERDE)),
    (9,  Arco("Arco de Caca", 3, 1.2, config.LARANJA)),
    (1,  Arco("Arco Reforcado", 2, 1.1, config.CINZA)),
]


def arco_por_qualidade(qualidade):
    """Mapeia o valor obtido na mochila para um arco forjado."""
    for minimo, arco in _FAIXAS_ARCO:
        if qualidade >= minimo:
            return arco
    return ARCO_INICIAL


class Mundo:
    def __init__(self):
        self.inventario = Inventario()
        self.ouro = 0
        self.arco = ARCO_INICIAL
        self.vida_max = 5
        self.vida = 5
        # estatisticas da partida (aparecem na tela de vitoria)
        self.arcos_forjados = 0
        self.abatidos = 0
        self.coletados = 0
        self.tempo = 0.0
        # Desafio da Rota (TSP): estrelas somadas nas fases (max 3 por fase)
        self.estrelas_rota = 0
