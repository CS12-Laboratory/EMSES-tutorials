#!/bin/bash
#SBATCH -p gr10451a
#SBATCH --rsc p=112:t=1:c=1
#SBATCH -t 120:00:00
#SBATCH -o stdout.%J.log
#SBATCH -e stderr.%J.log

# set -x
module load intel/2023.2 intelmpi/2023.2
module list

case_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
repo_dir=$(cd "$case_dir/.." && pwd)
cd "$case_dir" || exit 1

if [ -f "$repo_dir/.venv/bin/activate" ]; then
    source "$repo_dir/.venv/bin/activate"
else
    echo "Repository-local venv is missing: $repo_dir/.venv" >&2
    echo "Run emses-tutorials setup from the QuickStart first." >&2
    exit 1
fi

input_file=./plasma.toml
if [ ! -f "$input_file" ]; then
    echo "plasma.toml is required for this tutorial. Legacy plasma.inp/preinp files are archived under .old/." >&2
    exit 1
fi

export EMSES_DEBUG=no

date

rm -f *_0000.h5
srun ./mpiemses3D "$input_file"

date

# Postprocessing(visualization code, etc.)
mypython plot.py ./
