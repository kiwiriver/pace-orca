<!---![FastMAPO Logo](img/fastmapol1.png)--->
<img src="logo/orca_logo1.png" alt="drawing" width="500"/>

# FastMAPOL Toolkit: ORCA-Observation and Retrieval Characterization with AI
Features:
- 1. download PACE HARP2, SPEXone L1C and L2 data for a given day (or automatically through cron)
- 2. find the scene satisfies given criteria (on aod range, spatial coverage etc) for aerosol event detection
- 3. generate plots on various aerosol properties from FastMAPOL or RemoTAP product suites
- 4. provide aerosol information to ChatGSFC for interpretation of aerosol type, source, transport, impacts
- 5. create an html page and hosted on OEL Fileshare
 
# Contribution
This repo is created by PACE FastMAPOL team. Any contribution is welcome.

## Add key for earthdata and chatgsfc
for development test:
- add the chatgsfc api key in key/chatgsfc_api_key.txt
- add earthdata appkey in key/earthdata_appkey.txt
- all the files inside the key folder will be ignored in the repository

location of the key can be set through environment variable

```
export MAPOLTOOL_KEY_PATH="/mnt/mfs/mgao1/analysis/github/mapoltool/lab/key/"
```

## Code installation
```
export MAPOLTOOL_LAB_PATH="/mnt/mfs/mgao1/analysis/github/mapoltool/lab/orca/"
```

## set customize html header information
```
/tools/orca_header.py
```

## test
copy code from /run into /test (will not be included in git repo)
modify for any timestamp and run
```
bash run_orca_spotlight.sbatch
```

modify for any given time (or default 1/2 days ago)
```
bash run_orca_rapid.sbatch spexone_fastmapol
```


## setup cron job for automatic rapid page generation
```
crontab -l #list
crontab -e #edit
date #system date                                                                                                     
timedatectl #check and set system time
systemctl status cron #check cron job status
```

crontab setup example:
```
0 5 * * * cd /accounts/mgao1/mfs_pace/rapid && bash run_orca_rapid.sbatch harp2_fastmapol >> rapid_log_harp2_fastmapol.log 2>&1
0 5 * * * cd /accounts/mgao1/mfs_pace/rapid && bash run_orca_rapid.sbatch spexone_fastmapol >> rapid_log_spexone_fastmapol.log 2>&1
0 5 * * * cd /accounts/mgao1/mfs_pace/rapid && bash run_orca_rapid.sbatch spexone_remotap >> rapid_log_spexone_remotap.log 2>&1
```
