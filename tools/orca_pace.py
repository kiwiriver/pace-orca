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

def get_pace_data_info(product):
    """
    get pace data info
    """
    
    if(product=='harp2_fastmapol'):
        outputfile_header='harp2_fastmapol_'
        product_info_nrt={"short_name": "PACE_HARP2_L2_MAPOL_OCEAN_NRT", "sensor_id": 48, "dtid":1546, \
                             "sensor":"PACE_HARP2","suite1":"L1C.V3.5km", "suite2":"L2.MAPOL_OCEAN.V3.0.NRT"}
        product_info_refined={"short_name": "PACE_HARP2_L2_MAPOL_OCEAN", "sensor_id": 48, "dtid":1547, \
                              "sensor":"PACE_HARP2", "suite1":"L1C.V3.5km", "suite2":"L2.MAPOL_OCEAN.V3.0"}
    elif(product=='spexone_fastmapol'):
        outputfile_header='spexone_fastmapol_'
        product_info_nrt={"short_name": "PACE_SPEXONE_L2_MAPOL_OCEAN_NRT", "sensor_id": 41, "dtid":1970, \
                             "sensor":"PACE_SPEXONE","suite1":"L1C.V3.5km", "suite2":"L2.MAPOL_OCEAN.V3.0.NRT"}
        product_info_refined={"short_name": "PACE_SPEXONE_L2_MAPOL_OCEAN", "sensor_id": 41, "dtid":1971, \
                              "sensor":"PACE_SPEXONE", "suite1":"L1C.V3.5km", "suite2":"L2.MAPOL_OCEAN.V3.0"}
    
    elif(product=='spexone_remotap'):
        outputfile_header='spexone_remotap_'
        product_info_nrt={"short_name": "PACE_SPEXONE_L2_AER_RTAPOCEAN_NRT", "sensor_id": 41, "dtid":1350, \
                             "sensor":"PACE_SPEXONE","suite1":"L1C.V3.5km", "suite2":"L2.RTAP_OC.V3.0.NRT"}
        product_info_refined={"short_name": "PACE_SPEXONE_L2_AER_RTAPOCEAN", "sensor_id": 41, "dtid":1420, \
                              "sensor":"PACE_SPEXONE", "suite1":"L1C.V3.5km", "suite2":"RTAP_OC.V3.0"}
    else:
        print(product, "not available")
        outputfile_header=None
        product_info_nrt={}
        product_info_refined={}
        
    return outputfile_header, product_info_nrt, product_info_refined

def download_pace_data(tspan, product, appkey, api_key, path1='./pace_tmp/', \
                       flag_earthdata_cloud = False):
    #setup_data(tspan, sensor='PACE_HARP2', suite='MAPOL_OCEAN.V3.0', path1='./pace_tmp/')
    
    outputfile_header, product_info_nrt, product_info_refined = get_pace_data_info(product)
    
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