
# Fibonacci Heaps and van Emde Boas Trees

Implementação educacional das estruturas de dados avançadas descritas nos Capítulos 19 e 20 de Cormen et al. (2012).

## Autores
- Ahmed Amer Hachem
- Álvaro Augusto José Silva
- Bernardo Silva Andrade
- Deivy Rossi Teixeira de Melo
- João Pedro Silva Siqueira
- João Vitor Lobato Romualdo
- Lucas Roseno Medeiros Araújo
- Luiz Fernando dos Santos Queiroz
- Thallys Eduardo Dias Lamounier

## Estrutura do Repositório
```
├── fibonacci/
│   ├── fibonacci_heap.py       # Implementação do Heap de Fibonacci
│   ├── dijkstra_com_fibonacci.py
│   └── dijkstra_baseline_heapq.py
├── arvore_vEB/
│   ├── vEB_tree.py              # Implementação da Árvore vEB
│   └── run_benchmark.py         # Benchmark Fila de Prioridade em Universo Limitado 
└── benchmarks/
    ├── run_benchmarks.py        # Benchmark Dijkstra
    └── benchmark_resultados.csv
```

## Requisitos
```bash
pip install matplotlib
```

Python 3.8+

## Execução

### Dijkstra (Fibonacci vs Binary Heap)
```bash
cd benchmarks
python3 run_benchmarks.py
```

### vEB vs Heap Binário
```bash
cd arvore_vEB
python3 run_benchmark.py
```

## Tabela Comparativa

| Estrutura         | Chaves          | INSERT      | EXTRACT-MIN | DECREASE-KEY | Espaço | Uso Ideal                     |
|-------------------|-----------------|-------------|-------------|--------------|--------|-------------------------------|
| Fibonacci Heap    | Qualquer        | O(1)†       | O(lg n)†    | O(1)†        | O(n)   | Grafos densos (V>10³, E≈V²)  |
| van Emde Boas     | [0, u-1]        | O(lg lg u)* | O(lg lg u)* | N/A          | O(u)   | Universo limitado, tempo real |
| Heap Binário      | Qualquer        | O(lg n)     | O(lg n)     | O(lg n)      | O(n)   | Uso geral (prático)           |

† Tempo amortizado  
\* Tempo no pior caso

### Quando Usar Cada Estrutura?

**Fibonacci Heap**: 
- Algoritmos de grafos massivos (Dijkstra, Prim) com E >> V lg V
- Exemplo: Malhas 3D com |V| > 10⁴, E ≈ V²
- **Trade-off**: Alto overhead (~47x mais lento em grafos esparsos)

**van Emde Boas**:
- Sistemas de tempo real com universo limitado [0, u-1]
- Roteamento IP (longest prefix match), tabelas de símbolo inteiras
- **Trade-off**: Espaço O(u), apenas chaves inteiras (~40x mais lento para N<1k)

**Heap Binário**:
- **Padrão para 99% dos casos práticos**
- Vantagens: Simples, cache-friendly, constantes baixas
- Use a menos que precise das garantias teóricas acima

## Resultados Experimentais

### Dijkstra (Grafos Densos, V=500, E≈50k)
- Fibonacci: 0.0115s (média)
- Binário: 0.0102s (média)
- **Crossover não atingido**: Fibonacci se aproxima mas ainda é 12% mais lento

### vEB (U=2²⁴, N=262k)
- vEB: 3.6097s (média)
- Heapq: 0.4303s (média)
- **Crossover estimado**: N > 2²² (≈4 milhões)

## Referências

1. CORMEN et al. *Algoritmos: Teoria e Prática*. 3ª ed. Elsevier, 2012.
2. FREDMAN & TARJAN. *Fibonacci heaps and their uses*. JACM, 1987.
3. VAN EMDE BOAS et al. *Design and implementation*. Math Systems Theory, 1977.

## Licença

Código educacional para disciplina de Algoritmos e Estrutura de Dados II (CEFET-MG).
