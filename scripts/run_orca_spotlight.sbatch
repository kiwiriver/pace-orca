#!/bin/bash
#SBATCH --job-name=rapid          # Job name
#SBATCH --ntasks=1                      # Number of tasks
#SBATCH --partition=research            # SLURM partition (adjust as necessary)

# Activate your Python environment
mamba=/accounts/mgao1/.local/bin/mamba
$mamba activate py3.12  # Replace with your environment name if different
echo "activate" $mamba

#location of the python file

pyfile="/mnt/mfs/mgao1/analysis/github/mapoltool/lab/orca/tools/orca_run.py"
echo "Using file: $pyfile"

#load environment variable for package path and key path
export MAPOLTOOL_LAB_PATH="/mnt/mfs/mgao1/analysis/github/mapoltool/lab/orca/"
export MAPOLTOOL_KEY_PATH="/mnt/mfs/mgao1/analysis/github/mapoltool/lab/key/"

# Output confirmation
echo "Using file: $pyfile"

#set timestamp
#timestamp='20240906T202704'
#timestamp='20250109T200019'
timestamp='20250404T005140'
#timestamp='20250621T172107'
#timestamp='20250612T165904'
#timestamp='20251117T172232'
#timestamp='20251124T101339'
tspan_start='None'
tspan_end='None'

#set time span
#timestamp="None"
#tspan_start='2025-11-17'
#tspan_end='2025-11-17'

#product=$1  # First parameter to the script (e.g., harp2_fastmapol, spexone_fastmapol)
product="harp2_fastmapol"
#product="spexone_fastmapol"
#product="spexone_remotap"

#configure min aod for selecting pixels and plot

#highlight high aod event
#aod_min_default=0.4
#aod_min_plot_default=0.4

#include more pixels
aod_min_default=0.01
aod_min_plot_default=0.01

npixel_min_default=1

#where to save the html files
#destination_folder="/mnt/mfs/FILESHARE/meng_gao/rapid_pace/html/"
destination_folder="/mnt/mfs/FILESHARE/meng_gao/pace/spotlight/html/"

# Execute the Python script
#python=/accounts/mgao1/miniforge3/bin/python
python=/accounts/mgao1/miniforge3/envs/py3.12/bin/python
$python $pyfile --timestamp "$timestamp" --tspan_start "$tspan_start" --tspan_end "$tspan_end" --product "$product" \
	--aod_min_default $aod_min_default  --aod_min_plot_default $aod_min_plot_default \
	--npixel_min_default $npixel_min_default \
	--destination_folder "$destination_folder" --no_cloud --plot_filter

#if keep the l1c and l2 file set -no_rm
#if download data from oel data server, not earthdata cloud set --no_cloud

