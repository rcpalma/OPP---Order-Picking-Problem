import numpy as np
import pandas as pd
import osmnx as ox
import networkx as nx
import random



def dados(Ia,Orders):


    lados = ['L', 'R']
    colunas = range(1, 37) # 1 a 32
    niveis = range(1, 10)  # 1 a 9
    v_inicial = [('F',0,37)] 
    v_final = [('I',0,0)]

    vertices_nomes = [(l, c, n) for l in lados for c in colunas for n in niveis]
    vertices_nomes_f = v_inicial + vertices_nomes + v_final

    G = nx.complete_graph(vertices_nomes_f)


    for u, v in G.edges():
        a1, a2, a3 = u  # (lado_u, col_u, nivel_u)
        b1, b2, b3 = v  # (lado_v, col_v, nivel_v)
        
        # Cálculo das diferenças absolutas
        diff_col = abs(b2 - a2)
        diff_niv = abs(b3 - a3)
        
        if a1 != b1:
            # Se os lados são diferentes (ex: um está em L e outro em R)
            if a1 in ['I','F'] and a2 in ['I','F']:
                dist = ((1.35 * diff_col)**2)**(1/2) + (1.15 * diff_niv)
            else:
                dist = ((1.6)**2 + (1.35 * diff_col)**2)**(1/2) + (1.15 * diff_niv)
        else:
            # Se estão no mesmo lado
            dist = (1.35 * diff_col) + (1.15 * diff_niv)
        
        # Atribuir o peso ao grafo
        G.edges[u, v]['weight'] = dist
        G.edges[u, v]['length'] = dist

    # Teste rápido: Distância entre ('L', 1, 1) e ('R', 1, 1) deve ser 1.6
    print(f"Distância L1,1 para R1,1: {G['L', 1, 1]['R', 1, 1]['weight']:.2f}")
    # for u,v in G.edges():
    #     print(f"Distância {u[0],u[1],u[2]} para {v[0],v[1],v[2]}: {G[u][v]['weight']:.2f}")


    return G,vertices_nomes_f




def conversao(G, node_list=None):
    # Se uma lista de nós for fornecida, usamos ela para definir a ordem dos IDs
    # Caso contrário, usamos a ordem padrão do NetworkX
    nodes = node_list if node_list is not None else list(G.nodes())
    
    vertex_to_id = {node: i for i, node in enumerate(nodes)}
    id_to_vertex = {i: node for i, node in enumerate(nodes)}

    # 2. Criar a matriz de distâncias usando os IDs (para o solver)
    n = G.number_of_nodes()
    dist_matrix = {}

    for u, v, data in G.edges(data=True):
        i, j = vertex_to_id[u], vertex_to_id[v]
        dist_matrix[i, j] = data['weight']
        dist_matrix[j, i] = data['weight'] # Grafo não direcionado

    return dist_matrix, id_to_vertex, n


def pedidos(n_pedidos):
    tipos = ['A', 'B', 'C']
    lados = ['L', 'R']
    colunas = range(1, 37)
    niveis = range(1, 10)

    # 2. Gerar todos os pontos possíveis com o prefixo (x, l, c, n)
    pedidos = [(x, l, c, n) 
                    for x in tipos 
                    for l in lados 
                    for c in colunas 
                    for n in niveis]
    
    return random.sample(pedidos, n_pedidos)
    