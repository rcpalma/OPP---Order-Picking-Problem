# Order Picking Problem do artigo: https://www.researchgate.net/publication/299405243_Optimizing_the_order_picking_of_a_scholar_and_office_supplies_warehouse

Nesse projeto pessoal, utilizei Python e a biblioteca gurobipy para modelar e resolver o problema de Order Picking (OPP) descrito no artigo no link acima de ISLER, C. A.; RIGHETTO, G. M.; MORABITO, R. Criei também uma visualização para melhor interpretabilidade da solução.
Para mais detalhes veja o artigo.

## Descrição
O problema Order Picking consiste em decidir a order de coleta de produtos armazenados em um CD satisfazendo um conjunto de restrições operacionais de maneira a minizar a distancia percorrida da coleta.
O problema exige a resolução de problemas de Caminho e Ciclo Hamiltoniano (HPP e HCP), simulando a necessidade do operador de alternar entre entradas frontais e saídas traseiras para otimizar o percurso.

## Instâncias
No artigo as instâncias são baseadas no banco de dados real de uma empresa brasileira de suprimentos escolares que no artigo foi capaz de reduzir a distância total percorrida em 26,8% em comparação às rotas manuais realizadas pela empresa.
Já no presente projeto, no arquivo data.py os dados de pedidos foram gerados de maneira sintética.

## Estrutura do Projeto
```text
├── main.py        # main
├── Solver.py      # Modelagem e otimização (Gurobi)
├── Data.py        # Geração de dados sintéticos
├── plot.py        # Visualizações da solução

```


## Resultados e Gráficos

Um gráfico é gerado ao executar main.py

**Primeiro - Layout do armazém:** Vista superior dos corredores do armazém. Note que a mudança entre corredores occore apenas pelo corredor de saída ao final e toda coleta tem que terminar em um dos pontos frontais.

<img width="2656" height="1340" alt="picking_route_2d" src="https://github.com/user-attachments/assets/997c3af3-e4be-4895-b031-144ef0ce92ad" />

Nesse caso, o trabalhador se encontrava no corredor 'B' e recebeu pedidos nos corredores 'B' e 'C' apenas. A solução foi um caminho por 'B' e, em seguida, por 'C', terminando neste último."

**Segundo - Layout do armazém:** Vista superior dos corredores do armazém. Note que a mudança entre corredores occore apenas pelo corredor de saída ao final e toda coleta tem que terminar em um dos pontos frontais.

<img width="2656" height="1340" alt="picking_route_2d" src="https://github.com/user-attachments/assets/479b7669-1eeb-4133-a5e8-e59f764d7ea6" />

Já neste caso, o trabalhador se encontrava no corredor 'A' e recebeu pedidos nos três corredores. A solução ótima foi ir do corredor 'A' até 'C', em 'C' fazer um ciclo hamiltoniano voltando para 'B' e terminar o trajeto no inicio de 'B'.

## Como usar
Abra a função main e escolha os dois parâmetros: num_pedidos(argumento dentro da função pedidos) e corr_inicial escolha entre 'A', 'B' ou 'C'.
No diretório do projeto execute o comando: "python main.py"

## Requirements

- Python 3.10+
- Gurobi (with valid license — academic license available at gurobi.com)
- **Python dependencies:**
  - `matplotlib`
  - `pandas`
  - `gurobipy`
  - `networkx`

## References
*   **Paper**: ISLER, C. A.; RIGHETTO, G. M.; MORABITO, R. (2016). *Optimizing the order picking of a scholar and office supplies warehouse*. https://www.researchgate.net/publication/299405243_Optimizing_the_order_picking_of_a_scholar_and_office_supplies_warehouse
