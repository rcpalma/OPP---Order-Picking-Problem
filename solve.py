import gurobipy as gp
from gurobipy import GRB


def HCP(dist_matrix, n):
    model = gp.Model("HCP")

    # Variáveis: x[i,j] se o arco (i,j) é usado, u[i] para eliminação de subciclos (MTZ)
    x = model.addVars(n, n, vtype=GRB.BINARY, name="x")
    u = model.addVars(n, lb=0.0, vtype=GRB.CONTINUOUS, name="u")

    # Restrição: cada nó tem exatamente um arco de saída
    model.addConstrs(
        (gp.quicksum(x[i, j] for j in range(n) if i != j) == 1 for i in range(n)),
        name="saida"
    )

    # Restrição: cada nó tem exatamente um arco de entrada
    model.addConstrs(
        (gp.quicksum(x[i, j] for i in range(n) if i != j) == 1 for j in range(n)),
        name="entrada"
    )

    # Eliminação de subciclos (MTZ) - Para HCP, o nó 0 é fixo como referência
    model.addConstrs(
        (u[i] - u[j] + n * x[i, j] <= n - 1 for i in range(1,n) for j in range(1,n) if i != j),
        name="mtz"
    )

    # Função Objetivo: minimizar a distância total
    model.setObjective(
        gp.quicksum(dist_matrix[i, j] * x[i, j] for i in range(n) for j in range(n) if i != j),
        GRB.MINIMIZE
    )

    model.optimize()

    if model.status == GRB.OPTIMAL:
        print(f"Custo Total Ótimo (HCP): {model.objVal}")
        # Retornamos os valores (solução) em vez dos objetos Var
        x_sol = model.getAttr('x', x)
        return x_sol, model.objVal
    else:
        print("Modelo HCP não ótimo ou infactível!")
        return None, None


def HPP(dist_matrix, n):
    model = gp.Model("HPP")

    x = model.addVars(n, n, vtype=GRB.BINARY, name="x")
    u = model.addVars(n, lb=0.0, vtype=GRB.CONTINUOUS, name="u")

    # Restrição: cada nó (exceto o último) tem exatamente um arco de saída
    # Assumindo nó 0 como Início ('F') e nó n-1 como Fim ('I')
    model.addConstrs(
        (gp.quicksum(x[i, j] for j in range(n) if i != j) == 1 for i in range(n - 1)),
        name="saida"
    )

    # Restrição: cada nó (exceto o primeiro) tem exatamente um arco de entrada
    model.addConstrs(
        (gp.quicksum(x[i, j] for i in range(n) if i != j) == 1 for j in range(1, n)),
        name="entrada"
    )

    # Eliminação de subciclos (MTZ)
    model.addConstrs(
        (u[i] - u[j] + n * x[i, j] <= n - 1 for i in range(1, n) for j in range(1, n) if i != j),
        name="mtz"
    )

    model.setObjective(
        gp.quicksum(dist_matrix[i, j] * x[i, j] for i in range(n) for j in range(n) if i != j),
        GRB.MINIMIZE
    )

    model.optimize()

    if model.status == GRB.OPTIMAL:
        print(f"Custo Total Ótimo (HPP): {model.objVal}")
        # Retornamos os valores (solução) em vez dos objetos Var
        x_sol = model.getAttr('x', x)
        return x_sol, model.objVal
    else:
        print("Modelo HPP não ótimo ou infactível!")
        return None, None




def exibir_solucao(x_sol, id_to_elem, n, obj_val, titulo="SOLUÇÃO", tipo="HPP"):
    """
    Função auxiliar para visualizar a solução (Caminho ou Ciclo).
    """
    if obj_val is None:
        print(f"\n[{titulo}] Não foi possível encontrar uma solução.")
        return

    if tipo == "HCP":
        print(f"\n--- {titulo} (CICLO) - Custo: {obj_val:.2f} ---")
        curr = 0
        caminho = [str(id_to_elem[curr])]
        visitados = {0}
        while len(visitados) < n:
            for j in range(n):
                if j not in visitados and x_sol[curr, j] > 0.5:
                    caminho.append(str(id_to_elem[j]))
                    visitados.add(j)
                    curr = j
                    break
        print("Rota:", " -> ".join(caminho), "->", str(id_to_elem[0]))
    
    else: # HPP (Caminho)
        print(f"\n--- {titulo} (CAMINHO) - Custo: {obj_val:.2f} ---")
        curr = 0
        caminho = [str(id_to_elem[curr])]
        visitados = {0}
        while curr != n-1:
            encontrou = False
            for j in range(n):
                if j not in visitados and x_sol[curr, j] > 0.5:
                    caminho.append(str(id_to_elem[j]))
                    visitados.add(j)
                    curr = j
                    encontrou = True
                    break
            if not encontrou: break
        print("Rota:", " -> ".join(caminho))


def all_tour(G, pedidos, corr_inicial, conversao):
    """
    Resolve o tour completo baseado nas zonas dos pedidos (A, B, C).
    """
    all_corr = sorted(list(set(item[0] for item in pedidos)))
    print(all_corr)
    if all_corr == ['A']:
        if corr_inicial == 'A':
            X_sample = [('I', 0, 0)] + [item[1:] for item in pedidos] 
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hcp = HCP(G1_matrix, n)
            exibir_solucao(res_hcp[0], id_to_elem, n, res_hcp[1], titulo="Picking Zona A", tipo="HCP")

        elif corr_inicial == 'B':
            # Vai de I para F, depois atende Zona A
            X_sample = [('I', 0, 0)] + [('F', 0, 37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Deslocamento I -> F")

            X_sample1 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('I', 0, 0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Picking Zona A")

        elif corr_inicial == 'C':
            X_sample = [('I', 0, 0)] + [('F', 0, 37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Deslocamento I -> F")

            X_sample1 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('I', 0, 0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Picking Zona A")

    elif all_corr == ['B']:
        if corr_inicial == 'A':
            X_sample = [('I', 0, 0)] + [('F', 0, 37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Deslocamento I -> F")

            X_sample1 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('I', 0, 0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Picking Zona B")

        elif corr_inicial == 'B':
            X_sample1 = [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'B']
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hcp = HCP(G1_matrix, n)
            exibir_solucao(res_hcp[0], id_to_elem, n, res_hcp[1], titulo="Picking Zona B", tipo="HCP")

        elif corr_inicial == 'C':
            X_sample = [('I', 0, 0)] + [('F', 0, 37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Deslocamento I -> F")

            X_sample1 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('I', 0, 0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Picking Zona B")

    elif all_corr == ['C']:
        if corr_inicial == 'A':
            X_sample = [('I', 0, 0)] + [('F', 0, 37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Deslocamento I -> F")

            X_sample1 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I', 0, 0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Picking Zona C")

        elif corr_inicial == 'B':
            X_sample = [('I', 0, 0)] + [('F', 0, 37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Deslocamento I -> F")

            X_sample1 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I', 0, 0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Picking Zona C")

        elif corr_inicial == 'C':
            X_sample = [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'C']
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hcp = HCP(G1_matrix, n)
            exibir_solucao(res_hcp[0], id_to_elem, n, res_hcp[1], titulo="Picking Zona C", tipo="HCP")

    elif all_corr == ['A', 'B']:
        if corr_inicial == 'A':
            # A -> B
            X_sample = [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('F', 0, 37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Atendimento Zona A (seguindo para B)")

            X_sample1 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('I', 0, 0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Atendimento Zona B (retornando I)")

        elif corr_inicial == 'B':
            # B -> A
            X_sample = [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('F', 0, 37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Atendimento Zona B (seguindo para A)")

            X_sample1 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('I', 0, 0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Atendimento Zona A (retornando I)")

    elif all_corr == ['A', 'C']:
        if corr_inicial == 'A':
            X_sample = [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('F', 0, 37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Zona A -> F")

            X_sample1 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I', 0, 0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Zona C -> I")

        elif corr_inicial == 'C':
            X_sample = [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('F', 0, 37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Zona C -> F")

            X_sample1 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('I', 0, 0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Zona A -> I")

    elif all_corr == ['B', 'C']:
        if corr_inicial == 'B':
            X_sample = [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('F', 0, 37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Zona B -> F")

            X_sample1 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I', 0, 0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Zona C -> I")

        elif corr_inicial == 'C':
            X_sample = [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('F', 0, 37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Zona C -> F")

            X_sample1 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('I', 0, 0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            exibir_solucao(res_hpp[0], id_to_elem, n, res_hpp[1], titulo="Zona B -> I")

    elif all_corr == ['A', 'B', 'C']:
        if corr_inicial == 'A':
            X_sample = [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('F', 0, 37)]
            G1_matrix, id_to_elem, n = conversao(G.subgraph(X_sample), node_list=X_sample)
            res1 = HPP(G1_matrix, n)
            exibir_solucao(res1[0], id_to_elem, n, res1[1], titulo="A -> F")

            X_sample1 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'B'] 
            G1_matrix, id_to_elem, n = conversao(G.subgraph(X_sample1), node_list=X_sample1)
            res2 = HCP(G1_matrix, n)
            exibir_solucao(res2[0], id_to_elem, n, res2[1], titulo="Picking B (Ciclo em F)", tipo="HCP")

            X_sample2 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I', 0, 0)]
            G1_matrix, id_to_elem, n = conversao(G.subgraph(X_sample2), node_list=X_sample2)
            res3 = HPP(G1_matrix, n)
            exibir_solucao(res3[0], id_to_elem, n, res3[1], titulo="C -> I")

        elif corr_inicial == 'B':
            X_sample = [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('F', 0, 37)]
            G1_matrix, id_to_elem, n = conversao(G.subgraph(X_sample), node_list=X_sample)
            res1 = HPP(G1_matrix, n)
            exibir_solucao(res1[0], id_to_elem, n, res1[1], titulo="B -> F")

            X_sample1 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'A']
            G1_matrix, id_to_elem, n = conversao(G.subgraph(X_sample1), node_list=X_sample1)
            res2 = HCP(G1_matrix, n)
            exibir_solucao(res2[0], id_to_elem, n, res2[1], titulo="Picking A (Ciclo em F)", tipo="HCP")

            X_sample2 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I', 0, 0)]
            G1_matrix, id_to_elem, n = conversao(G.subgraph(X_sample2), node_list=X_sample2)
            res3 = HPP(G1_matrix, n)
            exibir_solucao(res3[0], id_to_elem, n, res3[1], titulo="C -> I")

        elif corr_inicial == 'C':
            X_sample = [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('F', 0, 37)]
            G1_matrix, id_to_elem, n = conversao(G.subgraph(X_sample), node_list=X_sample)
            res1 = HPP(G1_matrix, n)
            exibir_solucao(res1[0], id_to_elem, n, res1[1], titulo="C -> F")

            X_sample1 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'A']
            G1_matrix, id_to_elem, n = conversao(G.subgraph(X_sample1), node_list=X_sample1)
            res2 = HCP(G1_matrix, n)
            exibir_solucao(res2[0], id_to_elem, n, res2[1], titulo="Picking A (Ciclo em F)", tipo="HCP")

            X_sample2 = [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('I', 0, 0)]
            G1_matrix, id_to_elem, n = conversao(G.subgraph(X_sample2), node_list=X_sample2)
            res3 = HPP(G1_matrix, n)
            exibir_solucao(res3[0], id_to_elem, n, res3[1], titulo="B -> I")

        

            




