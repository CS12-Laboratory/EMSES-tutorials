#!/bin/bash
#SBATCH -p gr10451a
#SBATCH --rsc p=32:t=1:c=1
#SBATCH -t 120:00:00
#SBATCH -o stdout.%J.log
#SBATCH -e stderr.%J.log

# set -x
module load intel/2023.2 intelmpi/2023.2
module load hdf5/1.12.2_intel-2023.2-impi
module load fftw/3.3.10_intel-2022.3-impi
module list

input_file=./plasma.inp
if [ -f ./plasma.toml ]; then
    input_file=./plasma.toml
elif [ -f ./plasma.preinp ]; then
    preinp
fi

export EMSES_DEBUG=no

date

rm *_0000.h5
srun ./mpiemses3D "$input_file"

date

# Postprocessing(visualization code, etc.)
mypython plot.py ./
