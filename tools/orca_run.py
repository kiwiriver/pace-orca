"""
Run aerosol event detection code
Meng Gao, Sep 25, 2025

flag_earthdata_cloud: True, use earthaccess tool, need cloud access
flag_earthdata_cloud: False: use web search tool, replace your <appkey>


440, 550, 670, 870:
remotap [3, 7, 9, 13]
fastmapol [ 5, 21, 30, 33]
"""


import earthaccess
import requests

import os
import sys
import glob
import shutil
import numpy as np
import xarray as xr

import argparse
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from pathlib import Path
from matplotlib import rcParams
from datetime import datetime, timedelta

#add the path of the tools
#mapol_path=os.path.expanduser('~/github/mapoltool')
key_path = os.environ.get('MAPOLTOOL_KEY_PATH') or '../key/'
mapol_path = os.environ.get('MAPOLTOOL_LAB_PATH') or '/mnt/mfs/mgao1/analysis/github/mapoltool/lab/'
sys.path.append(mapol_path)

from tools.orca_html import *
from tools.orca_header import *
from tools.orca_plot import *
from tools.orca_utility import *
from tools.orca_download import *
from tools.orca_ai import *
from tools.orca_pace import *

from matplotlib import rcParams

import earthaccess

###########################
#aod_min_plot = 0.15 #may contain artifacts

#try:
# Add argument parsing with optional values for tspan_start and tspan_end

parser = argparse.ArgumentParser(description="Run PACE L2 daily processing script.")

parser.add_argument("--timestamp", type=str, default=None, help="timestamp, if given, ignoret span_start and tspan_end ")
parser.add_argument("--tspan_start", type=str, help="Start date of the time span (YYYY-MM-DD).")
parser.add_argument("--tspan_end", type=str, help="End date of the time span (YYYY-MM-DD).")
parser.add_argument("--product", type=str, help="product: harp2_fastmapol, ...")
parser.add_argument("--aod_min_default", type=float, default=None, \
                    help="set aod_min, if not set, use existing values")
parser.add_argument("--aod_min_plot_default", type=float, default=None, \
                    help="set aod_min_plot, if not set, use existing values")
parser.add_argument("--npixel_min_default", type=float, default=None, \
                    help="set npixel_min, if not set, use existing values")
parser.add_argument("--destination_folder", type=str, default="/mnt/mfs/FILESHARE/meng_gao/rapid_pace/html/",\
                    help="where to save the html")
parser.add_argument("--no_rm", action="store_true",
                       help="Do NOT remove files after finish (default: remove files)")
parser.add_argument("--no_cloud", action="store_true",
                       help="Do NOT use Earthdata cloud (default: use cloud)")
parser.add_argument("--plot_filter", action="store_true",
                       help="default plot everything, when specified plot filtered values")

args = parser.parse_args()

product = args.product

timestamp = args.timestamp

if timestamp and timestamp.lower() in ['none', 'null', '']:
    #or not given
    timestamp = None
    
if timestamp:
    print("use timestamp")
    # Parse timestamp and create time span with buffer
    dt = datetime.strptime(timestamp, '%Y%m%dT%H%M%S')
    buffer = timedelta(minutes=1)  # Adjust buffer as needed

    #ocationally, there could be 1 second difference between L1C and L2
    tspan_start = (dt - buffer).strftime('%Y-%m-%dT%H:%M:%S')
    #tspan_start = (dt).strftime('%Y-%m-%dT%H:%M:%S')
    tspan_end = (dt + buffer).strftime('%Y-%m-%dT%H:%M:%S')
    tspan = (tspan_start, tspan_end)
    
    print(f"Using timestamp: {timestamp}")
    print(f"Generated time span: {tspan}")

    tspan_web = format_tspan(tspan)
    print(f"web download format: {tspan_web}" )

else:
    print("use time range")
    # Use provided start and end times
    tspan_start = args.tspan_start
    tspan_end = args.tspan_end
    tspan = (tspan_start, tspan_end)
    
    print(f"Using provided time span: {tspan}")
    
    tspan_web = format_tspan(tspan)
    print(f"web download format: {tspan_web}" )
    
product = args.product
aod_min_default = args.aod_min_default
aod_min_plot_default = args.aod_min_plot_default
npixel_min_default = args.npixel_min_default
destination_folder = args.destination_folder
os.makedirs(destination_folder, exist_ok=True)

print("product=", product)
#load correct information for that product
outputfile_header, product_info_nrt, product_info_refined = get_pace_data_info(product)

if(product=='harp2_fastmapol'):
    outputfile_header='harp2_fastmapol_'
    
    dict1 = {'aod_min':[0.3,aod_min_default], \
         'aod_min_plot':[0.3, aod_min_plot_default],\
          'npixel_min':[100*40, npixel_min_default]}
    
    #100*100 early version
    #100*20 may be too less
        
    iv=[40, 5, 85] #nadir rgb
    iwvv=0
    ivp=iv
    iwvvp=iwvv
    
    iwv550=1 #550 for aod_min
    iwv_aod=1 # for aod plot
    iwv_rrs=0 # for rrs plot
    criteria = (30, 30, 2.0)
    nv_max = 90
elif(product=='spexone_fastmapol'):
    outputfile_header='spexone_fastmapol_'

    dict1 = {'aod_min':[0.2,aod_min_default], \
         'aod_min_plot':[0.2, aod_min_plot_default],\
          'npixel_min':[100*4, npixel_min_default]}
    
    iwvv=[290, 170, 60] #l1c
    iv=2 #0 degree
    iwvvp=[39, 25, 9] #668.4302, 548.3369, 437.2723, 
    ivp=iv
    
    iwv550=21 #550
    iwv_aod=21 #550
    iwv_rrs=5 #440
    criteria = (140, 140, 2.0)
    nv_max = 170
elif(product=='spexone_remotap'):
    outputfile_header='spexone_remotap_'
    dict1 = {'aod_min':[0.2,aod_min_default], \
         'aod_min_plot':[0.2, aod_min_plot_default],\
          'npixel_min':[100*4, npixel_min_default]}

    iwvv=[290, 170, 60] #l1c
    iv=2 #0 degree
    iwvvp=[39, 25, 9]
    ivp=iv
    
    iwv550=7 #550
    iwv_aod=7 #550
    iwv_rrs=3 #440
    criteria = (None, None, 5.0)
    nv_max = 170

print("dict1:", dict1)
aod_min, aod_min_plot, npixel_min = set_default_values(dict1)
print("aod_min, aod_min_plot, npixel_min", aod_min, aod_min_plot, npixel_min)

####DO NOT SHARE the KEYS###########
appkey = open(os.path.join(key_path,'earthdata_appkey.txt')).read().strip()
api_key = open(os.path.join(key_path, 'chatgsfc_api_key.txt')).read().strip()

flag_rm = not args.no_rm  # True by default, False if --no_rm is specified
flag_earthdata_cloud = not args.no_cloud  # True by default, False if --no_cloud is specified
flag_plot_filter = args.plot_filter
print("flag_plot_filter:", flag_plot_filter)

if(flag_earthdata_cloud):
    auth = earthaccess.login(persist=True)

rcParams['font.family'] = 'serif' 
rcParams['font.size'] = '12' 

if timestamp:
    day1 = timestamp
else:
    day1 = tspan[0]+'_'+tspan[1]

try:
    #refined
    print("search refined data")
    short_name=product_info_refined["short_name"]
    sensor_id=product_info_refined["sensor_id"]
    dtid=product_info_refined["dtid"]
    sensor =product_info_refined["sensor"]
    suite1 =product_info_refined["suite1"]
    suite2 = product_info_refined["suite2"]
    filelist_name=sensor+'_'+suite2+'_'+day1+'_filelist.txt'

    data_path, l1c_path, plot_path, html_path = setup_data(tspan, sensor=sensor, suite=suite2)
    if(flag_earthdata_cloud):
        filelist_l2 = download_l2_cloud(tspan, short_name=short_name, output_folder=data_path)
    else:
        filelist_l2 = download_l2_web(tspan_web, appkey, output_folder=data_path,  \
                                      sensor_id=sensor_id, dtid=dtid, filelist_name=filelist_name)
except:
    print("didn't find in refined data")

if(len(filelist_l2)==0):
    try:
        #nrt
        print("search NRT data")
        short_name=product_info_nrt["short_name"]
        sensor_id=product_info_nrt["sensor_id"]
        dtid=product_info_nrt["dtid"]
        sensor =product_info_nrt["sensor"]
        suite1 =product_info_nrt["suite1"]
        suite2 = product_info_nrt["suite2"]
        filelist_name=sensor+'_'+suite2+'_'+day1+'_filelist.txt'
        data_path, l1c_path, plot_path, html_path = setup_data(tspan, sensor=sensor, suite=suite2)
        if(flag_earthdata_cloud):
            filelist_l2 = download_l2_cloud(tspan, short_name=short_name, output_folder=data_path)
        else:
            filelist_l2 = download_l2_web(tspan_web, appkey, output_folder=data_path,\
                                         sensor_id=sensor_id, dtid=dtid, filelist_name=filelist_name)
    except:
        print("didn't find in nrt data neither, quit")
        sys.exit(1)
        
    
print("found:", short_name)

nfile = len(filelist_l2)
    
if nfile == 0:
    print("****no new file downloaded****")
    print("****file may already downloaded")
    #sys.exit(1)
else:
    print(f"****Successfully downloaded {nfile} new files")

try:
    print("check existing folder")
    filelist_l2 = glob.glob(data_path+'/*.nc')
    nfile = len(filelist_l2)
    print("total file before selection in existing folder", nfile)
except:
    print("cannot check existing folder")


filev2 = select_data(filelist_l2, \
                     aod_min=aod_min, npixel_min=npixel_min, \
                     iwv550=iwv550, criteria=criteria)
nfile = len(filev2)
print("total file after selection", nfile)


key1v = ['aot', 'ssa', 'fvf', 'sph']
vmin1v = [0, 0.7, 0, 0]
vmax1v = [1, 1, 1, 1]
cmap1v = ['YlOrRd', 'jet', 'jet', 'jet']

key1v = ['aot', 'ssa', 'fvf', 'sph', 'chi2', 'nv_ref', 'nv_dolp']
vmin1v = [0, 0.7, 0, 0, 0, 0, 0]
vmax1v = [1, 1, 1, 1, 5, 170, 170]
cmap1v = ['YlOrRd', 'jet', 'jet', 'jet', 'jet', 'jet', 'jet']

dict1v= {'aot':[[0, 1],'YlOrRd','linear'] , \
         'ssa':[[0.7, 1], 'jet','linear'], 'fvf':[[0, 1], 'jet','linear'], 'sph':[[0,1], 'jet','linear'], \
         'aot_fine':[[0,1], 'YlOrRd','linear'], 'aot_coarse':[[0,1], 'YlOrRd','linear'], 'angstrom_440_670':[[-1,2], 'jet','linear'], \
         'alh':[[0,6], 'jet','linear'], 'mr':[[1.3,1.65], 'jet','linear'], 'mi':[[0,0.03], 'jet','linear'], \
          'wind_speed': [[0, 10], 'jet','linear'], 'chla':[[-2,1], 'jet','log10'],\
          'Rrs2_mean':[[0,0.02], 'jet','linear'], 'Rrs2_std':[[0,0.02], 'jet','linear'],\
          'chi2':[[0,5], 'jet','linear'], 'nv_ref':[[0,nv_max], 'jet','linear'], \
          'nv_dolp':[[0,nv_max], 'jet','linear'],'quality_flag':[[0,5], 'jet','linear']}

key1v = list(dict1v.keys())
vmin1v = [dict1v[key][0][0] for key in key1v]
vmax1v = [dict1v[key][0][1] for key in key1v]
cmap1v = [dict1v[key][1] for key in key1v]
scale1v = [dict1v[key][2] for key in key1v]

print("key1v =", key1v)
print("vmin1v =", vmin1v)
print("vmax1v =", vmax1v)
print("cmap1v =", cmap1v)
print("scale1v =", scale1v)

#scale1v = np.repeat("linear", len(key1v))
#scale1v[np.array(['chla' in k for k in key1v])] = 'log10'

#only plot selected pixels
#flag_plot_filter=True

#plot everything
#flag_plot_filter=False

##make plots
#infov: timestamp3, boundingbox, center, aerosols
infov, infov_dict = make_plot(filev2, plot_path, l1c_path, \
                              flag_earthdata_cloud=flag_earthdata_cloud, aod_min_plot=aod_min_plot,\
                              sensor=sensor, suite1=suite1,suite2=suite2, \
                              iwvv=iwvv,iv=iv, iwvvp=iwvvp,ivp=ivp,\
                              iwv_aod=iwv_aod, iwv_rrs=iwv_rrs, \
                              key1v=key1v, vmin1v=vmin1v, vmax1v=vmax1v, cmap1v=cmap1v, scale1v=scale1v,\
                             flag_plot_filter=flag_plot_filter)

print(infov_dict)

base_url="https://llm-api-access.caio.mcp.nasa.gov"
message1v, message2v = ask_ai_all(infov_dict, api_key, base_url)
print(message1v)

#text_box = message2v
text_box = None


title1 = day1
global_map1= os.path.join(plot_path,sensor+'_'+suite2+'_'+day1+'_boxes.png')
plot_bounding_box_many(infov, title=title1, fileout=global_map1)

#output_file = html_path+sensor+'_'+suite2+'_'+day1+'_n'+str(nfile)+"_aodmin"+str(aod_min)+"_chat5.html"
output_file = os.path.join(html_path,outputfile_header+day1+'_n'+str(nfile)+"_aod"+str(aod_min)+"_chat5.html")

sequence = [['globe', 'rgb', 'aot', ], ['ssa', 'fvf', 'sph']]
titlev_custom = [["", "", "AOD (550nm)"], ["Single Scattering Albedo (550nm)", 
                                           "Fine Mode Volume Fraction", "Spherical Fraction"]]

sequence = [['globe', 'rgb', 'aot', ], ['ssa', 'fvf', 'sph'], ['chi2', 'nv_ref', 'nv_dolp']]
titlev_custom = [["", "", "AOD (550nm)"], \
                 ["Single Scattering Albedo (550nm)", "Fine Mode Volume Fraction", "Spherical Fraction"],\
                 ["Cost Function (chi2)", "Total Valid Reflectance (nv_ref)", "Total Valid DoLP (nv_dolp)"]]

#'text_box', 'globe', 'rgb'
sequence = [['globe', 'rgb', 'dolp'], \
            ['aot', 'ssa', 'fvf'], \
            ['aot_fine', 'aot_coarse', 'angstrom_440_670'],\
            ['sph','alh', 'mr', 'mi'], \
            ['wind_speed', 'chla','Rrs2_mean', 'Rrs2_std'],\
            ['chi2','nv_ref', 'nv_dolp', 'quality_flag']
            ]

titlev_custom = [["", "Reflectance", "DoLP"], \
                 ["Total AOD (550nm)", "Total SSA (550nm)", "Fine Mode Volume Fraction"],\
                 ['aot_fine', 'aot_coarse', 'angstrom_440_670'],\
                 ["Spherical Fraction", "Aerosol Layer height", "Total refractive index(Real)", "Total refractive index(Imag)"],\
                 ["Wind speed", "Log10(Chla)", "Anguar Mean of Rrs2", "Angular STD of Rrs2"], \
                 ["Cost Function (chi2)", "Total Valid Reflectance (nv_ref)", "Total Valid DoLP (nv_dolp)","Quality Flag"]]


#title = f"{sensor} {suite2} Rapid Data Live View ({tspan[0]})"
title = format_simple_title(sensor, suite2, tspan)
title2 = format_html_info(nfile, criteria, npixel_min, aod_min, aod_min_plot, flag_plot_filter=flag_plot_filter)

image_groups = get_images_from_subfolders(plot_path)
#title2_html=title2_html
hide_after_key = 'fvf'

logo_path = os.path.join(mapol_path, "img", 'orca_logo1.png')
print("====logo location:", logo_path)
if os.path.isfile(logo_path):
    print("====find the logo")
else:
    print("====missing logo")
    logo_path=None
    
create_html_from_subfolders(image_groups, output_file, sequence, global_map=global_map1, \
                            title=title, title2=title2,
                            titlev=titlev_custom, resolution_factor=2, quality=75, \
                            sensor=sensor, suite=suite2,\
                            message1v=message1v, message2v=message2v, \
                            hide_after_key = hide_after_key,
                            infov_dict=infov_dict, text_box=text_box, logo_path=logo_path)

#### copy and clean files
source_file = output_file
#destination_folder = "/mnt/mfs/FILESHARE/meng_gao/rapid_pace/html/"

# Copy the file to the destination folder
destination_path = os.path.join(destination_folder, os.path.basename(source_file))

try:
    shutil.copy(source_file, destination_path)
    print("copy the html file to ", destination_path)
except:
    print("failed copy the html file")


l2_path, l2_file = os.path.split(filelist_l2[0])

    
print("l2_path, l2_file:", l2_path, l2_file)

if(flag_rm):
    pathv = [l1c_path, l2_path]
    for path1 in pathv:
        try:
            shutil.rmtree(path1)  # Recursively remove the folder and its contents
            print(f"✅ Folder removed: {path1}")
        except:
            print("do not exist", path1)
