from data import *
from solve import *
import random

G, X_completo = dados('a', 'a')



# Definindo Início (F) na primeira posição e Fim (I) na última
X_sample = pedidos(10)

all_tour(X_sample,'A')

print(f"Resolvendo para {n} nós...")
for i in range(n):
    print(f"ID {i}: {id_to_elem[i]}")

# Resolver como Ciclo (HCP) - Volta ao ponto de partida
res_hcp = HCP(G1_matrix, n)
x_hcp, obj_hcp = res_hcp if res_hcp else (None, None)

# Resolver como Caminho (HPP) - De index 0 para index n-1
res_hpp = HPP(G1_matrix, n)
x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

if obj_hcp is not None:
    print(f"\n--- CICLO OTIMIZADO (HCP) - Custo: {obj_hcp:.2f} ---")
    curr = 0
    caminho = [str(id_to_elem[curr])]
    visitados = {0}
    while len(visitados) < n:
        for j in range(n):
            if j not in visitados and x_hcp[curr, j] > 0.5:
                caminho.append(str(id_to_elem[j]))
                visitados.add(j)
                curr = j
                break
    print("Rota (Ciclo):", " -> ".join(caminho), "->", str(id_to_elem[0]))

if obj_hpp is not None:
    print(f"\n--- CAMINHO OTIMIZADO (HPP) - Custo: {obj_hpp:.2f} ---")
    print(f"Ponto de Partida (ID 0): {id_to_elem[0]}")
    print(f"Ponto de Destino (ID {n-1}): {id_to_elem[n-1]}")
    
    curr = 0
    caminho = [str(id_to_elem[curr])]
    visitados = {0}
    # Seguir o caminho até o penúltimo nó (o último nó n-1 não tem saída no HPP)
    while curr != n-1:
        encontrou = False
        for j in range(n):
            if j not in visitados and x_hpp[curr, j] > 0.5:
                caminho.append(str(id_to_elem[j]))
                visitados.add(j)
                curr = j
                encontrou = True
                break
        if not encontrou: break
    
    print("Rota (Caminho):", " -> ".join(caminho))
else:
    print("\nNão foi possível encontrar uma solução para o caminho (HPP).")

