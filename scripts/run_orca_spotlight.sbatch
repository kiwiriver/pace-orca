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

#set timestamp
#timestamp='20240906T202704'
#timestamp='20250109T200019'
#timestamp='20250404T005140'
#timestamp='20250621T172107'
#timestamp='20250612T165904'
#timestamp='20251117T172232'
#timestamp='20251124T101339'
#timestamp='20260203T053050'
#timestamp='20260130T194428'
#timestamp='20240815T110624'
#timestamp='20240815T110623'

#timestamp='20241201T202708'
#timestamp='20241210T203953'
#timestamp='20250115T201156'
#timestamp='20250109T200019'
#timestamp='20250109T200519'
#timestamp='20250110T203003'
#timestamp='20250110T203503'
#timestamp='20250531T181236'
#timestamp='20250712T212833'
#timestamp='20250712T212833'
#timestamp='20240930T193040'
#timestamp='20240930T210857'
#timestamp='20250109T200019'
#timestamp='20250531T181236'
#timestamp='20240927T205927'
#timestamp='20260319T181104'

#black smoke
#timestamp='20260416T095302'

#wind shadow
timestamp='20260216T225500'

input_data_path='None'
#header='V3'
header='V3_wind' 
#l2str='obdaac'
l2str='V3' #V3_0

echo $l2str

#header: outputfile_header = outputfile_header + header+'_'
#add the header to the l2 and l1 output folder path
#l2str: identify the l2 file
#print("path to check:", data_path+f'/*{l2str}*.nc')
#########################################################################
#timestamp='20240927T210427'                                                                                                            
#input_data_path='/mnt/mfs/mgao1/develop/fastmapol/test2026/test9_global/data_gitlab/data_hipp4.7/land_v4.2_d1/test/'
#input_data_path='/mnt/mfs/mgao1/develop/fastmapol/test2026/test9_global/data_gitlab/data_hipp4.7/land_v4.2_d1/'
timestamp='20240930T024250'
#austrilia
input_data_path='/accounts/mgao1/mfs_pace/pace/spotlight/data_tmp_aus/'
#/mnt/mfs/FILESHARE/meng_gao/pace/spotlight/html/harp2_fastmapol_land_v4.0_20240930T024250_n7_aod0.001_chat5.html
header='land_v4.0'
suite1='L2.MAPOL_LAND'
#l2str='V4.0'
l2str='V4_0'
l2str=$suite1.$l2str
echo $l2str 


timestamp='20240930T024250'
#railroad                                                                                                                                    
input_data_path='/accounts/mgao1/mfs_develop/fastmapol/test2026/test10_v4/land_v4.5_var1/HARP2/railroad/'
header='land_v4.5'
suite1='L2.MAPOL_LAND'
l2str='V4_v4.5_var1_d1'
l2str=$suite1.$l2str
echo $l2str
#/mnt/mfs/FILESHARE/meng_gao/pace/spotlight/html/harp2_fastmapol_land_v4.5_20240930T024250_n2_aod0.001_chat5.html


timestamp='20240930T193040'
#fire
input_data_path='/accounts/mgao1/mfs_develop/fastmapol/test2026/test10_v4/land_v4.6_var1/HARP2/spot/'
header='land_v4.6'
suite1='L2.MAPOL_LAND'
l2str='V4_v4.6_var1_d1'
l2str=$suite1.$l2str
echo $l2str

#########################################################################
#timestamp='20240927T210427'
#header='hipp4.6_public'
#input_data_path='/accounts/mgao1/mfs_develop/fastmapol/test2026/test9_global/data_public/data_hipp4.6/'

#suite1='L2.MAPOL_LAND'
#suite1='L2.MAPOL_OCEAN'

#l2str='V4.0.'
#l2str=$suite1.$l2str
#echo $l2str

#header='hipp4.6_gitlab'$l2str
#input_data_path='/accounts/mgao1/mfs_develop/fastmapol/test2026/test9_global/data_gitlab/data_hipp4.6_pr1/'
#header='hipp4.7_gitlab'$l2str

tspan_start='None'
tspan_end='None'



######################################################################################
#coco from Carina
timestamp='20260504T165915'
#timestamp='20260504T170415'
#
#input_data_path='None'
input_data_path='/accounts/mgao1/mfs_pace/rapid/test/test_coco/'

header='V3_Coco'
suite1='L2.MAPOL_OCEAN'
l2str='V'
l2str=$suite1.$l2str
#l2str=$suite1

#tspan_start='2026-05-04'
#tspan_end='2026-05-04'


##############################################################################

#tspan_start='None'
#tspan_end='None'

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
#aod_max_plot_default=1.0
aod_max_plot_default=0.5

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
	--destination_folder "$destination_folder" --no_cloud --plot_filter --no_rm


        #--do_not_ask_ai

#if keep the l1c and l2 file set -no_rm
#if download data from oel data server, not earthdata cloud set --no_cloud

