#!/bin/bash

#SBATCH -t 350:00:00
#SBATCH --mem=64G
#SBATCH -n 1
#SBATCH --mail-type=ALL
#SBATCH -c 3
#SBATCH --mail-user=<YOUR EMAIL>
#SBATCH --account=<YOUR LAB'S OSCAR CONDO>

# source conda init bash 
# source conda deactivate

module load anaconda/3-5.2.0
source activate <YOUR CONDA ENVIRONMENT>

PYTHON_FILE='run_model_example.py'
BASH_OUTFILE='out_example.txt'

python3 $PYTHON_FILE > $BASH_OUTFILE 2>&1
