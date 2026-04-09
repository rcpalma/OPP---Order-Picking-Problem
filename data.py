import numpy as np
import pandas as pd
import osmnx as ox
import networkx as nx



def dados(Ia,Orders):


    lados = ['L', 'R']
    colunas = range(1, 37) # 1 a 32
    niveis = range(1, 10)  # 1 a 9

    vertices_nomes = [(l, c, n) for l in lados for c in colunas for n in niveis]

    G = nx.complete_graph(vertices_nomes)


    for u, v in G.edges():
        a1, a2, a3 = u  # (lado_u, col_u, nivel_u)
        b1, b2, b3 = v  # (lado_v, col_v, nivel_v)
        
        # Cálculo das diferenças absolutas
        diff_col = abs(b2 - a2)
        diff_niv = abs(b3 - a3)
        
        if a1 != b1:
            # Se os lados são diferentes (ex: um está em L e outro em R)
            dist = ((1.6)**2 + (1.35 * diff_col)**2)**(1/2) + (1.15 * diff_niv)
        else:
            # Se estão no mesmo lado
            dist = (1.35 * diff_col) + (1.15 * diff_niv)
        
        # Atribuir o peso ao grafo
        G.edges[u, v]['weight'] = dist
        G.edges[u, v]['length'] = dist

    # Teste rápido: Distância entre ('L', 1, 1) e ('R', 1, 1) deve ser 1.6
    print(f"Distância L1,1 para R1,1: {G['L', 1, 1]['R', 1, 1]['weight']:.2f}")
    for u,v in G.edges():
        print(f"Distância {u[0],u[1],u[2]} para {v[0],v[1],v[2]}: {G[u][v]['weight']:.2f}")


dados("a","a")