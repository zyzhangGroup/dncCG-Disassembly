# Import required libraries
import os
import numpy as np
import subprocess
from multiprocessing import Pool
import networkx as nx

# Example usage
T_min = 300  #min temperature
T_max = 500  #max temperature
n_subunits = 3    #the number of subunits(chains)
protein_name = 'example'  #the name of proteins
nodelist = [ 'node16', 'node17', 'node18','node19']   # the nodelists

# Define a function to submit commands
def submit_command(cmd, cwd=None):
    try:
        subprocess.call(cmd, shell=True, cwd=cwd)
    # Catch any exceptions and print an error message
    except Exception as e:
        print("Failed to execute command: %s. Error: %s" % (cmd, str(e)))

# # Define a function to run simulations
def run_simulation(jobs_directory, job_name, temperatures, num_nodes, n_subunits, nodelist, project_name):
    with Pool(num_nodes) as pool:
        for node_i, temp_i in zip(nodelist, temperatures):
            command = '%s %.1f %s %d %s' % (job_name, float(temp_i), node_i, n_subunits, project_name)
            print(command)
            pool.apply_async(submit_command, args=(command, jobs_directory))
        pool.close()
        pool.join()

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

# Create result directory
os.makedirs('Result_Tq', exist_ok=True)

# Create the jobs directory
os.makedirs('run', exist_ok=True)
os.chdir('run')

# Run the simulations
temps = np.linspace(T_min,T_max,len(nodelist))
run_simulation('.', '../submit_run.sh', temps, len(nodelist), n_subunits, nodelist, protein_name)
print("First simulation is done")

# mian loop
while True:
    qscore_inter = []   # store raw qscore_inter.txt data
    qscore_matrix = []  # store reconstructed symmetric matrices
    T_list = []         # store temperatures
    T_lists = [] # T_list is a list of temperature pairs
    deltaT = [] # deltaT is a list of temperature differences
    deltaCmp = [] # deltaCmp is a list of connected_components differences
    T_list0 = sorted(os.listdir('.')) # T_list0 is a list of temperatures of finished simulation

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
        
    units_data = [list(nx.connected_components(matrix_to_graph(q_matrix))) for q_matrix in qscore_matrix]
    num_components_list = [len(list(nx.connected_components(matrix_to_graph(q_matrix)))) for q_matrix in qscore_matrix]

    for i in range(len(T_list)-1):
        delta_Cmp = num_components_list[i+1] - num_components_list[i]
        delta_T = T_list[i + 1] - T_list[i]
        if delta_T > 1.0 and delta_Cmp > 1.0:
            T_lists.append([T_list[i], T_list[i + 1]])
            deltaT.append(delta_T)
            deltaCmp.append(delta_Cmp)


    if not T_lists:        
        combined_data = []
        units_set = set()

        for units, value in zip(units_data, T_list):
            units_tuple = tuple(tuple(sorted(unit)) for unit in units)
            if units_tuple not in units_set:
                combined_data.append((str(value)+"K", units))
                units_set.add(units_tuple)

        # 输出合并后的数据
        for data in combined_data:
            print(data)
        print("Work is done")
        break

    # Sort the temperatures by temperature difference and subunit difference    
    tem_sorted = sorted(zip(T_lists, deltaCmp, deltaT), key=lambda x: (-x[2], -x[1]))

    # Unique the temperature pairs
    tem_uniq=[]
    for item in tem_sorted:
        if item not in tem_uniq :
            tem_uniq.append(item)

    # Assign subunit numbers to each temperature
    node_sub = np.zeros(len(tem_uniq), dtype=int) 
    for i in range(len(nodelist)):
        for j in range(len(tem_uniq)):
            temp = tem_uniq[j][2]
            if temp / (i + 1) > 1.0 and sum(node_sub) < len(nodelist):
                node_sub[j] = i + 1 
            else:
                break

    # Assign temperature numbers to each node
    temp_l = []
    for i, (temp_range, d_com, d_T) in enumerate(tem_uniq):
        temp_l.extend(np.linspace(float(temp_range[0]), float(temp_range[1]), node_sub[i] + 2)[1:-1])

    # Round the temperature numbers to the nearest integer
    temp_list = np.unique(np.rint(temp_l))

    # Generate commands
    run_simulation('.', '../submit_run.sh', temp_list, len(nodelist), n_subunits, nodelist, protein_name)

