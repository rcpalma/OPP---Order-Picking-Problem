from data import *
from solve import *
from plot import *

G, X_completo = dados()

X_sample = pedidos(25)

#X_sample = [item for item in X_sample if item[0] == 'C' or item[0] == 'B']

Corr_inicial = 'A'

# Obter a rota consolidada
rota = all_tour(G, X_sample, Corr_inicial, conversao)

# Plotar a solução
plot_picking_route(rota)

