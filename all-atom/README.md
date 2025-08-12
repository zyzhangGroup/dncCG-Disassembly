# Contact Analysis Tool for All-atom Molecular Dynamics

## Overview
This Python script analyzes protein contact dynamics from molecular dynamics simulations. It processes protein structures, identifies residue contacts, calculates contact frequencies across trajectories, and generates normalized contact data for further analysis.

## Environment Setup

### Conda Environment

```
conda create -n mda python=3.10.6
conda activate mda
```

### Core Dependencies

```
conda install -c conda-forge \
    mdanalysis=2.8.0 \
    numpy=1.26.4 \
    scipy=1.15.1 \
    tqdm=4.67.1 \
    joblib=1.4.2 \
    scikit-learn=1.6.1
```

## Input Files
1. **Protein Structure**: PDB file (`example.pdb`)
2. **Contact Information**: `em1.ninfo` file from CafeMol energy minimization
3. **Trajectory Data**:
   - Reference structure (`ref.pdb`)
   - Fitted trajectory (`fit.xtc`)

## Output Files
| File                | Description                                        |
| ------------------- | -------------------------------------------------- |
| `contact.txt`       | Extracted contact pairs from em1.ninfo             |
| `protein.pdb`       | Processed protein structure without hydrogen atoms |
| `contact_count.npy` | Contact counts per frame (binary NumPy format)     |
| `new_contact.txt`   | Normalized contact data with statistics            |
| `final_contact.txt` | Final contact data with scaled parameters          |

## Usage
```bash
python contact_analysis.py
```

