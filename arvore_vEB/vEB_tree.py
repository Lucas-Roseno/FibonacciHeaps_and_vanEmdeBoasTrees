# vEB_tree.py

import math

class vEB:
    def __init__(self, universe_size):
        # Arredonda U para a próxima potência de 2
        if universe_size <= 2:
            self.U = 2
        else:
            # Encontra a potência de 2
            # (usamos bit_length - 1 para lidar com potências de 2 exatas)
            power = (universe_size - 1).bit_length()
            self.U = 1 << int(power) # 1 << power é 2^power
            # Se o tamanho original não era uma potência de 2, precisamos da próxima
            if self.U < universe_size:
                self.U = self.U << 1
        
        self.min_val = None
        self.max_val = None

        # Caso base da recursão
        if self.U > 2:
            # Pre-calcula os tamanhos para divisão
            half_power = (self.U.bit_length() - 1) // 2
            self.l_sqrt_U = 1 << half_power       # 2^(floor(log/2))
            self.u_sqrt_U = 1 << ((self.U.bit_length() - 1) - half_power) # 2^(ceil(log/2))

            # Cria o summary e os clusters (como dicionários)
            self.summary = vEB(self.u_sqrt_U)
            self.clusters = {} # Dicionário para clusters esparsos

    # --- Funções Auxiliares ---
    def high(self, x):
        return x // self.l_sqrt_U

    def low(self, x):
        return x % self.l_sqrt_U

    def index(self, h, l):
        return h * self.l_sqrt_U + l

    # --- Operações Principais ---
    
    def get_min(self):
        return self.min_val

    def get_max(self):
        return self.max_val

    def insert(self, x):
        # 1. Árvore está vazia
        if self.min_val is None:
            self.min_val = self.max_val = x
            return

        # 2. Se x é o novo mínimo, troque x com min_val
        if x < self.min_val:
            x, self.min_val = self.min_val, x

        # 3. A recursão só continua se U > 2
        if self.U > 2:
            h = self.high(x)
            l = self.low(x)

            # 4. Se o cluster 'h' está vazio
            if h not in self.clusters:
                # Insere 'h' no summary
                self.summary.insert(h)
                # Cria o novo cluster
                self.clusters[h] = vEB(self.l_sqrt_U)
                # Insere 'l' no novo cluster
                self.clusters[h].insert(l)
            else:
                # 5. Se o cluster já existe
                self.clusters[h].insert(l)

        # 6. Atualiza o máximo
        if x > self.max_val:
            self.max_val = x

    def successor(self, x):
        # 1. Caso base U=2
        if self.U == 2:
            if x == 0 and self.max_val == 1: return 1
            else: return None

        # 2. Se x < min, sucessor é o min
        if self.min_val is not None and x < self.min_val:
            return self.min_val

        h = self.high(x)
        l = self.low(x)

        # 3. Tentar encontrar sucessor DENTRO do cluster de x
        max_in_cluster_obj = self.clusters.get(h, None)
        
        if max_in_cluster_obj is not None:
             max_in_cluster_val = max_in_cluster_obj.get_max()
             if max_in_cluster_val is not None and l < max_in_cluster_val:
                succ_low = max_in_cluster_obj.successor(l)
                if succ_low is not None:
                    return self.index(h, succ_low)
        
        # 4. Se não, procure o PRÓXIMO cluster
        succ_cluster_idx = self.summary.successor(h)
        if succ_cluster_idx is None:
            return None # Sem sucessor

        # 5. O sucessor é o MENOR elemento do próximo cluster
        succ_low = self.clusters[succ_cluster_idx].get_min()
        return self.index(succ_cluster_idx, succ_low)
        
    def extract_min(self):
        if self.min_val is None:
            return None

        min_to_return = self.min_val

        # 1. Se min == max, a árvore fica vazia
        if self.min_val == self.max_val:
            self.min_val = self.max_val = None
            return min_to_return

        # 2. Caso Base U=2
        if self.U == 2:
            # min_val era 0, max_val era 1
            self.min_val = self.max_val # O min se torna o max (que era 1)
            return min_to_return # Retorna 0

        # 3. Encontrar o próximo menor elemento para ser o novo min_val
        first_cluster_idx = self.summary.get_min()
        
        # Se summary está vazio, só tínhamos min_val e max_val
        if first_cluster_idx is None:
            self.min_val = self.max_val # O novo min é o max
            return min_to_return

        # 4. O novo min_val é o menor elemento do primeiro cluster
        new_min_low = self.clusters[first_cluster_idx].extract_min()
        self.min_val = self.index(first_cluster_idx, new_min_low)
        
        # 5. Limpeza: Se o cluster ficou vazio
        if self.clusters[first_cluster_idx].get_min() is None:
            self.summary.extract_min() # Remove o cluster do summary
            del self.clusters[first_cluster_idx] # Deleta o cluster

        return min_to_return