import os
import requests
import csv
import glob
import shutil
from urllib.parse import urlparse
from io import StringIO
import pandas as pd
import earthaccess
from matplotlib import rcParams
from datetime import datetime, timedelta
from tools.orca_utility import setup_data
from tools.orca_download import download_l2_cloud, download_l2_web

import re

def parse_l2str(l2str):
    """
    Parse strings such as:
        L2.MAPOL_LAND.V4_0
        L2.MAPOL_OCEAN.V3_1

    Returns
    -------
    l1c_version : str
        Major version, e.g. "v4".
    l2_version : str
        Full version, e.g. "v4.0".
    surface : str
        "land" or "ocean".
    """

    l2str_upper = l2str.upper()

    # Determine surface
    if "LAND" in l2str_upper:
        surface = "land"
    elif "OCEAN" in l2str_upper:
        surface = "ocean"
    else:
        raise ValueError(
            f"Cannot determine surface from l2str: {l2str}"
        )

    # Extract version after ".V", such as V4_0 or V3_1
    match = re.search(r"\.V(\d+)(?:[_\.](\d+))?", l2str_upper)

    if match is None:
        raise ValueError(
            f"Cannot determine version from l2str: {l2str}"
        )

    major_version = match.group(1)
    minor_version = match.group(2)

    # L1C uses only the major version
    l1c_version = f"v{major_version}"

    # L2 uses major.minor
    if minor_version is not None:
        if major_version==3:
            l2_version = f"v{major_version}.{minor_version}"
        else:
            l2_version = f"v{major_version}_{minor_version}"
    else:
        l2_version = f"v{major_version}"

    return l1c_version, l2_version, surface
    
def get_pace_data_info(product, l1c_version='v3', l2_version='v3.0', surface='ocean'):
    """
    get pace data info
    """
    l1c_version=str(l1c_version).upper()
    l2_version=str(l2_version).upper()
    surface=str(surface).upper()
    
    if(product=='harp2_fastmapol'):
        
        outputfile_header='harp2_fastmapol_'
        product_info_nrt={"short_name": f"PACE_HARP2_L2_MAPOL_{surface}_NRT", "sensor_id": 48, "dtid":None, "sensor":"PACE_HARP2","suite1":f"L1C.{l1c_version}.5km", "suite2":f"L2.MAPOL_{surface}.{l2_version}.NRT"}
        product_info_refined={"short_name": f"PACE_HARP2_L2_MAPOL_{surface}", "sensor_id": 48, "dtid":None, "sensor":"PACE_HARP2", "suite1":f"L1C.{l1c_version}.5km", "suite2":f"L2.MAPOL_{surface}.{l2_version}.NRT"}

        #different file id for land and ocean data
        if surface=='OCEAN':
            product_info_nrt['dtid']=1546
            product_info_refined['dtid']=1547
        if surface=='LAND':
            product_info_nrt['dtid']=1247
            product_info_refined['dtid']=1246
            
    elif(product=='spexone_fastmapol'):
        #only ocean
        outputfile_header='spexone_fastmapol_'
        product_info_nrt={"short_name": f"PACE_SPEXONE_L2_MAPOL_{surface}_NRT", "sensor_id": 41, "dtid":1970,"sensor":"PACE_SPEXONE","suite1":f"L1C.{l1c_version}.5km", "suite2":f"L2.MAPOL_{surface}.{l2_version}.NRT"}
        product_info_refined={"short_name": f"PACE_SPEXONE_L2_MAPOL_{surface}", "sensor_id": 41, "dtid":1971, "sensor":"PACE_SPEXONE", "suite1":f"L1C.{l1c_version}.5km", "suite2":f"L2.MAPOL_{surface}.{l2_version}.NRT"}
    
    elif(product=='spexone_remotap'):
        #for ocean, need updata land
        outputfile_header='spexone_remotap_'
        product_info_nrt={"short_name": f"PACE_SPEXONE_L2_AER_RTAP{surface}_NRT", "sensor_id": 41, "dtid":1350, "sensor":"PACE_SPEXONE","suite1":f"L1C.{l1c_version}.5km", "suite2":f"L2.RTAP_OC.{l2_version}.NRT"}
        product_info_refined={"short_name": f"PACE_SPEXONE_L2_AER_RTAP{surface}", "sensor_id": 41, "dtid":1420, "sensor":"PACE_SPEXONE", "suite1":f"L1C.{l1c_version}.5km", "suite2":f"RTAP_OC.{l2_version}.NRT"}
    else:
        print(product, "not available")
        outputfile_header=None
        product_info_nrt={}
        product_info_refined={}
        
    return outputfile_header, product_info_nrt, product_info_refined
    
def download_pace_data(tspan, product, appkey, api_key, l2str='L2.MAPOL_LAND.V4_0',\
                       path1='./pace_tmp/', \
                       flag_earthdata_cloud = False):
    #setup_data(tspan, sensor='PACE_HARP2', suite='MAPOL_OCEAN.V3.0', path1='./pace_tmp/')


    l1c_version, l2_version, surface = parse_l2str(l2str)

    print("l1c_version:", l1c_version)  # v4
    print("l2_version:", l2_version)   # v4.0
    print("surface:", surface)      # land

    outputfile_header, product_info_nrt, product_info_refined = get_pace_data_info(
                        product,
                        l1c_version=str(l1c_version),
                        l2_version=str(l2_version),
                        surface=str(surface),
                    )

    if(flag_earthdata_cloud):
        auth = earthaccess.login(persist=True)
    
    # Change default font to something available
    rcParams['font.family'] = 'serif' 
    rcParams['font.size'] = '12' 
    
    day1 = tspan[0]+'_'+tspan[1]
    
    try:
        short_name=product_info_refined["short_name"]
        sensor_id=product_info_refined["sensor_id"]
        dtid=product_info_refined["dtid"]
        sensor =product_info_refined["sensor"]
        suite1 =product_info_refined["suite1"]
        suite2 = product_info_refined["suite2"]
        filelist_name=sensor+'_'+suite2+'_'+day1+'_filelist.txt'

        
        l2_path, l1c_path, plot_path, html_path = setup_data(tspan, sensor=sensor, suite=suite2, path1=path1)

        #print(sensor, suite1, suite2)
        #print(l2_path)
        
        if(flag_earthdata_cloud):
            filelist_l2 = download_l2_cloud(tspan, short_name=short_name, output_folder=l2_path)
        else:
            filelist_l2 = download_l2_web(tspan, appkey, output_folder=l2_path,  \
                                          sensor_id=sensor_id, dtid=dtid, filelist_name=filelist_name)

        #print(filelist_l2)
    except:
        short_name=product_info_nrt["short_name"]
        sensor_id=product_info_nrt["sensor_id"]
        dtid=product_info_nrt["dtid"]
        sensor =product_info_nrt["sensor"]
        suite1 =product_info_nrt["suite1"]
        suite2 = product_info_nrt["suite2"]
        filelist_name=sensor+'_'+suite2+'_'+day1+'_filelist.txt'
        l2_path, l1c_path, plot_path, html_path = setup_data(tspan, sensor=sensor, suite=suite2, path1=path1)
        if(flag_earthdata_cloud):
            filelist_l2 = download_l2_cloud(tspan, short_name=short_name, output_folder=l2_path)
        else:
            filelist_l2 = download_l2_web(tspan, appkey, output_folder=l2_path,\
                                         sensor_id=sensor_id, dtid=dtid, filelist_name=filelist_name)
    return l2_path, l1c_path, plot_path, html_path