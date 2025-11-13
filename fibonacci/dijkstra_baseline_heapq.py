import heapq
import math

def dijkstra_baseline_heapq(G, source):


    counts = {
        'extract_min': 0,
        'insert_relax': 0 # Contamos os "push" no relaxamento
    }
    
    distancias = {}
    predecessores = {}
    H = [] 

    for u in G:
        distancias[u] = math.inf
        predecessores[u] = None
        
    distancias[source] = 0
    heapq.heappush(H, (0, source))

    while H:
        
        # 1. Contar EXTRACT-MIN
        counts['extract_min'] += 1
        (dist_u, u) = heapq.heappop(H)
        
        if dist_u > distancias[u]:
            continue
        
        if u not in G:
            continue
            
        for v, peso in G[u]:
            nova_distancia = distancias[u] + peso
            
            if distancias[v] > nova_distancia:
                distancias[v] = nova_distancia
                predecessores[v] = u
                
                # 2. Contar o INSERT (que substitui o DECREASE-KEY)
                counts['insert_relax'] += 1
                heapq.heappush(H, (nova_distancia, v))

    return distancias, predecessores, counts