# -*- coding: utf-8 -*-
"""
Som do jogo, 100% gerado em codigo (estilo chiptune).

Nao usamos nenhum arquivo de audio: cada efeito e uma onda sintetizada na mao
(quadrada, triangular ou ruido) com um envelope de decaimento, e a musiquinha
de fundo e uma frase curta de notas tocada em loop. Tudo e gerado uma unica vez
na inicializacao e guardado como pygame.mixer.Sound.

Se o mixer nao inicializar (maquina sem audio, testes em modo dummy), todas as
funcoes viram no-op e o jogo segue mudo sem reclamar.

Uso:
    som.iniciar()          # uma vez, depois do pygame.init()
    som.tocar("pulo")
    som.musica("vila")     # troca o loop de fundo (None para parar)
    som.alternar_mudo()    # tecla M
"""

import array
import math
import random

import pygame

TAXA = 22050

_ok = False
_mudo = False
_sons = {}
_canal_musica = None
_musica_atual = None
_estereo = False


# ---------------------------------------------------------------- geradores
def _silencio(dur):
    return array.array("h", bytes(2 * max(1, int(TAXA * dur))))


def _tom(freq, dur, tipo="tri", vol=0.4, decai=2.5):
    """Uma nota: onda basica * envelope de decaimento."""
    n = max(1, int(TAXA * dur))
    dados = array.array("h", bytes(2 * n))
    for i in range(n):
        fase = (i * freq / TAXA) % 1.0
        if tipo == "quad":
            v = 1.0 if fase < 0.5 else -1.0
        elif tipo == "ruido":
            v = random.uniform(-1.0, 1.0)
        else:  # triangulo (mais suave)
            v = 4.0 * abs(fase - 0.5) - 1.0
        env = (1.0 - i / n) ** decai
        dados[i] = int(32000 * vol * env * v)
    return dados


def _varredura(f0, f1, dur, tipo="quad", vol=0.4, decai=2.0):
    """Nota com a frequencia deslizando de f0 pra f1 (efeito de 'zip')."""
    n = max(1, int(TAXA * dur))
    dados = array.array("h", bytes(2 * n))
    fase = 0.0
    for i in range(n):
        t = i / n
        f = f0 + (f1 - f0) * t
        fase += f / TAXA
        fr = fase % 1.0
        if tipo == "quad":
            v = 1.0 if fr < 0.5 else -1.0
        elif tipo == "ruido":
            v = random.uniform(-1.0, 1.0)
        else:
            v = 4.0 * abs(fr - 0.5) - 1.0
        env = (1.0 - t) ** decai
        dados[i] = int(32000 * vol * env * v)
    return dados


def _seq(*partes):
    """Emenda sons um atras do outro."""
    saida = array.array("h")
    for p in partes:
        saida += p
    return saida


def _mix(*partes):
    """Soma sons em paralelo (com clamp pra nao estourar)."""
    n = max(len(p) for p in partes)
    saida = array.array("h", bytes(2 * n))
    for p in partes:
        for i, v in enumerate(p):
            soma = saida[i] + v
            saida[i] = max(-32000, min(32000, soma))
    return saida


def _frase(notas, bpm, tipo="tri", vol=0.14):
    """Sequencia de colcheias; 0 = pausa. Vira o loop da musica de fundo."""
    dur = 60.0 / bpm / 2.0
    saida = array.array("h")
    for f in notas:
        if f:
            saida += _tom(f, dur, tipo, vol, decai=1.6)
        else:
            saida += _silencio(dur)
    return saida


def _para_estereo(dados):
    saida = array.array("h", bytes(4 * len(dados)))
    for i, v in enumerate(dados):
        saida[2 * i] = v
        saida[2 * i + 1] = v
    return saida


def _som(dados):
    if _estereo:
        dados = _para_estereo(dados)
    return pygame.mixer.Sound(buffer=dados.tobytes())


# ---------------------------------------------------------------- montagem
def _gerar_tudo():
    s = {}
    # efeitos
    s["tiro"] = _som(_mix(_varredura(880, 280, 0.12, "quad", 0.30),
                          _tom(1, 0.05, "ruido", 0.18, 4)))
    s["fincar"] = _som(_tom(150, 0.09, "quad", 0.45, 5))
    s["pulo"] = _som(_varredura(300, 720, 0.12, "tri", 0.28))
    s["coleta"] = _som(_seq(_tom(660, 0.06, "tri", 0.30, 3), _tom(990, 0.10, "tri", 0.30, 3)))
    s["acerto"] = _som(_mix(_tom(1, 0.06, "ruido", 0.32, 3), _tom(220, 0.06, "quad", 0.25, 4)))
    s["morte"] = _som(_mix(_tom(1, 0.22, "ruido", 0.40, 3), _varredura(420, 70, 0.20, "quad", 0.28)))
    s["dano"] = _som(_varredura(520, 110, 0.18, "quad", 0.35))
    s["forja"] = _som(_mix(_tom(1318, 0.28, "quad", 0.22, 6), _tom(659, 0.28, "tri", 0.22, 4)))
    s["moeda"] = _som(_seq(_tom(1047, 0.05, "quad", 0.22, 3), _tom(1568, 0.11, "quad", 0.22, 3)))
    s["cura"] = _som(_seq(_tom(523, 0.07, "tri", 0.26, 2), _tom(659, 0.07, "tri", 0.26, 2),
                          _tom(784, 0.13, "tri", 0.26, 2)))
    s["porta"] = _som(_mix(_tom(392, 0.30, "tri", 0.18, 2), _tom(494, 0.30, "tri", 0.16, 2),
                           _tom(587, 0.30, "tri", 0.16, 2)))
    s["clique"] = _som(_tom(880, 0.03, "quad", 0.16, 3))
    s["pronto"] = _som(_seq(_tom(990, 0.04, "quad", 0.18, 3), _tom(1319, 0.07, "quad", 0.18, 3)))

    # musiquinhas de fundo (frases curtas em la menor, tocadas em loop)
    vila = _frase([220, 0, 262, 330, 392, 330, 262, 0,
                   196, 0, 247, 294, 330, 294, 247, 0], bpm=84, tipo="tri", vol=0.12)
    fase = _frase([165, 165, 0, 196, 220, 0, 196, 165,
                   147, 147, 0, 196, 247, 220, 196, 0], bpm=110, tipo="quad", vol=0.07)
    s["musica_vila"] = _som(vila)
    s["musica_menu"] = s["musica_vila"]   # mesmo clima, sem gastar memoria a toa
    s["musica_fase"] = _som(fase)
    return s


def iniciar():
    """Liga o mixer e gera os sons. Chamar uma vez, depois do pygame.init()."""
    global _ok, _sons, _canal_musica, _estereo
    if _sons:
        return
    try:
        pygame.mixer.init(TAXA, -16, 1, 512)
    except pygame.error:
        _ok = False
        return
    real = pygame.mixer.get_init()
    if real is None:
        _ok = False
        return
    _estereo = (real[2] == 2)
    _sons = _gerar_tudo()
    pygame.mixer.set_num_channels(12)
    pygame.mixer.set_reserved(1)          # canal 0 fica so pra musica
    _canal_musica = pygame.mixer.Channel(0)
    _ok = True


def tocar(nome, volume=1.0):
    if _ok and not _mudo and nome in _sons:
        canal = _sons[nome].play()
        if canal is not None and volume < 1.0:
            canal.set_volume(volume)


def musica(nome):
    """Troca o loop de fundo. None para silencio."""
    global _musica_atual
    if not _ok or nome == _musica_atual:
        return
    _musica_atual = nome
    _canal_musica.stop()
    if nome:
        _canal_musica.play(_sons["musica_" + nome], loops=-1, fade_ms=400)
        _canal_musica.set_volume(0.0 if _mudo else 1.0)


def alternar_mudo():
    global _mudo
    _mudo = not _mudo
    if _ok and _canal_musica is not None:
        _canal_musica.set_volume(0.0 if _mudo else 1.0)
    return _mudo


def esta_mudo():
    return _mudo
