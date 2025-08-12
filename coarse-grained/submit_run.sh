#!/bin/bash

# Extract job parameters
TEMP=$1
NODE=$2
N_SUB=$3
NAME="$4"
INP=protein.inp
N_LINES=$((N_SUB * (N_SUB - 1) / 2))


mkdir -p "$TEMP" || { echo "Failed to create directory: $TEMP"; exit 1; }

cd "$TEMP" || { echo "Failed to change to directory: $TEMP"; exit 1; }

cp ../../Setup/{em2cg.pdb,em1.ninfo} .
sed -e "s/tempk = 300.0/tempk = $TEMP/g"  "../../Setup/$INP" > "$INP"
wait

# Write nodename to nodefile
printf "%s" "$NODE" > nodefile.txt

# Run a job and wait for its completion using INP file from TEMP directory as input, save output to TEMP.out
mpirun -hostfile nodefile.txt cafemol "${INP}" > ${TEMP}.out
wait

# Process output using NAME.ts as input, save output to qscore_inter.txt
tail -n "$N_LINES" ${NAME}.ts | awk '{print $8}' > qscore_inter.txt
wait

# Call the test script with N_SUB and qscore_inter.txt as arguments
../../Script/T_Sub "$N_SUB" qscore_inter.txt
wait