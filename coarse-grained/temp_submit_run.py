# Import required libraries
import os
import numpy as np
import subprocess
from multiprocessing import Pool

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


# Define a function to group and print temperatures
def group_and_print_temperatures(T_subunit):
    """
    Groups temperature subunits with their corresponding numbers and prints the results.
    
    param T_subunit: A list of temperature subunits
    """
    dict = {}

    # Group temperatures by their values
    for index, temperature in enumerate(T_subunit):
        subunit_id = index + 1
        if temperature not in dict:
            dict[temperature] = []
        dict[temperature].append(subunit_id)
    
    # Sort the temperatures in ascending order
    sorted_temp = sorted(dict.keys())

    # Print the temperatures and their corresponding subunit IDs
    for temp_i in sorted_temp:
        temp_list = dict[temp_i]
        print(f"Temperature: {temp_i}K, subunit ID: {temp_list}")

# Create the jobs directory
os.makedirs('run', exist_ok=True)
os.chdir('run')

# Run the simulations
temps = np.linspace(T_min,T_max,len(nodelist))
run_simulation('.', '../submit_run.sh', temps, len(nodelist), n_subunits, nodelist, protein_name)
print("First simulation is done")

# mian loop
while True:
    T_subunit = np.zeros(n_subunits) 
    T_list = [] # T_list is a list of temperature
    T_lists = [] # T_list is a list of temperature pairs
    deltaT = [] # deltaT is a list of temperature differences
    deltaSub = [] # deltaSub is a list of subunit differences
    sub_num = [] # sub_num is a list of subunit numbers

    T_list0 = sorted(os.listdir('.')) # T_list0 is a list of temperatures of finished simulation
    subunit_matrix = [] 
    print(T_list0)
    # T_list is the temperature list of finished simulation
    for T in T_list0:
        try:
            subunit_matrix.append(np.loadtxt(os.path.join('.', T, 'subunit.txt')))
            T_list.append(float(T))
        except Exception:
            continue

    subunit_matrix = np.array(subunit_matrix) # subunit_matrix is a matrix of subunit numbers
    sub_num = np.sum(subunit_matrix, axis=1) # sub_num is the number of dissociated subunits at each temp

    # Group and print temperatures
    m = len(T_list)
    for j in range(n_subunits):
        for i in range(m - 1):
            if subunit_matrix[i, j] != subunit_matrix[i + 1, j]:
                T_subunit[j] = T_list[i + 1]
                delta_Sub = sub_num[i + 1] - sub_num[i] 
                delta_T = T_list[i + 1] - T_list[i] 
                if delta_T > 1.0 and delta_Sub > 1.0: 
                    T_lists.append([T_list[i], T_list[i + 1]]) 
                    deltaT.append(delta_T) 
                    deltaSub.append(delta_Sub)
                else: 
                    break

    if not T_lists:
        group_and_print_temperatures(T_subunit)
        print("Work is done")
        break

    # Sort the temperatures by temperature difference and subunit difference    
    # tem_sorted = []
    # for i in range(len(deltaT)): 
    #     tem_sorted.append([T_lists[i], deltaSub[i], deltaT[i]])
    # tem_sorted = sorted(tem_sorted, key=lambda x : (-x[2], -x[1])) 
    tem_sorted = sorted(zip(T_lists, deltaSub, deltaT), key=lambda x: (-x[2], -x[1]))

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
    for i, (temp_range, d_sub, d_T) in enumerate(tem_uniq):
        temp_l.extend(np.linspace(float(temp_range[0]), float(temp_range[1]), node_sub[i] + 2)[1:-1])

    # Round the temperature numbers to the nearest integer
    temp_list = np.unique(np.rint(temp_l))

    # Generate commands
    run_simulation('.', '../submit_run.sh', temp_list, len(nodelist), n_subunits, nodelist, protein_name)

