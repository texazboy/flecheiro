# Flecheiro 🏹

Jogo **side-scroller** de plataforma em pixel art onde um arqueiro atravessa as
fases derrotando inimigos e usando as **próprias flechas como plataformas** para
escalar. Entre as fases há uma vila com NPCs, onde dá pra forjar arcos melhores
e negociar os itens coletados.

O jogo foi feito para a atividade *"Desenvolvimento de Jogo com Algoritmos
Computacionais"* e usa três algoritmos clássicos como mecânica de verdade (não só
"encaixados"): **TSP**, **Mochila 0/1** e **Quicksort**.

## Integrantes

- José Gabriel Dâmaso
- Pedro Augusto Ferreira de Oliveira
- Matheus dos Santos Tenório
- Matheus Vasconcelos Soares da Silva

## Gênero

Plataforma / aventura 2D (side-scroller). **Não é survivor.**

## Como rodar

Precisa de **Python 3.10+** (testado no 3.14). No Windows:

```powershell
# 1. (opcional, recomendado) criar um ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. instalar a dependência (pygame-ce, o fork mantido do pygame)
python -m pip install -r requirements.txt

# 3. rodar
python main.py
```

No Linux/Mac é igual, trocando a ativação do venv por `source .venv/bin/activate`.

## Controles

| Ação | Tecla |
|------|-------|
| Andar | `A` / `D` ou setas |
| Pular | `Espaço` (ou `W` / seta para cima) |
| Atirar | **segurar** o botão esquerdo tensiona o arco; **soltar** dispara |
| Coletar itens próximos | `E` |
| Mostrar rota ótima de coleta (TSP) | `T` |
| Abrir/fechar inventário | `I` (ou `Tab`) |
| Conversar com NPC / seguir viagem (na vila) | `E` |
| Pausar | `Esc` |
| Som liga/desliga | `M` |

Quanto mais tempo o arco fica tensionado, mais longe (e mais forte) a flecha
vai — a trajetória pontilhada mostra exatamente onde ela cai. Ao bater numa
estrutura, a flecha **finca e vira uma pequena plataforma**: é assim que se
escala a parede da fase 2 e se atravessam os vãos da fase 3 (a flecha fincada
na beirada funciona de ponte).

São **três fases** (dia, poente e noite), com a vila entre elas. Inimigos
terrestres patrulham o chão e morcegos rondam os pontos altos. Derrotar
inimigos solta **moedas** (coleta automática, com efeito ímã) além dos
materiais; **baús de tesouro** escondidos nos pontos altos guardam materiais
raros, e **placas** pelo caminho dão dicas (leia com `E`). Os efeitos sonoros
e a música de fundo são gerados pelo próprio código (sem arquivos de áudio).

## Algoritmos implementados (e onde aparecem)

| Algoritmo | Onde está no jogo | Arquivo |
|-----------|-------------------|---------|
| **TSP** (Held-Karp exato + heurística 2-opt) | overlay `T` mostra a menor rota para coletar todos os itens da fase e voltar | [`algoritmos/tsp.py`](algoritmos/tsp.py) |
| **Mochila 0/1** (programação dinâmica) | ferraria: escolhe os melhores materiais dentro da capacidade da bigorna para forjar o arco | [`algoritmos/mochila.py`](algoritmos/mochila.py) |
| **Quicksort** | ordenação do inventário por valor / peso / raridade | [`algoritmos/ordenacao.py`](algoritmos/ordenacao.py) |

A estrutura de dados do **inventário** (adicionar/remover/consultar em O(1)) está
em [`core/inventario.py`](core/inventario.py).

Os detalhes e a justificativa de cada escolha estão em
[`docs/DOCUMENTACAO.md`](docs/DOCUMENTACAO.md).

## Estrutura do projeto

```
.
├── main.py                 # loop principal e janela
├── config.py               # constantes (resolução, física, cores)
├── algoritmos/             # os algoritmos puros (sem pygame) e testáveis
│   ├── tsp.py              #   Caixeiro Viajante
│   ├── mochila.py          #   Mochila 0/1
│   └── ordenacao.py        #   Quicksort
├── core/                   # peças centrais
│   ├── estados.py          #   base da máquina de estados (telas)
│   ├── camera.py           #   câmera do side-scroller (conversão de coordenadas)
│   ├── recursos.py         #   carrega sprites/animações/tiles (com fallback)
│   ├── animacao.py         #   sistema de animação por spritesheet
│   ├── cenario.py          #   céu com gradiente, parallax e terreno pré-renderizado
│   ├── som.py              #   efeitos sonoros e música gerados em código (chiptune)
│   ├── inventario.py       #   estrutura de dados do inventário
│   └── mundo.py            #   estado que persiste entre as fases
├── entidades/              # jogador, flecha, inimigo, item
├── fases/                  # fases de ação e a vila dos NPCs
├── telas/                  # HUD, inventário, diálogo, ferraria, loja, menu
├── testes/                 # testes automáticos dos algoritmos + smoke test
└── assets/                 # sprites (.png) — opcional, ver assets/LEIA-ME.txt
```

## Testes

Testes unitários dos algoritmos e do inventário (não precisam de janela):

```powershell
python -m unittest discover -s testes -p "test_*.py" -v
```

Smoke test que roda o jogo inteiro sem abrir janela (verifica que nenhuma tela
quebra em tempo de execução):

```powershell
python testes/smoke_jogo.py
```

## Sprites e arte

O jogo **roda sem nenhum sprite**: quando um arquivo não é encontrado, o código
gera um placeholder (inclusive **animado**) e desenha o cenário (chão, plataformas
e fundo com parallax) de forma procedural. Para usar arte de verdade:

- **Personagens animados:** spritesheets em tira horizontal, ex.: `jogador_andar_6.png`,
  `inimigo_andar_4.png` (o nº no fim é a quantidade de quadros).
- **Sprites simples:** `flecha.png`, `item_*.png`, `npc_*.png`.
- **Cenário:** `tile_grama.png`, `tile_terra.png`, `tile_plataforma.png` (16×16) e
  `fundo.png` (opcional).

A arte é **escalada automaticamente** para o tamanho certo, então não precisa ser
pixel-exata. A lista completa de nomes e as regras estão em
[`assets/LEIA-ME.txt`](assets/LEIA-ME.txt). Use sprites de **domínio público / CC0**
e cite a fonte nos créditos.

## Créditos

- Código: os quatro integrantes acima.
- Arte (todos pacotes gratuitos):
  - Personagem **Huntress** — *LuizMelo* (CC0) — [itch.io](https://luizmelo.itch.io/huntress)
  - Inimigos (slime e morcego) — pacote *Monsters Creatures Fantasy 2* (gratuito)
  - Baú e moedas — **Treasure Hunters**, *Pixel Frog* (CC0) — [itch.io](https://pixelfrog-assets.itch.io/treasure-hunters)
  - Cenário de fundo — **Grassy Mountains**, *vnitti* — [itch.io](https://vnitti.itch.io/grassy-mountains-parallax-background)
  - Props da vila (árvore, poço, poste, banco...) — **Village Props**, *Cainos* — [itch.io](https://cainos.itch.io/pixel-art-platformer-village-props)
- O que não vem de pacote (NPCs, itens, tiles, interface) é desenhado
  proceduralmente pelo próprio jogo.
- Feito com [pygame-ce](https://pyga.me/).
