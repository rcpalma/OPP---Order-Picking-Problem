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

    model.setParam('TimeLimit', 60)
    
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

    model.setParam('TimeLimit', 60)
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





def extrair_caminho(x_sol, id_to_elem, n, tipo):
    if x_sol is None: return []
    caminho_ids = []
    if tipo == "HCP":
        curr = 0
        caminho_ids = [0]
        visitados = {0}
        while len(visitados) < n:
            for j in range(n):
                if j not in visitados and x_sol[curr, j] > 0.5:
                    caminho_ids.append(j)
                    visitados.add(j)
                    curr = j
                    break
        caminho_ids.append(0) 
    else: # HPP
        curr = 0
        caminho_ids = [0]
        visitados = {0}
        while curr != n-1:
            encontrou = False
            for j in range(n):
                if j not in visitados and x_sol[curr, j] > 0.5:
                    caminho_ids.append(j)
                    visitados.add(j)
                    curr = j
                    encontrou = True
                    break
            if not encontrou: break
    return [id_to_elem[i] for i in caminho_ids]


def all_tour(G, pedidos, corr_inicial, conversao):
    """
    Resolve o tour completo baseado nas zonas dos pedidos (A, B, C).
    """
    all_corr = sorted(list(set(item[0] for item in pedidos)))

    def dist_corredor(c1, c2):
        # Distâncias fornecidas: d(A,B)=1.6, d(B,C)=1.6, d(A,C)=3.2
        # Posições relativas: A=0, B=1.6, C=3.2
        pos = {'A': 0, 'B': 1.6, 'C': 3.2}
        return abs(pos[c1] - pos[c2])
    
    def avaliar_rota(sequencia, label_map=None):
        total = 0
        passos = []
        full_path = []
        prev_label = corr_inicial 
        for nodes, titulo, tipo in sequencia:
            G1 = G.subgraph(nodes)
            matrix, id_map, n = conversao(G1, node_list=nodes)
            if tipo == "HCP":
                res = HCP(matrix, n)
            else:
                res = HPP(matrix, n)
            if res[1] is None: return float('inf'), [], []
            
            caminho = extrair_caminho(res[0], id_map, n, tipo)
            
            # Inferir label
            label = "Unknown"
            if "Corredor A" in titulo or "Zona A" in titulo: label = "A"
            elif "Corredor B" in titulo or "Zona B" in titulo: label = "B"
            elif "Corredor C" in titulo or "Zona C" in titulo: label = "C"
            if label_map and titulo in label_map: label = label_map[titulo]

            if prev_label is not None and label != prev_label and label != "Unknown" and prev_label != "Unknown":
                total += dist_corredor(prev_label, label)

            total += res[1]
            passos.append((res[0], id_map, n, res[1], titulo, tipo, label))
            for node in caminho:
                full_path.append((label, node))
            
            prev_label = label
                
        return total, passos, full_path

    def exibir_vencedor(passos):
        total_acumulado = 0
        prev_label = corr_inicial
        for p in passos:
            res_sol, id_map, n, obj, titulo, tipo, label = p
            
            if prev_label is not None and label != prev_label and label != "Unknown" and prev_label != "Unknown":
                d_trans = dist_corredor(prev_label, label)
                print(f"\n[Transição de Corredor: {prev_label} -> {label} | Distância: {d_trans:.2f}]")
                total_acumulado += d_trans

            exibir_solucao(res_sol, id_map, n, obj, titulo=titulo, tipo=tipo)
            total_acumulado += obj
            prev_label = label
            
        print(f"\n>>> CUSTO TOTAL CONSOLIDADO: {total_acumulado:.2f} <<<")


    if all_corr == ['A']:
        if corr_inicial == 'A':
            X_sample = [('I', 0, 1)] + [item[1:] for item in pedidos if item[0] == 'A']
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hcp = HCP(G1_matrix, n)
            exibir_solucao(res_hcp[0], id_to_elem, n, res_hcp[1], titulo="Picking Zona A", tipo="HCP")
            return [("A", node) for node in extrair_caminho(res_hcp[0], id_to_elem, n, "HCP")]

        elif corr_inicial in ['B', 'C']:
            label_init = "B" if corr_inicial == 'B' else "C"
            seq = [
                ([('I', 0, 1), ('F', 37, 1)], f"Deslocamento I -> F (Corredor {label_init})", "HPP"),
                ([('F', 37, 1)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('I', 0, 1)], "Picking Zona A", "HPP")
            ]
            t, p, path = avaliar_rota(seq, {f"Deslocamento I -> F (Corredor {label_init})": label_init, "Picking Zona A": "A"})
            exibir_vencedor(p)
            return path

    elif all_corr == ['B']:
        if corr_inicial == 'B':
            X_sample = [('I', 0, 1)] + [item[1:] for item in pedidos if item[0] == 'B']
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hcp = HCP(G1_matrix, n)
            exibir_solucao(res_hcp[0], id_to_elem, n, res_hcp[1], titulo="Picking Zona B", tipo="HCP")
            return [("B", node) for node in extrair_caminho(res_hcp[0], id_to_elem, n, "HCP")]

        elif corr_inicial in ['A', 'C']:
            label_init = corr_inicial
            seq = [
                ([('I', 0, 1), ('F', 37, 1)], f"Deslocamento I -> F (Corredor {label_init})", "HPP"),
                ([('F', 37, 1)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('I', 0, 1)], "Picking Zona B", "HPP")
            ]
            t, p, path = avaliar_rota(seq, {f"Deslocamento I -> F (Corredor {label_init})": label_init, "Picking Zona B": "B"})
            exibir_vencedor(p)
            return path

    elif all_corr == ['C']:
        if corr_inicial == 'C':
            X_sample = [('I', 0, 1)] + [item[1:] for item in pedidos if item[0] == 'C']
            G1 = G.subgraph(X_sample)
            G1_matrix, id_to_elem, n = conversao(G1, node_list=X_sample)
            res_hcp = HCP(G1_matrix, n)
            exibir_solucao(res_hcp[0], id_to_elem, n, res_hcp[1], titulo="Picking Zona C", tipo="HCP")
            return [("C", node) for node in extrair_caminho(res_hcp[0], id_to_elem, n, "HCP")]

        elif corr_inicial in ['A', 'B']:
            label_init = corr_inicial
            seq = [
                ([('I', 0, 1), ('F', 37, 1)], f"Deslocamento I -> F (Corredor {label_init})", "HPP"),
                ([('F', 37, 1)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I', 0, 1)], "Picking Zona C", "HPP")
            ]
            t, p, path = avaliar_rota(seq, {f"Deslocamento I -> F (Corredor {label_init})": label_init, "Picking Zona C": "C"})
            exibir_vencedor(p)
            return path

    elif all_corr == ['A', 'B']:
        if corr_inicial == 'A':
            # A -> B
            seq = [
                ([('I', 0, 1)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('F', 37, 1)], "Atendimento Zona A (seguindo para B)", "HPP"),
                ([('F', 37, 1)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('I', 0, 1)], "Atendimento Zona B (retornando I)", "HPP")
            ]
            t, p, path = avaliar_rota(seq, {"Atendimento Zona A (seguindo para B)": "A", "Atendimento Zona B (retornando I)": "B"})
            exibir_vencedor(p)
            return path

        elif corr_inicial == 'B':
            # B -> A
            seq = [
                ([('I', 0, 1)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('F', 37, 1)], "Atendimento Zona B (seguindo para A)", "HPP"),
                ([('F', 37, 1)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('I', 0, 1)], "Atendimento Zona A (retornando I)", "HPP")
            ]
            t, p, path = avaliar_rota(seq, {"Atendimento Zona B (seguindo para A)": "B", "Atendimento Zona A (retornando I)": "A"})
            exibir_vencedor(p)
            return path

        elif corr_inicial == 'C':
            pedidos_A = [p[1:] for p in pedidos if p[0] == 'A']
            pedidos_B = [p[1:] for p in pedidos if p[0] == 'B']
            
            # Possibilidade 1: Traversal C -> Tour B (HCP) -> Tour A (HPP to I)
            seq1 = [
                ([('I', 0, 1), ('F', 37, 1)], "Trajeto Inicial Corredor C", "HPP"),
                ([('F', 37, 1)] + pedidos_B, "Picking Zona B (Ciclo em F)", "HCP"),
                ([('F', 37, 1)] + pedidos_A + [('I', 0, 1)], "Picking Zona A (retornando I)", "HPP")
            ]
            
            # Possibilidade 2: Traversal C -> Tour A (HCP) -> Tour B (HPP to I)
            seq2 = [
                ([('I', 0, 1), ('F', 37, 1)], "Trajeto Inicial Corredor C", "HPP"),
                ([('F', 37, 1)] + pedidos_A, "Picking Zona A (Ciclo em F)", "HCP"),
                ([('F', 37, 1)] + pedidos_B + [('I', 0, 1)], "Picking Zona B (retornando I)", "HPP")
            ]
            
            t1, p1, path1 = avaliar_rota(seq1, {"Trajeto Inicial Corredor C": "C", "Picking Zona B (Ciclo em F)": "B", "Picking Zona A (retornando I)": "A"})
            t2, p2, path2 = avaliar_rota(seq2, {"Trajeto Inicial Corredor C": "C", "Picking Zona A (Ciclo em F)": "A", "Picking Zona B (retornando I)": "B"})
            
            if t1 < t2:
                exibir_vencedor(p1); return path1
            else:
                exibir_vencedor(p2); return path2

    elif all_corr == ['A', 'C']:
        if corr_inicial == 'A':
            seq = [
                ([('I', 0, 1)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('F', 37, 1)], "Zona A -> F", "HPP"),
                ([('F', 37, 1)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I', 0, 1)], "Zona C -> I", "HPP")
            ]
            t, p, path = avaliar_rota(seq, {"Zona A -> F": "A", "Zona C -> I": "C"})
            exibir_vencedor(p); return path

        elif corr_inicial == 'C':
            seq = [
                ([('I', 0, 1)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('F', 37, 1)], "Zona C -> F", "HPP"),
                ([('F', 37, 1)] + [item[1:] for item in pedidos if item[0] == 'A'] + [('I', 0, 1)], "Zona A -> I", "HPP")
            ]
            t, p, path = avaliar_rota(seq, {"Zona C -> F": "C", "Zona A -> I": "A"})
            exibir_vencedor(p); return path
        
        elif corr_inicial == 'B':
            seq1 = [
                ([('I', 0, 1), ('F', 37, 1)], "Trajeto Inicial Corredor B", "HPP"),
                ([('F', 37, 1)] + [p[1:] for p in pedidos if p[0] == 'A'], "Picking Zona A (Ciclo em F)", "HCP"),
                ([('F', 37, 1)] + [p[1:] for p in pedidos if p[0] == 'C'] + [('I', 0, 1)], "Picking Zona C (retornando I)", "HPP")
            ]
            seq2 = [
                ([('I', 0, 1), ('F', 37, 1)], "Trajeto Inicial Corredor B", "HPP"),
                ([('F', 37, 1)] + [p[1:] for p in pedidos if p[0] == 'C'], "Picking Zona C (Ciclo em F)", "HCP"),
                ([('F', 37, 1)] + [p[1:] for p in pedidos if p[0] == 'A'] + [('I', 0, 1)], "Picking Zona A (retornando I)", "HPP")
            ]
            t1, p1, path1 = avaliar_rota(seq1, {"Trajeto Inicial Corredor B": "B", "Picking Zona A (Ciclo em F)": "A", "Picking Zona C (retornando I)": "C"})
            t2, p2, path2 = avaliar_rota(seq2, {"Trajeto Inicial Corredor B": "B", "Picking Zona C (Ciclo em F)": "C", "Picking Zona A (retornando I)": "A"})
            if t1 < t2:
                exibir_vencedor(p1); return path1
            else:
                exibir_vencedor(p2); return path2



    elif all_corr == ['B', 'C']:
        if corr_inicial == 'B':
            seq = [
                ([('I', 0, 1)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('F', 37, 1)], "Zona B -> F", "HPP"),
                ([('F', 37, 1)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('I', 0, 1)], "Zona C -> I", "HPP")
            ]
            t, p, path = avaliar_rota(seq, {"Zona B -> F": "B", "Zona C -> I": "C"})
            exibir_vencedor(p); return path

        elif corr_inicial == 'C':
            seq = [
                ([('I', 0, 1)] + [item[1:] for item in pedidos if item[0] == 'C'] + [('F', 37, 1)], "Zona C -> F", "HPP"),
                ([('F', 37, 1)] + [item[1:] for item in pedidos if item[0] == 'B'] + [('I', 0, 1)], "Zona B -> I", "HPP")
            ]
            t, p, path = avaliar_rota(seq, {"Zona C -> F": "C", "Zona B -> I": "B"})
            exibir_vencedor(p); return path
        
        elif corr_inicial == 'A':
            seq1 = [
                ([('I', 0, 1), ('F', 37, 1)], "Trajeto Inicial Corredor A", "HPP"),
                ([('F', 37, 1)] + [p[1:] for p in pedidos if p[0] == 'B'], "Picking Zona B (Ciclo em F)", "HCP"),
                ([('F', 37, 1)] + [p[1:] for p in pedidos if p[0] == 'C'] + [('I', 0, 1)], "Picking Zona C (retornando I)", "HPP")
            ]
            seq2 = [
                ([('I', 0, 1), ('F', 37, 1)], "Trajeto Inicial Corredor A", "HPP"),
                ([('F', 37, 1)] + [p[1:] for p in pedidos if p[0] == 'C'], "Picking Zona C (Ciclo em F)", "HCP"),
                ([('F', 37, 1)] + [p[1:] for p in pedidos if p[0] == 'B'] + [('I', 0, 1)], "Picking Zona B (retornando I)", "HPP")
            ]
            t1, p1, path1 = avaliar_rota(seq1, {"Trajeto Inicial Corredor A": "A", "Picking Zona B (Ciclo em F)": "B", "Picking Zona C (retornando I)": "C"})
            t2, p2, path2 = avaliar_rota(seq2, {"Trajeto Inicial Corredor A": "A", "Picking Zona C (Ciclo em F)": "C", "Picking Zona B (retornando I)": "B"})
            if t1 < t2:
                exibir_vencedor(p1); return path1
            else:
                exibir_vencedor(p2); return path2

    elif all_corr == ['A', 'B', 'C']:
        if corr_inicial == 'A':
            pedidos_A = [p[1:] for p in pedidos if p[0] == 'A']
            pedidos_B = [p[1:] for p in pedidos if p[0] == 'B']
            pedidos_C = [p[1:] for p in pedidos if p[0] == 'C']

            # Opção 1: A -> B (HCP) -> C (HPP to I)
            seq1 = [
                ([('I', 0, 1)] + pedidos_A + [('F', 37, 1)], "Picking Zona A (seguindo para F)", "HPP"),
                ([('F', 37, 1)] + pedidos_B, "Picking Zona B (Ciclo em F)", "HCP"),
                ([('F', 37, 1)] + pedidos_C + [('I', 0, 1)], "Picking Zona C (retornando I)", "HPP")
            ]
            # Opção 2: A -> C (HCP) -> B (HPP to I)
            seq2 = [
                ([('I', 0, 1)] + pedidos_A + [('F', 37, 1)], "Picking Zona A (seguindo para F)", "HPP"),
                ([('F', 37, 1)] + pedidos_C, "Picking Zona C (Ciclo em F)", "HCP"),
                ([('F', 37, 1)] + pedidos_B + [('I', 0, 1)], "Picking Zona B (retornando I)", "HPP")
            ]
            t1, p1, r1 = avaliar_rota(seq1, {"Picking Zona A (seguindo para F)": "A", "Picking Zona B (Ciclo em F)": "B", "Picking Zona C (retornando I)": "C"})
            t2, p2, r2 = avaliar_rota(seq2, {"Picking Zona A (seguindo para F)": "A", "Picking Zona C (Ciclo em F)": "C", "Picking Zona B (retornando I)": "B"})
            if t1 < t2:
                exibir_vencedor(p1); return r1
            else:
                exibir_vencedor(p2); return r2

        elif corr_inicial == 'B':
            pedidos_A = [p[1:] for p in pedidos if p[0] == 'A']
            pedidos_B = [p[1:] for p in pedidos if p[0] == 'B']
            pedidos_C = [p[1:] for p in pedidos if p[0] == 'C']

            # Opção 1: B -> A (HCP) -> C (HPP to I)
            seq1 = [
                ([('I', 0, 1)] + pedidos_B + [('F', 37, 1)], "Picking Zona B (seguindo para F)", "HPP"),
                ([('F', 37, 1)] + pedidos_A, "Picking Zona A (Ciclo em F)", "HCP"),
                ([('F', 37, 1)] + pedidos_C + [('I', 0, 1)], "Picking Zona C (retornando I)", "HPP")
            ]
            # Opção 2: B -> C (HCP) -> A (HPP to I)
            seq2 = [
                ([('I', 0, 1)] + pedidos_B + [('F', 37, 1)], "Picking Zona B (seguindo para F)", "HPP"),
                ([('F', 37, 1)] + pedidos_C, "Picking Zona C (Ciclo em F)", "HCP"),
                ([('F', 37, 1)] + pedidos_A + [('I', 0, 1)], "Picking Zona A (retornando I)", "HPP")
            ]
            t1, p1, r1 = avaliar_rota(seq1, {"Picking Zona B (seguindo para F)": "B", "Picking Zona A (Ciclo em F)": "A", "Picking Zona C (retornando I)": "C"})
            t2, p2, r2 = avaliar_rota(seq2, {"Picking Zona B (seguindo para F)": "B", "Picking Zona C (Ciclo em F)": "C", "Picking Zona A (retornando I)": "A"})
            if t1 < t2:
                exibir_vencedor(p1); return r1
            else:
                exibir_vencedor(p2); return r2

        elif corr_inicial == 'C':
            pedidos_A = [p[1:] for p in pedidos if p[0] == 'A']
            pedidos_B = [p[1:] for p in pedidos if p[0] == 'B']
            pedidos_C = [p[1:] for p in pedidos if p[0] == 'C']

            # Opção 1: C -> A (HCP) -> B (HPP to I)
            seq1 = [
                ([('I', 0, 1)] + pedidos_C + [('F', 37, 1)], "Picking Zona C (seguindo para F)", "HPP"),
                ([('F', 37, 1)] + pedidos_A, "Picking Zona A (Ciclo em F)", "HCP"),
                ([('F', 37, 1)] + pedidos_B + [('I', 0, 1)], "Picking Zona B (retornando I)", "HPP")
            ]
            # Opção 2: C -> B (HCP) -> A (HPP to I)
            seq2 = [
                ([('I', 0, 1)] + pedidos_C + [('F', 37, 1)], "Picking Zona C (seguindo para F)", "HPP"),
                ([('F', 37, 1)] + pedidos_B, "Picking Zona B (Ciclo em F)", "HCP"),
                ([('F', 37, 1)] + pedidos_A + [('I', 0, 1)], "Picking Zona A (retornando I)", "HPP")
            ]
            t1, p1, r1 = avaliar_rota(seq1, {"Picking Zona C (seguindo para F)": "C", "Picking Zona A (Ciclo em F)": "A", "Picking Zona B (retornando I)": "B"})
            t2, p2, r2 = avaliar_rota(seq2, {"Picking Zona C (seguindo para F)": "C", "Picking Zona B (Ciclo em F)": "B", "Picking Zona A (retornando I)": "A"})
            if t1 < t2:
                exibir_vencedor(p1); return r1
            else:
                exibir_vencedor(p2); return r2
    
    return []

        

            




