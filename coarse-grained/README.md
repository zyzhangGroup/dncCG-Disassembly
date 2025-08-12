# Protein Thermal Dissociation Simulation Toolkit

## Installation

### Prerequisites
- CafeMol (https://www.cafemol.org/)
- MPI (for parallel execution)
- Python 3 with numpy, networkx, matplotlib

```bash
pip install numpy networkx matplotlib
```

## Project Structure

```
Setup/
├──em1.inp        # Input parameter file 1
├──em2.inp        # Input parameter file 2
├──protein.inp    # Main simulation input file
├──example.pdb    # Example protein structure file
└──final_contact.txt  # Final contact information
Script/
├──T_Sub          # Subunit analysis executable
└──T_Sub.c        # Source code for subunit analysis
analysis.py       # Analysis disassembly order script
submit_run.sh     # Job submission script
temp_submit_run.py # Main simulation control script
```

## Complete Workflow

### 1. Initial Structure Preparation
```bash
cd Setup/
cafemol em1.inp
```

### 2. Contact Analysis Bridge
1. Copy `em1.ninfo` to your all-atom analysis directory
2. Perform contact analysis
3. Copy results back as `final_contact.txt`

### 3. File Processing
```bash
# Process PDB files
awk 'n==1{print} $0~/MODEL         2/{n=1}' "em1.pdb" > "em1cg.pdb"

# Process ninfo file 
awk '{print} /coef_go\(kcal\/mol\) = factor_go \* icon_dummy_mgo \* cgo1210 \* energy_unit_protein/ {exit}' em1.ninfo > temp.txt && mv temp.txt em1.ninfo

# Append contact results
cat final_contact.txt >> em1.ninfo
echo ">>>>" >> em1.ninfo
```

### 4. Secondary Simulation
```bash
cafemol em2.inp
awk 'n==1{print} $0~/MODEL         2/{n=1}' "em2.pdb" > "em2cg.pdb"
cd ../
```

### 5. Main Simulation Execution
```bash
nohup python temp_submit_run.py > temp.log &
```

### 6. Results Analysis
```bash
python analysis.py
```

## Configuration

Edit `temp_submit_run.py`:

```python
# Temperature range (K)
T_min = 300
T_max = 500  

# Protein details
n_subunits = 3         # Number of subunits/chains
protein_name = 'example'  # Base name for input files

# Compute resources
nodelist = ['node16', 'node17', 'node18', 'node19']  # Available nodes
```

## Output Files

```
Results/
├── run/               # Intermediate files
└── result.png         # Dissociation visualization
```
