# run_benchmark.py

import time
import random
import sys
import heapq 
import matplotlib.pyplot as plt
import gc 


from vEB_tree import vEB


sys.setrecursionlimit(40000)

def benchmark_veb(universe_size, elements):
    """
    Testa N inserções + N extrações de mínimo na vEB.
    Retorna o tempo total.
    """
    
    # 1. Warm-up run (descartada)
    gc.collect() # Limpa a memória
    tree_warmup = vEB(universe_size)
    for k in elements:
        tree_warmup.insert(k)
    for _ in range(len(elements)):
        tree_warmup.extract_min()
    del tree_warmup # Libera a memória
    
    # 2. Medição Real (Média de N=10)
    total_time = 0
    N_EXECUTIONS = 10
    
    for _ in range(N_EXECUTIONS):
        gc.collect() # Limpa a memória antes de cada execução
        tree = vEB(universe_size)
        
        start_time = time.perf_counter()
        
        # Fase 1: Inserção
        for k in elements:
            tree.insert(k)
            
        # Fase 2: Extração
        for _ in range(len(elements)):
            tree.extract_min()
            
        end_time = time.perf_counter()
        total_time += (end_time - start_time)
        del tree # Libera a memória

    return total_time / N_EXECUTIONS # Retorna a média

def benchmark_heapq(elements):
    """
    Testa N inserções + N extrações de mínimo no heapq.
    Retorna o tempo total.
    """
    
    # 1. Warm-up run (descartada)
    gc.collect()
    h_warmup = []
    for k in elements:
        heapq.heappush(h_warmup, k)
    for _ in range(len(elements)):
        heapq.heappop(h_warmup)
    del h_warmup

    # 2. Medição Real (Média de N=10)
    total_time = 0
    N_EXECUTIONS = 10

    for _ in range(N_EXECUTIONS):
        gc.collect()
        h = []
        
        start_time = time.perf_counter()
        
        # Fase 1: Inserção
        for k in elements:
            heapq.heappush(h, k)
            
        # Fase 2: Extração
        for _ in range(len(elements)):
            heapq.heappop(h)
            
        end_time = time.perf_counter()
        total_time += (end_time - start_time)
        del h

    return total_time / N_EXECUTIONS # Retorna a média


# Universo Fixo (conforme texto do relatório, 2^24)
U = 2**24 
print(f"Universo (U) fixado em: {U}")

# Valores de N (número de elementos) para testar
# (Potências de 2, de 2^10 até 2^18)
N_values = [2**k for k in range(10, 19)] 


# Listas para guardar os resultados
veb_times = []
heap_times = []

# Seed para reprodutibilidade
random.seed(42)

print("Iniciando benchmark:")

for N in N_values:
    # Gera N chaves aleatórias únicas dentro do universo U
    elements = random.sample(range(U), N)
    
    # --- Roda o Benchmark vEB ---
    print(f"Testando vEB com N = {N}...", end="", flush=True)
    time_veb = benchmark_veb(U, elements)
    veb_times.append(time_veb)
    print(f" {time_veb:.4f}s")
    
    # --- Roda o Benchmark Heapq ---
    print(f"Testando Heapq com N = {N}...", end="", flush=True)
    time_heap = benchmark_heapq(elements)
    heap_times.append(time_heap)
    print(f" {time_heap:.4f}s")

print("Benchmark concluído. Gerando gráfico.")



plt.figure(figsize=(10, 6))

plt.plot(N_values, veb_times, 'o-', label=f'vEB (U={U}, O(N log log U))')
plt.plot(N_values, heap_times, 's-', label='Heap Binário (heapq, O(N log N))')

plt.xlabel('Número de Elementos (N)')
plt.ylabel('Tempo Médio de Execução (segundos)')
plt.title(f'vEB vs. Heap Binário (U={U}): N Inserções + N Extrações')
plt.legend()
plt.grid(True, which="both", linestyle='--', alpha=0.6) 

plt.xscale('log', base=2) 
plt.yscale('log', base=10) 


plt.xticks(N_values, [f'$2^{{{k}}}$' for k in range(10, 19)]) 


output_filename = 'images/plot_veb_vs_heap_v1.png' 

plt.savefig(output_filename)

print(f"Gráfico salvo como: {output_filename}")
plt.show()