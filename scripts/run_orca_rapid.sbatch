#!/bin/bash
#SBATCH --job-name=rapid          # Job name
#SBATCH --ntasks=1                      # Number of tasks
#SBATCH --partition=research            # SLURM partition (adjust as necessary)

# Activate your Python environment
mamba=/accounts/mgao1/.local/bin/mamba
$mamba activate py3.12  # Replace with your environment name if different
echo "activate" $mamba

pyfile="/mnt/mfs/mgao1/analysis/github/mapoltool/lab/orca/tools/orca_run.py"
echo "Using file: $pyfile"

#load environment variable for package path and key path                                                                         
export MAPOLTOOL_LAB_PATH="/mnt/mfs/mgao1/analysis/github/mapoltool/lab/orca/"
export MAPOLTOOL_KEY_PATH="/mnt/mfs/mgao1/analysis/github/mapoltool/lab/key/"

# Set the tspan_start to one day ago based on current time
#tspan_start=$(date -d "yesterday" "+%Y-%m-%d")  # e.g., "2025-10-01"
tspan_start=$(date -d "2 day ago" "+%Y-%m-%d")

# Set tspan_end to the same date (adjust this if needed)
tspan_end="$tspan_start"

#test for a given granuel  20251029T044528
#tspan_start="2025-10-29T04:45:00"
#tspan_end="2025-10-29T04:50:00"

# Read the product passed by the cron job
product=$1  # First parameter to the script (e.g., harp2_fastmapol, spexone_fastmapol, spexone_remotap)

#direct set product
#product='harp2_fastmapol'
#product='spexone_fastmapol'
#product='spexone_remotap'

# Execute the Python script
python=/accounts/mgao1/miniforge3/envs/py3.12/bin/python
$python $pyfile --tspan_start "$tspan_start" --tspan_end "$tspan_end" --product "$product" --no_cloud
