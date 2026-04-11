import matplotlib.pyplot as plt
import matplotlib.patches as patches

def plot_picking_route(route):
    """
    Plots the picking route in a 2D Floor Plan with arrows, emphasizing F-end connectivity.
    route: List of (label, (side, col, niv))
    """
    if not route:
        print("Empty route, nothing to plot.")
        return


    clean_route = []
    for i, item in enumerate(route):
        if i > 0 and item == route[i-1]:
            continue
        clean_route.append(item)
    route = clean_route

    fig, ax = plt.subplots(figsize=(18, 9))
    
    # Configuration
    corr_offset = {'A': 10, 'B': 5, 'C': 0} 
    colors = {'A': '#FF5733', 'B': '#2ECC71', 'C': '#3498DB', 'Unknown': 'gray'}
    side_offset = {'L': 0.8, 'R': -0.8} 
    
    col_width = 1.35
    max_col = 37 
    
    # Draw Background Layout
    # 1. Corridors
    for corr, y_base in corr_offset.items():
        # Shelf area
        rect = patches.Rectangle((0, y_base - 1.2), max_col * col_width, 2.4, 
                                 linewidth=1, edgecolor='#bdc3c7', facecolor='#ecf0f1', alpha=0.6, zorder=0)
        ax.add_patch(rect)
        ax.text(-5, y_base, f"Corredor {corr}", va='center', ha='right', fontweight='bold', fontsize=14, color=colors[corr])
        

    # 2. Transverse Aisle at the FIM (F) end
    aisle_f = patches.Rectangle((max_col * col_width - 1, -2), 3, 14, 
                               linewidth=0, facecolor='#dfe6e9', alpha=0.7, zorder=-1)
    ax.add_patch(aisle_f)
    ax.text(max_col * col_width + 2, 9, "CORREDOR TRANSVERSAL (CONEXÃO F)", rotation=270, va='top', fontweight='bold', alpha=0.5)

    # 3. Entry/Exit area at the INÍCIO (I) end
    entry_area = patches.Rectangle((-1, -2), 2, 14, linewidth=0, facecolor='#fdf6e3', alpha=0.3, zorder=-1)
    ax.add_patch(entry_area)
    #ax.text(0, -2.5, "ZONA DE EXPEDIÇÃO (I)", ha='center', fontweight='bold', alpha=0.5)
    
    xs, ys = [], []
    
    # Extract coordinates
    for label, node in route:
        side, col, niv = node
        
        # Horizontal position is now standardized in 'col' (2nd element) for all nodes
        x = col * col_width
        
        y_base = corr_offset.get(label, 5) 
        y_off = side_offset.get(side, 0)
        y = y_base + y_off
        xs.append(x)
        ys.append(y)

    # Plot the path with arrows
    for i in range(len(xs) - 1):
        # Color the segment based on the destination corridor if it's a transition
        seg_color = 'black'
        alpha = 0.6
        lw = 1.5
        
        # Check for corridor transition
        label_curr = route[i][0]
        label_next = route[i+1][0]
        is_transition = (label_curr != label_next)
        
        # Distance from 'I' end (Left) and 'F' end (Right)
        at_i_end = (abs(xs[i]) < 1.0 and abs(xs[i+1]) < 1.0)
        at_f_end = (abs(xs[i] - max_col * col_width) < 1.0 and abs(xs[i+1] - max_col * col_width) < 1.0)

        # 1. No arrows between starts (I end) of corridors
        if is_transition and at_i_end:
            continue
            
        # 2. Access only via right (F end) side
        if is_transition and not at_f_end:
            # If it's a transition not at the end, we might want to warn or skip 
            # as per "o acesso acontece apenas pela saida"
            seg_color = 'red' # Highlight illegal transition for visibility if it happens
            alpha = 0.8
            lw = 1.0
        
        # If it's a movement along the Transverse Aisle (X constant at the end)
        if abs(xs[i] - xs[i+1]) < 0.1 and at_f_end:
            seg_color = '#7f8c8d' # Aisle color
            lw = 2.5
            
        ax.annotate("", xy=(xs[i+1], ys[i+1]), xytext=(xs[i], ys[i]),
                    arrowprops=dict(arrowstyle="->", color=seg_color, lw=lw, 
                                  alpha=alpha, shrinkA=2, shrinkB=2, mutation_scale=15),
                    zorder=2)

    # Plot points and labels
    for i, (label, node) in enumerate(route):
        side, col, niv = node
        x, y = xs[i], ys[i]
        
        if side in ['L', 'R']:
            # Pick location
            color = colors.get(label, 'black')
            ax.scatter(x, y, color=color, s=30, edgecolors='white', linewidth=2, zorder=4)
            # Label with picking order
            ax.text(x, y + 0.6, f"#{i}", va='bottom', ha='center', 
                    fontsize=9, fontweight='bold', bbox=dict(facecolor='white', alpha=0.8, edgecolor=color, boxstyle='round,pad=0.2'))
        elif side == 'I':
            is_start = (i == 0)
            is_end = (i == len(route) - 1)
            marker = 'D' if is_start else 'X'
            color = 'green' if is_start else 'red'
            ax.scatter(x, y, color=color, s=150, marker=marker, edgecolors='black', zorder=5)
            label_text = "INÍCIO" if is_start else "FIM"
            ax.text(x - 1, y, label_text, va='center', ha='right', color=color, fontweight='bold', fontsize=10)
        elif side == 'F':
            # Connection points at the end of the corridor
            ax.scatter(x, y, color='#95a5a6', s=50, marker='s', zorder=3)

    # Formatting
    ax.set_xlabel('Comprimento do Corredor (Metros)', fontsize=12)
    ax.set_ylabel('')
    ax.set_title('PLANO DE COLETA OTIMIZADO', fontsize=18, fontweight='bold', pad=25)
    
    # Custom Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['A'], markersize=12, label='Pedidos no corredor A'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['B'], markersize=12, label='Pedidos no corredor B'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=colors['C'], markersize=12, label='Pedidos no corredor C'),
        Line2D([0], [0], color='black', lw=2, label='Trajetória de coleta'),
        Line2D([0], [0], color='#7f8c8d', lw=3, label='Corredor de saída (F)'),
        Line2D([0], [0], marker='D', color='w', markerfacecolor='green', markersize=10, label='Ponto de Partida'),
        Line2D([0], [0], marker='X', color='w', markerfacecolor='red', markersize=10, label='Ponto de Entrega'),
    ]
    ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.15), 
              ncol=4, frameon=True, fancybox=True, shadow=True, fontsize=10)

    ax.set_yticks([]) 
    ax.set_xlim(-10, max_col * col_width + 10)
    ax.set_ylim(-4, 14)
    ax.set_axis_off() # Beautiful clean layout
    
    # Add a border for the armazem
    rect_border = patches.Rectangle((-10, -3), max_col * col_width + 10, 16, 
                                   linewidth=2, edgecolor='#2c3e50', facecolor='none', alpha=0.3, zorder=-2)
    ax.add_patch(rect_border)

    plt.tight_layout()
    plt.savefig('picking_route_2d.png', dpi=150, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    # Test route reflecting the user's requested sequence:
    # 1. Path A: (I,0,1) -> (F,37,1)
    # 2. Cycle B: (F,37,1) -> (F,37,1)
    # 3. Path C: (F,37,1) -> (I,0,1)
    test_route = [
        ('A', ('I', 0, 1)),
        ('A', ('L', 5, 2)),
        ('A', ('F', 37, 1)), # End of A path
        ('B', ('F', 37, 1)), # Transition to B cycle
        ('B', ('R', 10, 5)),
        ('B', ('L', 20, 3)),
        ('B', ('F', 37, 1)), # End of B cycle
        ('C', ('F', 37, 1)), # Transition to C path
        ('C', ('R', 30, 2)),
        ('C', ('I', 0, 1))  # Exit via C
    ]
    plot_picking_route(test_route)
