# -*- coding: utf-8 -*-
"""
Cobertura de conjuntos - ferramenta de level design.

Problema: dado um conjunto de ALVOS (plataformas relevantes de uma fase) e
varios POSTOS candidatos (cada um "cobre" os alvos ao seu alcance), qual o menor
numero de postos que deixa TODO alvo coberto? Isso e a cobertura de conjuntos,
que e NP-dificil.

Como achar o otimo e caro, usamos a heuristica gulosa de Chvatal: a cada passo
escolhe o posto que cobre a MAIOR quantidade de alvos ainda descobertos. Ela tem
garantia de aproximacao logaritmica (no maximo ~ln(n) vezes o otimo), o que e
otimo na pratica pra sugerir posicionamento de inimigos, tochas ou itens.

Tambem ha a variante de COBERTURA MAXIMA: com orcamento fixo de k postos, cobrir
o maximo de alvos possivel (mesma logica gulosa).

O modulo nao depende de pygame: da pra rodar e testar no terminal.
"""

from collections import namedtuple

# escolhidos : indices dos subconjuntos escolhidos, na ordem em que entraram
# cobertos   : conjunto de elementos efetivamente cobertos
# completa   : True se cobriu o universo inteiro
ResultadoCobertura = namedtuple("ResultadoCobertura", ["escolhidos", "cobertos", "completa"])


def _melhor_ganho(conjuntos, restantes, cobertos):
    """Indice do conjunto que cobre mais elementos ainda descobertos (ou -1)."""
    melhor = -1
    melhor_ganho = 0
    for i in restantes:
        ganho = len(conjuntos[i] - cobertos)
        if ganho > melhor_ganho:
            melhor_ganho = ganho
            melhor = i
    return melhor


def cobertura_de_conjuntos(universo, subconjuntos):
    """
    Cobertura MINIMA pela heuristica gulosa (Chvatal).

      universo     : elementos que precisam ser cobertos
      subconjuntos : lista de conjuntos (cada um cobre alguns elementos)

    Devolve ResultadoCobertura. Se nenhum conjunto cobre certo elemento, a
    cobertura sai incompleta (completa = False).
    """
    universo = set(universo)
    conjuntos = [set(s) & universo for s in subconjuntos]
    cobertos = set()
    escolhidos = []
    restantes = set(range(len(conjuntos)))

    while cobertos != universo:
        melhor = _melhor_ganho(conjuntos, restantes, cobertos)
        if melhor == -1:
            break  # ninguem cobre nada novo -> impossivel completar
        escolhidos.append(melhor)
        cobertos |= conjuntos[melhor]
        restantes.discard(melhor)

    return ResultadoCobertura(escolhidos, cobertos, cobertos == universo)


def cobertura_maxima(universo, subconjuntos, k):
    """
    Cobertura MAXIMA com orcamento: escolhe ate k conjuntos pra cobrir o maximo
    de elementos do universo (mesma logica gulosa).
    """
    universo = set(universo)
    conjuntos = [set(s) & universo for s in subconjuntos]
    cobertos = set()
    escolhidos = []
    restantes = set(range(len(conjuntos)))

    while len(escolhidos) < k and restantes:
        melhor = _melhor_ganho(conjuntos, restantes, cobertos)
        if melhor == -1:
            break
        escolhidos.append(melhor)
        cobertos |= conjuntos[melhor]
        restantes.discard(melhor)

    return ResultadoCobertura(escolhidos, cobertos, cobertos == universo)


def planejar_cobertura(candidatos):
    """
    Versao "com rotulos" pra usar no jogo.

      candidatos : dict {rotulo_do_posto: iteravel de alvos que ele cobre}

    Devolve (rotulos_escolhidos, completa) com o menor conjunto de postos que
    cobre todos os alvos citados.
    """
    rotulos = list(candidatos.keys())
    subconjuntos = [set(candidatos[r]) for r in rotulos]
    universo = set().union(*subconjuntos) if subconjuntos else set()
    res = cobertura_de_conjuntos(universo, subconjuntos)
    return [rotulos[i] for i in res.escolhidos], res.completa


if __name__ == "__main__":
    # cada posto (A..D) ameaca um grupo de plataformas (1..5)
    postos = {
        "A": {1, 2, 3},
        "B": {2, 4},
        "C": {3, 4},
        "D": {4, 5},
    }
    escolhidos, completa = planejar_cobertura(postos)
    print("postos escolhidos:", escolhidos, "| cobre tudo?", completa)
