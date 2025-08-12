import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def matrix_to_graph(matrix):
    """
    Convert a Q-score matrix into a NetworkX graph.
    Each non-zero entry in the upper triangle represents an edge between two units.
    """
    G = nx.Graph()
    n = len(matrix)
    
    # Add nodes: unit1, unit2, ...
    for i in range(n):
        G.add_node('unit' + str(i + 1))
    
    # Add edges where Q-score != 0
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i][j] != 0.0:
                G.add_edge('unit' + str(i + 1), 'unit' + str(j + 1))
    return G



# Load Q-score data
jobs_directory = 'run'  # directory containing simulation results
os.chdir(jobs_directory)
T_list0 = os.listdir('.') 
T_list0.sort()

qscore_inter = []   # store raw qscore_inter.txt data
qscore_matrix = []  # store reconstructed symmetric matrices
T_list = []         # store temperatures

for T in T_list0:
    try:
        # Read Q-score upper triangle
        data = np.loadtxt(os.path.join('.', T, 'qscore_inter.txt'))
        qscore_inter.append(data)

        # Infer number of subunits from number of data points
        n_subunits = int((1 + np.sqrt(1 + 8 * len(data))) / 2)

        # Fill upper triangle
        tri_upper = np.triu(np.ones((n_subunits, n_subunits)), 1)
        tri_upper[tri_upper == 1] = data

        # Make matrix symmetric
        tri_upper += tri_upper.T
        qscore_matrix.append(tri_upper)

        # Store temperature
        T_list.append(float(T))
    except Exception:
        continue

# Find connected components for each matrix
units_data = [list(nx.connected_components(matrix_to_graph(q_matrix))) for q_matrix in qscore_matrix]

combined_data = []  # unique (temperature, connected_components) pairs
units_set = set()

for units, value in zip(units_data, T_list):
    # Sort nodes inside each connected component
    units_tuple = tuple(tuple(sorted(unit)) for unit in units)
    if units_tuple not in units_set:
        combined_data.append((str(value) + "K", units))
        units_set.add(units_tuple)

# Print results
for data in combined_data:
    print(data)

# Plot graphs for each temperature
num_plots = len(combined_data)
cols = 3  # number of columns in subplot
rows = (num_plots + cols - 1) // cols  
fig, axes = plt.subplots(rows, cols, figsize=(18, rows * 6))

for idx, (temp, units) in enumerate(combined_data):
    row = idx // cols
    col = idx % cols
    ax = axes[row, col] if rows > 1 else axes[col]
    
    # Get Q-score matrix for the current temperature
    q_matrix = qscore_matrix[T_list.index(float(temp[:-1]))]
    G = matrix_to_graph(q_matrix)
    
    # Circular layout
    pos = nx.circular_layout(G)  
    
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=np.linspace(0, 1, G.number_of_nodes()),# gradient values
        cmap=plt.cm.tab20, 
        node_size=1300,
        edgecolors='#2b4f60',
        linewidths=1.5,
        alpha=1
    )
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        width=2.0,
        edge_color="#000000",
        alpha=0.5
    )
    nx.draw_networkx_labels(
        G, pos, ax=ax,
        font_size=11,
        font_weight='bold',
        font_color='black'
    )
    
    ax.set_title(temp, fontsize=15, fontweight='bold')
    ax.axis('off')

    ax.margins(0.25)
    ax.set_aspect('equal')

# Remove unused subplots
for idx in range(num_plots, rows * cols):
    fig.delaxes(axes.flatten()[idx])

plt.tight_layout()
plt.subplots_adjust(wspace=0.3, hspace=0.3) 
plt.savefig('../result.png', dpi=300)
# plt.show()
