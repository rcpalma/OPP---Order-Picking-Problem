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




def all_tour(pedidos,corr_inicial):

    

    all_corr = sorted(list(set(item[0] for item in pedidos)))

    if all_corr == 'A':
        if corr_inicial == 'A':
            X_sample =   [('I', 0, 0)] + [item[1:] for item in pedidos]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hcp = HCP(G1_matrix, n)
            x_hcp, obj_hcp = res_hcp if res_hcp else (None, None)

        else if corr_inicial == 'B':
            #X_sample =   [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('F', 0, 37)]
            X_sample =   [('I', 0, 0)] + [('F',0,37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'A']
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

        else if corr_inicial == 'C':
            X_sample =   [('I', 0, 0)] + [('F',0,37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'A']
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

    else if all_corr == 'B':
        if corr_inicial == 'A':
            X_sample =   [('I', 0, 0)] + [('F',0,37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'B']
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)


        else if all_corr == 'B':

            X_sample1 =   [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'B']
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HCP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

        else if all_corr == 'C':

            X_sample =   [('I', 0, 0)] + [('F',0,37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'B']
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

        else if all_corr == 'C':

            if corr_inicial == 'A':
                X_sample =   [('I', 0, 0)] + [('F',0,37)]
                G1 = G.subgraph(X_sample)
                G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
                res_hpp = HPP(G1_matrix, n)
                x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

                X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'C']
                G1 = G.subgraph(X_sample1)
                G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
                res_hpp = HPP(G1_matrix, n)
                x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            elif corr_inicial == 'B':
                X_sample =   [('I', 0, 0)] + [('F',0,37)]
                G1 = G.subgraph(X_sample)
                G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
                res_hpp = HPP(G1_matrix, n)
                x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

                X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I',0,0)]
                G1 = G.subgraph(X_sample1)
                G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
                res_hpp = HPP(G1_matrix, n)
                x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            elif corr_inicial == 'C':
                X_sample =   [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'C']
                G1 = G.subgraph(X_sample)
                G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
                res_hpp = HCP(G1_matrix, n)
                x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)


        else if all_corr == ['A','B']:

            if corr_inicial == 'A':
                X_sample =   [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('F',0,37)]
                G1 = G.subgraph(X_sample)
                G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
                res_hpp = HPP(G1_matrix, n)
                x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

                X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('I',0,0)]
                G1 = G.subgraph(X_sample1)
                G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
                res_hpp = HPP(G1_matrix, n)
                x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            elif corr_inicial == 'B':
                X_sample =   [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('F',0,37)]
                G1 = G.subgraph(X_sample)
                G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
                res_hpp = HPP(G1_matrix, n)
                x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

                X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('I',0,0)]
                G1 = G.subgraph(X_sample1)
                G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
                res_hpp = HPP(G1_matrix, n)
                x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            elif corr_inicial == 'C':
                #testar duas possibilidades

                X_sample =   [('I', 0, 0)] + [('F',0,37)] 
                G1 = G.subgraph(X_sample)
                G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
                res_hpp = HCP(G1_matrix, n)
                x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

                X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'A']
                G1 = G.subgraph(X_sample1)
                G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
                res_hpp = HCP(G1_matrix, n)
                x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

                X_sample2 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'B'] 
                G1 = G.subgraph(X_sample2)
                G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample2)
                res_hpp = HPP(G1_matrix, n)
                x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

    else if all_corr == ['A','C']:
        if corr_inicial == 'A':
            X_sample =   [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('F',0,37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I',0,0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

        elif corr_inicial == 'C':
            X_sample =   [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('F',0,37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('I',0,0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)
        elif corr_inicial == 'B':

            X_sample =   [('I', 0, 0)] + [('F',0,37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'A'] 
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HCP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample2 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I',0,0)]
            G1 = G.subgraph(X_sample2)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample2)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)


    else if all_corr == ['B','C']:
        if corr_inicial == 'B':
            X_sample =   [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('F',0,37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I',0,0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

        elif corr_inicial == 'C':
            X_sample =   [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('F',0,37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('I',0,0)]
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

        elif corr_inicial == 'A':

            X_sample =   [('I', 0, 0)] + [('F',0,37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'B'] 
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HCP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample2 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I',0,0)]
            G1 = G.subgraph(X_sample2)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample2)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)


    else if all_corr == ['A','B','C']:
        if corr_inicial == 'A':
            X_sample =   [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('F',0,37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'B'] 
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HCP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample2 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I',0,0)]
            G1 = G.subgraph(X_sample2)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample2)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

        elif corr_inicial == 'B':
            X_sample =   [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('F',0,37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'A'] 
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HCP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample2 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I',0,0)]
            G1 = G.subgraph(X_sample2)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample2)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

        elif corr_inicial == 'C':
            X_sample =   [('I', 0, 0)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('F',0,37)]
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample1 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'A']
            G1 = G.subgraph(X_sample1)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample1)
            res_hpp = HCP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

            X_sample2 =   [('F', 0, 37)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('I',0,0)]
            G1 = G.subgraph(X_sample2)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample2)
            res_hpp = HPP(G1_matrix, n)
            x_hpp, obj_hpp = res_hpp if res_hpp else (None, None)

        

            




