# run_benchmark.py
#
import time
import random
import sys
import heapq # Baseline (Heap Binário) 
import matplotlib.pyplot as plt
import gc # Importa o Garbage Collector 
import os # Para criar o diretório

# Importa a classe vEB do outro arquivo
from vEB_tree import vEB

# Aumenta o limite de recursão para a vEB 
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
        gc.collect() # Limpa a memória antes de cada execução [
        tree = vEB(universe_size)
        
        start_time = time.perf_counter() # 
        
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
        
        start_time = time.perf_counter() # 
        
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

# --- CONFIGURAÇÃO DO EXPERIMENTO ---

# Universo Fixo (conforme texto do relatório, 2^24)
U = 2**24 # 
print(f"Universo (U) fixado em: {U}")

# Valores de N (número de elementos) para testar
# (Potências de 2, de 2^10 até 2^18)
N_values = [2**k for k in range(10, 19)] 
# [1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144]


# Listas para guardar os resultados
veb_times = []
heap_times = []

# Seed para reprodutibilidade 
random.seed(42)

print("Iniciando benchmark (isso pode demorar)...")

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

print("Benchmark concluído. Gerando gráfico...")

# --- GERAÇÃO DO GRÁFICO (Figura 9) ---

plt.figure(figsize=(10, 6))
# Usar escala LOGARÍTMICA nos dois eixos é melhor para ver tendências
plt.plot(N_values, veb_times, 'o-', label=f'vEB (U={U}, O(N log log U))')
plt.plot(N_values, heap_times, 's-', label='Heap Binário (heapq, O(N log N))')

plt.xlabel('Número de Elementos (N)')
plt.ylabel('Tempo Médio de Execução (segundos)')
plt.title(f'vEB vs. Heap Binário (U={U}): N Inserções + N Extrações')
plt.legend()
plt.grid(True, which="both", linestyle='--', alpha=0.6) # "both" para grid em log

# Define os eixos para escala LOGARÍTMICA 
plt.xscale('log', base=2) # Base 2 para o eixo N
plt.yscale('log', base=10) # Base 10 para o tempo

# Garante que todos os ticks do eixo X apareçam
plt.xticks(N_values, [f'$2^{{{k}}}$' for k in range(10, 19)]) 

# --- Salvando o Gráfico ---

# Cria o diretório 'images' se ele não existir
output_dir = 'images'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_filename = os.path.join(output_dir, 'plot_veb_vs_heap_v1.png')
plt.savefig(output_filename)

print(f"Gráfico salvo como: {output_filename}")

# Mostra o gráfico na tela
plt.show()