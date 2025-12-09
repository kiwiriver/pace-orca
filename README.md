<div align="right">
  <img src="logo/orca_logo1.png" alt="ORCA Logo" width="200"/>
</div>

# FastMAPOL Toolkit: ORCA
## Observation and Retrieval Characterization with AI

### Key Features

- **Automated Data Download**: Retrieve PACE HARP2, SPEXone L1C and L2 data for specified dates or via automated cron jobs
- **Smart Scene Detection**: Identify scenes meeting specific criteria (AOD range, spatial coverage) for aerosol event analysis
- **Advanced Visualization**: Generate comprehensive plots of aerosol properties from FastMAPOL or RemoTAP product suites
- **AI-Powered Analysis**: Integrate aerosol data with ChatGSFC for intelligent interpretation of aerosol types, sources, transport patterns, and impacts
- **Web Publishing**: Create and host HTML reports on OEL Fileshare

---

## Contribution

This repository is developed and maintained by the **PACE FastMAPOL team**. We welcome any contributions. 

### Related Projects

This toolkit supports **PACE Rapid Response Efforts**:
- **Main Repository**: [pace-rapid-response](https://github.com/skyecaplan/pace-rapid-response)
- **Basic Tools**: A foundational version for data download, aerosol detection, and plotting is available in the [tools directory](https://github.com/skyecaplan/pace-rapid-response/tree/main/dust/mapoltool/tools)

---

## 📊 Live Examples

### Spotlight Scenes
- **Example Scene**: [HARP2 FastMAPOL Analysis](https://oceancolor.gsfc.nasa.gov/fileshare/meng_gao/pace/spotlight/html/harp2_fastmapol_20251124T101339_n1_aod0.01_chat5.html)
- **Browse All**: [Spotlight Portal](https://oceancolor.gsfc.nasa.gov/fileshare/meng_gao/pace/spotlight)

### Rapid Response
- **Example Analysis**: [Daily Rapid Response](https://oceancolor.gsfc.nasa.gov/fileshare/meng_gao/rapid_pace/html/harp2_fastmapol_2025-12-03_2025-12-03_n4_aod0.3_chat5.html)
- **Browse All**: [Rapid Response Portal](https://oceancolor.gsfc.nasa.gov/fileshare/meng_gao/pace/rapid_response/)

---

## 🔐 API Key Configuration

For development and testing, configure your API keys:

1. **ChatGSFC API Key**: Save to `key/chatgsfc_api_key.txt`
2. **Earthdata App Key**: Save to `key/earthdata_appkey.txt`

> 🔒 **Security Note**: All files in the `key/` folder are automatically ignored by git

### Environment Variables

```bash
export MAPOLTOOL_KEY_PATH="/mnt/mfs/mgao1/analysis/github/mapoltool/lab/key/"
export MAPOLTOOL_LAB_PATH="/mnt/mfs/mgao1/analysis/github/mapoltool/lab/orca/"
```

## Installation & Configuration
### Custom HTML Headers

Configure custom header information in:
```bash
/tools/orca_header.py
```
## Testing

### Test scripts are available in the /test folder (results excluded from git):

### Spotlight Analysis
```bash
bash run_spot
```
### Rapid Response Analysis
```bash
bash run_rapid spexone_fastmapol
```


## Automated Processing
Set up cron jobs for automatic report generation:

### Cron Management Commands
```bash
crontab -l #list
crontab -e #edit
date #system date                                                                                                     
timedatectl #check and set system time
systemctl status cron #check cron job status
```

### Example Cron Configuration
```bash
0 5 * * * cd /accounts/mgao1/mfs_pace/rapid && bash run_orca_rapid.sbatch harp2_fastmapol >> rapid_log_harp2_fastmapol.log 2>&1
0 5 * * * cd /accounts/mgao1/mfs_pace/rapid && bash run_orca_rapid.sbatch spexone_fastmapol >> rapid_log_spexone_fastmapol.log 2>&1
0 5 * * * cd /accounts/mgao1/mfs_pace/rapid && bash run_orca_rapid.sbatch spexone_remotap >> rapid_log_spexone_remotap.log 2>&1
```
