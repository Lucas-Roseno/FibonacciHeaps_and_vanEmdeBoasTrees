
import math

class vEB:
    def __init__(self, universe_size):
        # Arredonda U para a próxima potência de 2 
        if universe_size <= 2:
            self.U = 2
        else:
            power = (universe_size - 1).bit_length()
            self.U = 1 << int(power)
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

    def member(self, x):
        
        # Passo 1: Verifica min e max 
        if x == self.min_val or x == self.max_val:
            return True
        
        # Passo 2: Caso base 
        if self.U == 2:
            return False

        # Passo 3: Recurso no cluster 
        h = self.high(x)
        l = self.low(x)

        if h not in self.clusters:
            return False
        else:
            return self.clusters[h].member(l)

    def insert(self, x):
        
        # Caso 1: Árvore está vazia 
        if self.min_val is None:
            self.min_val = self.max_val = x
            return

        # Caso 2: Troca com o mínimo, se necessário 
        if x < self.min_val:
            x, self.min_val = self.min_val, x

        # A recursão só continua se U > 2
        if self.U > 2:
            h = self.high(x)
            l = self.low(x)

            # Caso 3: Inserção no cluster
            # Se o cluster 'h' está vazio
            if h not in self.clusters:
                # Insere 'h' no summary 
                self.summary.insert(h)
                # Cria o novo cluster
                self.clusters[h] = vEB(self.l_sqrt_U)
                # Insere 'l' (min e max) no novo cluster
                self.clusters[h].insert(l)
            else:
                # Se o cluster já existe 
                self.clusters[h].insert(l)

        # Atualiza o máximo 
        if x > self.max_val:
            self.max_val = x

    def successor(self, x):
        
        # 1. Caso base U=2
        if self.U == 2:
            if x == 0 and self.max_val == 1: return 1
            else: return None

        # 2. Caso 1: Se x < min, sucessor é o min 
        if self.min_val is not None and x < self.min_val:
            return self.min_val

        h = self.high(x)
        l = self.low(x)

        # 3. Caso 2: Tentar encontrar sucessor DENTRO do cluster de x 
        max_in_cluster_obj = self.clusters.get(h, None)
        
        if max_in_cluster_obj is not None:
             max_in_cluster_val = max_in_cluster_obj.get_max()
             if max_in_cluster_val is not None and l < max_in_cluster_val:
                succ_low = max_in_cluster_obj.successor(l)
                if succ_low is not None:
                    return self.index(h, succ_low)
        
        # 4. Caso 3: Se não, procure o PRÓXIMO cluster 
        succ_cluster_idx = self.summary.successor(h)
        if succ_cluster_idx is None:
            return None # Sem sucessor

        # 5. O sucessor é o MENOR elemento do próximo cluster
        succ_low = self.clusters[succ_cluster_idx].get_min()
        return self.index(succ_cluster_idx, succ_low)

    def predecessor(self, x):
       
        # 1. Caso base U=2
        if self.U == 2:
            if x == 1 and self.min_val == 0: return 0
            else: return None
        
        # 2. Caso 1: Se x > max, predecessor é o max 
        if self.max_val is not None and x > self.max_val:
            return self.max_val

        h = self.high(x)
        l = self.low(x)

        # 3. Caso 2: Tentar encontrar predecessor DENTRO do cluster 
        min_in_cluster_obj = self.clusters.get(h, None)
        
        if min_in_cluster_obj is not None:
            min_in_cluster_val = min_in_cluster_obj.get_min()
            if min_in_cluster_val is not None and l > min_in_cluster_val:
                pred_low = min_in_cluster_obj.predecessor(l)
                if pred_low is not None:
                    return self.index(h, pred_low)
        
        # 4. Caso 3: Se não, procure o cluster ANTERIOR 
        pred_cluster_idx = self.summary.predecessor(h)

        if pred_cluster_idx is None:
            # 5. Se não há cluster anterior, pode ser o min_val 
            if self.min_val is not None and x > self.min_val:
                return self.min_val
            else:
                return None
        else:
            # 6. O predecessor é o MAIOR elemento do cluster anterior
            pred_low = self.clusters[pred_cluster_idx].get_max()
            return self.index(pred_cluster_idx, pred_low)

    def delete(self, x):
        
        # Caso 1: Único elemento
        if self.min_val == self.max_val:
            if x == self.min_val:
                self.min_val = self.max_val = None
            return

        # Caso 2: Base U=2 
        if self.U == 2:
            if x == 0:
                self.min_val = 1
            else: # x == 1
                self.min_val = 0 # max_val é implicitamente 0
            self.max_val = self.min_val
            return

        # Caso 3: Removendo o mínimo 
        if x == self.min_val:
            first_cluster_idx = self.summary.get_min()
            
            # Se não há clusters, o único outro elemento é o max_val
            if first_cluster_idx is None:
                self.min_val = self.max_val
                return
            
            # Encontra o próximo menor (o min do primeiro cluster)
            l = self.clusters[first_cluster_idx].get_min()
            self.min_val = self.index(first_cluster_idx, l)
            
            # Prepara para deletar 'l' do cluster 'first_cluster_idx'
            h = first_cluster_idx
            x_to_delete_recursively = l
            # O 'x' original (que era o min) agora é tratado como o novo min,
            # para que a lógica de atualização do max no final funcione.
            x = self.min_val 
            
        else: # Caso 4: Remoção normal 
            h = self.high(x)
            x_to_delete_recursively = self.low(x)
            if h not in self.clusters:
                return # Item não existe (ou é o max, tratado abaixo)

        # --- Passo Recursivo (para Casos 3 e 4) ---
        if h in self.clusters: # (Necessário para Caso 4)
            self.clusters[h].delete(x_to_delete_recursively)

            # Caso 5: Cluster ficou vazio 
            if self.clusters[h].get_min() is None:
                self.summary.delete(h)
                del self.clusters[h]
        
        # --- Atualização do Max (se necessário) ---
        if x == self.max_val:
            last_cluster_idx = self.summary.get_max()
            
            # Se não há mais clusters, o único elemento é o min_val
            if last_cluster_idx is None:
                self.max_val = self.min_val
            else:
                # O novo max é o max do último cluster 
                new_max_low = self.clusters[last_cluster_idx].get_max()
                self.max_val = self.index(last_cluster_idx, new_max_low)

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
            self.min_val = self.max_val # O min se torna o max (que era 1)
            return min_to_return # Retorna 0

        # 3. Encontrar o próximo menor elemento 
        first_cluster_idx = self.summary.get_min()
        
        # Se summary está vazio, só tínhamos min_val e max_val
        if first_cluster_idx is None:
            self.min_val = self.max_val # O novo min é o max
            return min_to_return

        # 4. O novo min_val é o menor elemento do primeiro cluster
        # e já o removemos recursivamente 
        new_min_low = self.clusters[first_cluster_idx].extract_min()
        self.min_val = self.index(first_cluster_idx, new_min_low)
        
        # 5. Limpeza: Se o cluster ficou vazio 
        if self.clusters[first_cluster_idx].get_min() is None:
            self.summary.extract_min() # Remove o cluster do summary
            del self.clusters[first_cluster_idx] # Deleta o cluster

        return min_to_return