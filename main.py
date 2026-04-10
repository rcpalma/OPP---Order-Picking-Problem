from data import *
from solve import *

G, X_completo = dados('a', 'a')



# Definindo Início (F) na primeira posição e Fim (I) na última
X_sample = pedidos(40)

X_sample = [item for item in X_sample if item[0] == 'B']

all_tour(G, X_sample, 'A', conversao)

