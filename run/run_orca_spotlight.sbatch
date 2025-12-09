#!/bin/bash
#SBATCH --job-name=rapid          # Job name
#SBATCH --ntasks=1                      # Number of tasks
#SBATCH --partition=research            # SLURM partition (adjust as necessary)

#useful command
#timedatectl
#date
#systemctl status cron


# Activate your Python environment
mamba=/accounts/mgao1/.local/bin/mamba
$mamba activate py3.12  # Replace with your environment name if different
echo "activate" $mamba

# Paths to the Python scripts
file1="/home/mgao/github/mapoltool/tools/detection/detection_run.py"
file2="/accounts/mgao1/github/mapoltool/tools/detection/detection_run.py"

# Verify which script to use
if [ -f "$file1" ]; then
    pyfile="$file1"
elif [ -f "$file2" ]; then
    pyfile="$file2"
else
    echo "Neither file exists. Exiting."
    exit 1
fi

# Output confirmation
echo "Using file: $pyfile"

# Set the tspan_start to one day ago based on current time
#tspan_start=$(date -d "yesterday" "+%Y-%m-%d")  # e.g., "2025-10-01"
tspan_start=$(date -d "1 day ago" "+%Y-%m-%d")
tspan_start=$(date -d "2 day ago" "+%Y-%m-%d")
#tspan_start=$(date -d "10 day ago" "+%Y-%m-%d")

#PACE_HARP2.20250621T172107.L2.MAPOL_OCEAN.V3_0.nc

# Set tspan_end to the same date (adjust this if needed)
tspan_end="$tspan_start"

tspan_start="2025-06-21T17:15:00"
tspan_end="2025-06-21T17:30:00"

# Read the product passed by the cron job
#product=$1  # First parameter to the script (e.g., harp2_fastmapol, spexone_fastmapol)
product="harp2_fastmapol"

# Replace placeholders for appkey and api_key
appkey="KEY_REDACTED"
api_key="KEY_REDACTED"

sed "s/<appkey>/\"$appkey\"/g" "$pyfile" | sed "s/<api_key>/\"$api_key\"/g" > newpyjob.py

aod_min_default=0.1
aod_min_plot_default=0.1
npixel_min_default=10
#destination_folder="/mnt/mfs/FILESHARE/meng_gao/rapid_pace/html/"
destination_folder="/mnt/mfs/FILESHARE/meng_gao/pace/spotlight/html/"

# Execute the Python script
#python=/accounts/mgao1/miniforge3/bin/python
python=/accounts/mgao1/miniforge3/envs/py3.12/bin/python
$python newpyjob.py --tspan_start "$tspan_start" --tspan_end "$tspan_end" --product "$product" \
	--aod_min_default $aod_min_default  --aod_min_plot_default $aod_min_plot_default \
	--npixel_min_default $aod_min_plot_default \
	--destination_folder "$destination_folder"

