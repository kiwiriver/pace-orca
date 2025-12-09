#!/bin/bash
#SBATCH --job-name=rapid_harp2          # Job name
#SBATCH --ntasks=1                    # Number of tasks
#SBATCH --partition=research             # SLURM partition (adjust as necessary)

# Activate your Python environment with required dependencies
mamba activate py3.12  # Adjust this to your Python environment name

#python /accounts/mgao1/github/mapoltool/tools/detection/detection_run.py

# Run the Python script with the necessary arguments
# on poseidon
# Define two possible file paths
file1="/home/mgao/github/mapoltool/tools/detection/detection_run.py"
file2="/accounts/mgao1/github/mapoltool/tools/detection/detection_run.py"

# Check if the first file exists
if [ -f "$file1" ]; then
    pyfile="$file1"  # Use file1 if found
elif [ -f "$file2" ]; then
    pyfile="$file2"  # Use file2 if found
else
    echo "Neither file exists. Exiting."
    exit 1  # Exit if neither file is found
fi

# Output the chosen file path
echo "Using file: $pyfile"

#pyfile="/home/mgao/github/mapoltool/tools/detection/detection_run.py"
#pyfile="/accounts/mgao1/github/mapoltool/tools/detection/detection_run.py"

#tspan = ("2025-09-20", "2025-09-20")
#tspan_start="2024-09-30"
#tspan_start="2025-01-09"
tspan_start="2025-09-29"
#tspan_start="2025-09-30"
tspan_start="2025-10-01"

tspan_end=$tspan_start

product='harp2_fastmapol'
#product='spexone_fastmapol'
#product='spexone_remotap'
    
appkey="KEY_REDACTED"
api_key="KEY_REDACTED"

sed "s/<appkey>/\"$appkey\"/g" $pyfile | sed "s/<api_key>/\"$api_key\"/g" > newpyjob.py


python newpyjob.py --tspan_start $tspan_start --tspan_end $tspan_end --product $product
