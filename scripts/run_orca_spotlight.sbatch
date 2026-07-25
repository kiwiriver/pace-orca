#!/bin/bash
#SBATCH --job-name=rapid          # Job name
#SBATCH --ntasks=1                      # Number of tasks
#SBATCH --partition=research            # SLURM partition (adjust as necessary)

# Activate your Python environment
mamba=/accounts/mgao1/.local/bin/mamba
$mamba activate py3.12  # Replace with your environment name if different
echo "activate" $mamba

#location of the python file

#pyfile="/mnt/mfs/mgao1/analysis/github/mapoltool/lab/orca/tools/orca_run.py"
pyfile="/mnt/mfs/mgao1/analysis/github/pace-orca/tools/orca_run.py"

echo "Using file: $pyfile"

#load environment variable for package path and key path
#export MAPOLTOOL_LAB_PATH="/mnt/mfs/mgao1/analysis/github/mapoltool/lab/orca/"
export MAPOLTOOL_KEY_PATH="/mnt/mfs/mgao1/analysis/github/mapoltool/lab/key/"
export MAPOLTOOL_LAB_PATH="/mnt/mfs/mgao1/analysis/github/pace-orca/"

# Output confirmation
echo "Using file: $pyfile"

###############################################
#set timestamp manually search online
input_data_path='None'

#wild fire in us
timestamp='20260701T192832'

header='land_v4.0'
suite1='L2.MAPOL_LAND'
l2str='V4_0'
l2str=$suite1.$l2str
echo $l2str

##############################################
#set searching path manually
#input_data_path='/accounts/mgao1/mfs_pace/rapid/test/test_coco/'

##############################################################################

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

#include more pixels, 0, 0.01
aod_min_default=0.001 #filtering
aod_min_plot_default=0.001 #plot
aod_max_plot_default=1.0
#aod_max_plot_default=0.5

npixel_min_default=1

#where to save the html files
#destination_folder="/mnt/mfs/FILESHARE/meng_gao/rapid_pace/html/"
destination_folder="/mnt/mfs/FILESHARE/meng_gao/pace/spotlight/html/"

# Execute the Python script
#python=/accounts/mgao1/miniforge3/bin/python
#python=/accounts/mgao1/miniforge3/envs/py3.12/bin/python
#$python xxx
python $pyfile --timestamp "$timestamp" --tspan_start "$tspan_start" --tspan_end "$tspan_end" \
       --product "$product" --header "$header" --l2str "$l2str"\
	--aod_min_default $aod_min_default  --aod_min_plot_default $aod_min_plot_default --aod_max_plot_default $aod_max_plot_default \
	--npixel_min_default $npixel_min_default --input_data_path "$input_data_path" \
	--destination_folder "$destination_folder" --no_cloud --plot_filter --no_rm --do_not_ask_ai

#if do_not_ask_ai then no api will be called to save time


#if keep the l1c and l2 file set -no_rm
#if download data from oel data server, not earthdata cloud set --no_cloud

