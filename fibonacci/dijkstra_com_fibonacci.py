from fibonacci_heap import FibonacciHeap, Node
import math

def dijkstra_com_fibonacci(G, source):

    # Contadores para verificação de sanidade (Ponto 4 do Feedback)
    counts = {
        'extract_min': 0,
        'decrease_key': 0
    }

    distancias = {}
    predecessores = {}
    node_map = {} 
    
    H = FibonacciHeap()

    for u in G:
        distancias[u] = math.inf
        predecessores[u] = None
        
    distancias[source] = 0
    
    for u in G:
        node = H.insert(key=distancias[u], payload=u)
        node_map[u] = node

    # O laço principal do Dijkstra
    while H.min is not None:
        
        # 1. Contar EXTRACT-MIN
        counts['extract_min'] += 1
        u_node = H.extract_min()
        u = u_node.payload
        
        if u not in G:
            continue

        for v, peso in G[u]:
            nova_distancia = distancias[u] + peso
            
            if distancias[v] > nova_distancia:
                distancias[v] = nova_distancia
                predecessores[v] = u
                
                # 2. Contar DECREASE-KEY
                counts['decrease_key'] += 1
                v_node_para_atualizar = node_map[v]
                H.decrease_key(v_node_para_atualizar, nova_distancia)

    return distancias, predecessores, counts