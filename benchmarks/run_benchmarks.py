import time
import random
import csv
import math
import statistics
import gc # Importa o Garbage Collector

from dijkstra_com_fibonacci import dijkstra_com_fibonacci
from dijkstra_baseline_heapq import dijkstra_baseline_heapq

REPETICOES = 10
WARMUP_RUNS = 1 # Descarta a primeira execução
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
# ----------------------------------------------------

def gerar_grafo(num_vertices, num_arestas):
    """
    Gera um grafo aleatório usando o modelo G(V, E=m)
    G: Dicionário de adjacência {u: [(v, peso), ...]}
    Gera grafos não-dirigidos.
    """
    G = {i: [] for i in range(num_vertices)}
    
    arestas_adicionadas = 0
    max_iter = num_arestas * 5 # Segurança para evitar loop infinito
    
    # Garante conectividade mínima (caminho simples 0->1->2...)
    for i in range(num_vertices - 1):
        if arestas_adicionadas < num_arestas:
            peso = random.randint(1, 100)
            G[i].append((i+1, peso))
            G[i+1].append((i, peso)) # Não-dirigido
            arestas_adicionadas += 1

    # Adiciona arestas aleatórias restantes
    while arestas_adicionadas < num_arestas and max_iter > 0:
        u = random.randint(0, num_vertices - 1)
        v = random.randint(0, num_vertices - 1)
        
        if u != v and not any(neighbor == v for neighbor, _ in G[u]):
            peso = random.randint(1, 100)
            G[u].append((v, peso))
            G[v].append((u, peso)) # Não-dirigido
            arestas_adicionadas += 1
        
        max_iter -= 1
            
    return G

def executar_teste():
    resultados = []
    
    print(f"=== INICIANDO BENCHMARKS v3 (Rigoroso) ===")
    print(f"Repetições por teste: {REPETICOES} (após {WARMUP_RUNS} warm-up). Semente: {RANDOM_SEED}.")
    print("Isso pode demorar MUITO tempo.")

    # --- Cenário 1: ESPARSO (E = 2V) ---
    tamanhos_esparsos = [10, 100, 500, 1000, 2000, 5000]
    
    print("\n--- Rodando Cenário: ESPARSO (E = 2V) ---")
    for v in tamanhos_esparsos:
        e = 2 * v
        print(f"Gerando e testando V={v}, E={e}...", end=" ", flush=True)
        G = gerar_grafo(v, e)
        
        tempos_fib, tempos_bin = [], []
        fib_extracts, fib_decreases = [], []
        bin_extracts, bin_inserts = [], []

        for i in range(REPETICOES + WARMUP_RUNS):
            gc.collect()
            
            # Teste Fibonacci
            inicio = time.perf_counter()
            _, _, fib_counts = dijkstra_com_fibonacci(G, 0)
            fim = time.perf_counter()
            
            if i >= WARMUP_RUNS:
                tempos_fib.append(fim - inicio)
                fib_extracts.append(fib_counts['extract_min'])
                fib_decreases.append(fib_counts['decrease_key'])

            gc.collect()
            # Teste Binary Heap (Baseline)
            inicio = time.perf_counter()
            _, _, bin_counts = dijkstra_baseline_heapq(G, 0)
            fim = time.perf_counter()

            if i >= WARMUP_RUNS:
                tempos_bin.append(fim - inicio)
                bin_extracts.append(bin_counts['extract_min'])
                bin_inserts.append(bin_counts['insert_relax'])
        
        # Calcular estatísticas
        resultados.append([
            "Esparso", v, e,
            statistics.mean(tempos_fib), statistics.stdev(tempos_fib) if REPETICOES > 1 else 0,
            statistics.mean(tempos_bin), statistics.stdev(tempos_bin) if REPETICOES > 1 else 0,
            statistics.mean(fib_extracts), statistics.mean(fib_decreases),
            statistics.mean(bin_extracts), statistics.mean(bin_inserts)
        ])
        print(f"Fib: {statistics.mean(tempos_fib):.4f}s, Bin: {statistics.mean(tempos_bin):.4f}s")


    # --- Cenário 2: DENSO (E ≈ 0.4 * V^2) ---
    tamanhos_densos = [10, 100, 200, 300, 400, 500]
    
    print("\n--- Rodando Cenário: DENSO (E ≈ 0.4 * V^2) ---")
    for v in tamanhos_densos:
        e = int(0.4 * v * (v - 1) / 2) # /2 pois é não-dirigido
        print(f"Gerando e testando V={v}, E={e}...", end=" ", flush=True)
        G = gerar_grafo(v, e)
        
        tempos_fib, tempos_bin = [], []
        fib_extracts, fib_decreases = [], []
        bin_extracts, bin_inserts = [], []

        for i in range(REPETICOES + WARMUP_RUNS):
            gc.collect()
            inicio = time.perf_counter()
            _, _, fib_counts = dijkstra_com_fibonacci(G, 0)
            fim = time.perf_counter()
            if i >= WARMUP_RUNS:
                tempos_fib.append(fim - inicio)
                fib_extracts.append(fib_counts['extract_min'])
                fib_decreases.append(fib_counts['decrease_key'])

            gc.collect()
            inicio = time.perf_counter()
            _, _, bin_counts = dijkstra_baseline_heapq(G, 0)
            fim = time.perf_counter()
            if i >= WARMUP_RUNS:
                tempos_bin.append(fim - inicio)
                bin_extracts.append(bin_counts['extract_min'])
                bin_inserts.append(bin_counts['insert_relax'])

        # Calcular estatísticas
        resultados.append([
            "Denso", v, e,
            statistics.mean(tempos_fib), statistics.stdev(tempos_fib) if REPETICOES > 1 else 0,
            statistics.mean(tempos_bin), statistics.stdev(tempos_bin) if REPETICOES > 1 else 0,
            statistics.mean(fib_extracts), statistics.mean(fib_decreases),
            statistics.mean(bin_extracts), statistics.mean(bin_inserts)
        ])
        print(f"Fib: {statistics.mean(tempos_fib):.4f}s, Bin: {statistics.mean(tempos_bin):.4f}s")


    filename = "benchmark_resultados.csv"
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Tipo", "Vertices", "Arestas", 
            "Tempo_Fib_Mean_s", "Tempo_Fib_Std_s", 
            "Tempo_Bin_Mean_s", "Tempo_Bin_Std_s",
            "Fib_Extracts", "Fib_Decreases",
            "Bin_Extracts", "Bin_Inserts"
        ])
        writer.writerows(resultados)
    
    print(f"\nTeste finalizado! Resultados salvos em '{filename}'.")

if __name__ == "__main__":
    executar_teste()