#!/bin/bash -l
#SBATCH -J r_single_proc
#SBATCH -t 00:30:00
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=6000

module load r-env
srun Rscript btl.R $*
