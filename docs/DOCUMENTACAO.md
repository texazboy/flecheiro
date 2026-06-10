# Documentação — escolhas algorítmicas

Este documento justifica os algoritmos usados no **Flecheiro** e explica como
cada um foi integrado à jogabilidade (não apenas "encaixado"). Todos os
algoritmos ficam isolados no pacote [`algoritmos/`](../algoritmos), sem nenhuma
dependência do pygame, o que permite testá-los direto no terminal.

---

## 1. Problema do Caixeiro Viajante (TSP) — requisito 2.1

**Onde aparece:** na fase de ação, a tecla `T` liga um overlay que desenha a
**menor rota** para o jogador recolher todos os itens espalhados e voltar ao
ponto de partida. É exatamente o exemplo citado no enunciado ("rota ótima de
coleta").

**Por que TSP é interessante:** é um problema **NP-difícil**. Não se conhece
algoritmo de tempo polinomial que resolva o caso geral, então ele é perfeito
para discutir o trade-off entre **solução exata** (correta, mas que cresce
exponencialmente) e **heurística** (rápida, mas sem garantia de ótimo).

### Solução exata — Held-Karp (programação dinâmica)

Em vez de testar todas as `(n-1)!` permutações (força bruta), usamos a
programação dinâmica de Held-Karp. O estado é:

> `dp[S][j]` = menor custo de um caminho que começa no ponto 0, visita
> exatamente o conjunto de pontos `S` e termina no ponto `j`.

A recorrência expande o conjunto adicionando um próximo ponto `k`:

> `dp[S ∪ {k}][k] = min sobre j em S de ( dp[S][j] + dist(j, k) )`

No fim, fechamos o ciclo voltando ao ponto 0:
`custo = min_j ( dp[todos][j] + dist(j, 0) )`.

- **Complexidade de tempo:** `O(n² · 2ⁿ)`
- **Complexidade de espaço:** `O(n · 2ⁿ)`

É exponencial, mas viável para `n` pequeno. Medimos `n = 15` rodando em ~0,13 s,
o que é ótimo para um cálculo feito **sob demanda** (só quando o jogador aperta
`T`).

### Heurística — vizinho mais próximo + 2-opt

Quando há mais de 15 pontos, trocamos para uma heurística:

1. **Vizinho mais próximo:** começa no ponto 0 e sempre vai para o ponto mais
   perto ainda não visitado. Rápido (`O(n²)`), mas costuma deixar "cruzamentos"
   na rota.
2. **2-opt:** melhora a rota desfazendo cruzamentos — inverte trechos enquanto
   isso diminuir o custo total. Usamos cálculo de *delta* (só as 4 arestas que
   mudam) para não recalcular a rota inteira a cada tentativa.

A heurística não garante o ótimo, mas na prática chega bem perto, em tempo
polinomial.

### O limite (15)

O corte entre exato e heurístico está em `LIMITE_EXATO = 15`
([`tsp.py`](../algoritmos/tsp.py)), seguindo a sugestão do enunciado. Abaixo
disso a resposta é perfeita; acima, priorizamos a rapidez.

---

## 2. Mochila 0/1 (Knapsack) — requisito 2.4 (segundo problema)

**Onde aparece:** na **ferraria** da vila. A bigorna tem uma **capacidade máxima
de peso** por forja. Cada material coletado tem um peso e um valor (quanto
agrega de qualidade ao arco). Forjar = escolher **quais materiais usar** para
maximizar a qualidade sem estourar a capacidade. Como cada material entra ou não
(não dá pra usar "meio material"), isso é a **mochila 0/1**.

A qualidade obtida define o arco resultante (Reforçado → de Caça → Élfico →
Lendário), então a decisão do algoritmo tem efeito direto e visível no jogo.

### Solução — programação dinâmica

> `dp[i][c]` = melhor valor usando os primeiros `i` itens com capacidade `c`.

Para cada item, escolhemos o melhor entre **não usá-lo** (`dp[i-1][c]`) e
**usá-lo**, se couber (`dp[i-1][c - peso] + valor`). Depois fazemos
*backtracking* na tabela para descobrir **quais** itens entraram.

- **Complexidade:** `O(n · W)` (pseudo-polinomial; `W` = capacidade).

### Por que não o guloso?

O guloso (ordenar por razão valor/peso e ir pegando) é mais rápido, mas **não
garante o ótimo** no caso 0/1. Exemplo real (está nos testes):

| Item | peso | valor |
|------|------|-------|
| A | 1 | 2 |
| B | 3 | 5 |
| C | 3 | 5 |

Com capacidade 6, o guloso pega A primeiro (melhor razão) e sobra espaço só para
um dos outros → valor 7. A solução ótima é B + C → **valor 10**. Por isso o jogo
usa a DP. A versão gulosa fica implementada e é **mostrada na tela da ferraria**,
lado a lado, justamente para evidenciar esse trade-off.

---

## 3. Quicksort — ordenação do inventário (problema extra)

**Onde aparece:** na tela do inventário (`I`), o jogador reordena os itens por
**valor, peso ou raridade**. Em vez do `sorted()` pronto, implementamos o
Quicksort à mão ([`ordenacao.py`](../algoritmos/ordenacao.py)) para deixar o
algoritmo clássico explícito.

- **Complexidade:** `O(n log n)` no caso médio, `O(n²)` no pior caso (pivô ruim).
  Para um inventário pequeno é mais que suficiente.

---

## 4. Estrutura de dados do inventário — requisito 2.2

Em [`core/inventario.py`](../core/inventario.py). Por dentro é um **dicionário**
(`chave do material → [material, quantidade]`), o que dá:

- `adicionar`, `remover`, `consultar`: **O(1)** em média (acesso por hash).
- `expandir()`: devolve uma unidade por item (lista achatada), usado para
  alimentar a mochila da ferraria, onde cada unidade pode entrar ou não.

A coleta (requisito 2.3) é feita por **interação**: o jogador encosta nos itens
e aperta `E` para recolhê-los — não basta o inventário existir, é preciso
interagir com o mundo para preenchê-lo.

---

## 5. Testes

Os algoritmos são verificados em [`testes/`](../testes):

- **TSP:** o Held-Karp é comparado com **força bruta** (todas as permutações)
  para `n` pequeno — tem que dar exatamente o mesmo custo ótimo. A heurística é
  validada como permutação válida e nunca melhor que o ótimo.
- **Mochila:** a DP é comparada com **força bruta** (todos os subconjuntos),
  sempre respeita a capacidade e nunca é pior que o guloso.
- **Inventário e Quicksort:** operações básicas e ordenação comparada com o
  `sorted()` da linguagem.

Rodar tudo:

```powershell
python -m unittest discover -s testes -p "test_*.py" -v
```
