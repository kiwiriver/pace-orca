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
mapol_path = os.environ.get('MAPOLTOOL_LAB_PATH') or '/mnt/mfs/mgao1/analysis/github/pace-orca/'
sys.path.append(mapol_path)

from tools.orca_html import *
from tools.orca_header import *
from tools.orca_plot import *
from tools.orca_utility import *
from tools.orca_download import *
from tools.orca_ai import *
from tools.orca_pace import *
from tools.orca_plot_setup import load_dict1v

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
parser.add_argument("--header", type=str, help="any string", default='v3.0')
parser.add_argument("--l2str", type=str, help="any string to identify the l2 files", default='L2')
parser.add_argument("--aod_min_default", type=float, default=None, \
                    help="set aod_min, if not set, use existing values")
parser.add_argument("--aod_min_plot_default", type=float, default=None, \
                    help="set aod_min_plot, if not set, use existing values")
parser.add_argument("--aod_max_plot_default", type=float, default=1.0, \
                    help="set aod_max, if not set, use existing values")
parser.add_argument("--npixel_min_default", type=float, default=None, \
                    help="set npixel_min, if not set, use existing values")
parser.add_argument("--destination_folder", type=str, default="/mnt/mfs/FILESHARE/meng_gao/rapid_pace/html/",\
                    help="where to save the html")
parser.add_argument("--no_rm", action="store_true",
                       help="Do NOT remove files after finish (default: remove files)")
parser.add_argument("--do_not_ask_ai", action="store_true",
                       help="no ai if on")
parser.add_argument("--no_cloud", action="store_true",
                       help="Do NOT use Earthdata cloud (default: use cloud)")
parser.add_argument("--plot_filter", action="store_true",
                       help="default plot everything, when specified plot filtered values")
parser.add_argument("--input_data_path", type=str, default=None,\
                    help="if the data is already downloaded")


args = parser.parse_args()

product = args.product
header = args.header
l2str = args.l2str

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
input_data_path = args.input_data_path
os.makedirs(destination_folder, exist_ok=True)

print("product=", product)
#load correct information for that product
#default v3 ocean
#L2.MAPOL_OCEAN.V3.0, L2.MAPOL_LAND.V4_0

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

#old v3 data example, new data l2 version v4_0
#outputfile_header, product_info_nrt, product_info_refined = get_pace_data_info(product, l1c_version='v3', l2_version='v3.0', surface='ocean'):


print("outputfile_header, product_info_nrt, product_info_refined:", outputfile_header, product_info_nrt, product_info_refined)


if(product=='harp2_fastmapol'):
    outputfile_header='harp2_fastmapol_'
    
    dict1 = {'aod_min':[0.3,aod_min_default], \
         'aod_min_plot':[0.3, aod_min_plot_default],\
          'npixel_min':[100*40, npixel_min_default]}
    
    #100*100 early version
    #100*20 may be too less

    #nadir rgb
    #ivv=[[40, 5, 85]]
    #ivvp=ivv
    #ilabelv=[0]

    #more angles
    ivv=[[58, 8, 88],
        [48, 6, 86],
        [39, 4, 85],
        [31, 3, 83],
        [21, 1, 82]]
    ivvp=ivv
    ilabelv=[-40,-20,0,20,40]
    
    iwvv=0
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

    #need to update to include more angles
    ivv=[2] #0 degree
    ivvp=ivv
    ilabelv=[0]

    iwvv=[290, 170, 60] #l1c
    iwvvp=[39, 25, 9] #668.4302, 548.3369, 437.2723, 
    
    
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

    #need to update to include more angles
    ivv=2 #0 degree
    ivvp=ivv
    ilabelv=[0]
    
    iwvv=[290, 170, 60] #l1c
    iwvvp=[39, 25, 9]
    
    
    iwv550=7 #550
    iwv_aod=7 #550
    iwv_rrs=3 #440
    criteria = (None, None, 5.0)
    nv_max = 170

outputfile_header = outputfile_header + header+'_'

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

flag_ask_ai = not args.do_not_ask_ai
print("ask ai:", flag_ask_ai)

if(flag_earthdata_cloud):
    auth = earthaccess.login(persist=True)

rcParams['font.family'] = 'serif' 
rcParams['font.size'] = '12' 

if timestamp:
    day1 = timestamp
else:
    day1 = tspan[0]+'_'+tspan[1]

#given path is not there
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
    #PACE_HARP2_L2.MAPOL_OCEAN.
    data_path, l1c_path, plot_path, html_path = setup_data(tspan, sensor=sensor, suite=suite2, header=header)
    print("****where data is", data_path)
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
        data_path, l1c_path, plot_path, html_path = setup_data(tspan, sensor=sensor, suite=suite2, header=header)
        print("****where data is", data_path)
        
        if(flag_earthdata_cloud):
            filelist_l2 = download_l2_cloud(tspan, short_name=short_name, output_folder=data_path)
        else:
            filelist_l2 = download_l2_web(tspan_web, appkey, output_folder=data_path,\
                                         sensor_id=sensor_id, dtid=dtid, filelist_name=filelist_name)
    except:
        print("didn't find in nrt data neither, quit")
        sys.exit(1)
        
    
print("found:", short_name)

#if a path is given
if(input_data_path!=None and input_data_path.lower()!='none'):
    data_path = input_data_path
    print("input_data_path:", input_data_path)
    print("overwrite data_path by input_data_path")
else:
    print("use default data path:", data_path)

print("data_path, if data need download:", data_path)
print("input_data_path, if data is already available:", input_data_path)

nfile = len(filelist_l2)
    
if nfile == 0:
    print("****no new file downloaded****")
    print("****file may already downloaded")
    #sys.exit(1)
else:
    print(f"****Successfully downloaded {nfile} new files")

print("path to check:", data_path+f'/*{l2str}*.nc')

try:
    print("check existing folder")
    filelist_l2 = glob.glob(data_path+f'/*{l2str}*.nc')
    nfile = len(filelist_l2)
    print(f"*****list all the l2 files in {data_path} using {l2str} *****")
    print(filelist_l2)
    print("total file before selection in existing folder", nfile)
except:
    print("cannot check existing folder")


filev2 = select_data(filelist_l2, \
                     aod_min=aod_min, npixel_min=npixel_min, \
                     iwv550=iwv550, criteria=criteria)
nfile = len(filev2)
print("total file after selection", nfile)

###########################################################################
#variables to plot:

#'text_box', 'globe', 'rgb'
sequence = [['globe', 'rgb0',  'rp0', 'dolp0'], \
            ['aot', 'ssa', 'fvf'], \
            ['aot_fine', 'aot_coarse', 'angstrom_440_670'],\
            ['sph', 'sph_fine', 'sph_coarse'],\
            ['alh', 'aerosol_lidar_ratio', 'aerosol_depol_ratio'], \
            ['mr', 'mr_fine', 'mr_coarse', 'mi', 'mi_fine', 'mi_coarse'], \
            ['reff_fine', 'reff_coarse', 'veff_fine', 'veff_coarse'], \
            ['wind_speed', 'chla'],\
            ['Rrs1_mean', 'Rrs2_mean', 'Rrs1_std', 'Rrs2_std'],\
            ['Rrs_angular_mean', 'Rrs_nadir_mean', 'Rrs_angular_std', 'Rrs_nadir_std'],\
            ['rhos_angular_mean', 'rhos_nadir_mean', 'rhos_angular_std', 'rhos_nadir_std'],\
            ['chi2','nv_ref','nv_rho', 'nv_dolp', 'quality_flag', 'timing'],\
            ['ozone','surface_pressure', 'height'],\
            ['land_fiso', 'land_kvol', 'land_kgeo', 'land_fvol', 'land_fgeo', 'land_bpol', 'land_white_sky_albedo'],\
            ['rgb_Rrs_angular_mean', 'rgb_Rrs_nadir_mean', 'rgb_Rrs_angular_std', 'rgb_Rrs_nadir_std'],\
            ['rgb_rhos_angular_mean', 'rgb_rhos_nadir_mean', 'rgb_rhos_angular_std', 'rgb_rhos_nadir_std'],\
            ['rgb-40','rgb-20','rgb0','rgb20','rgb40'],\
            ['rp-40','rp-20','rp0','rp20','rp40'],\
            ['dolp-40','dolp-20','dolp0','dolp20','dolp40'],
            ]

titlev_custom = [["", "Reflectance",  "Rp", "DoLP"], \
                 ["Total AOD (550nm)", "Total SSA (550nm)", "Fine Mode Volume Fraction"],\
                 ['AOD (fine)', 'AOD (coarse)', 'Angstrom(440/670)'],\
                 ["Total Spherical Fraction", "Fine Spherical Fraction", "Coarse Spherical Fraction"], \
                  ["Aerosol Layer height",'Aerosol lidar ratio', 'Aerosol depol ratio'],\
                 ["Total refractive index(Real)", "Fine refractive index(Real)", "Coarse refractive index(Real)", "Total refractive index(Imag)", "Fine refractive index(Imag)", "Coarse refractive index(Imag)"],\
                 ['reff_fine', 'reff_coarse', 'veff_fine', 'veff_coarse'], \
                 ["Wind speed", "Log10(Chla)"], \
                 ["Anguar Mean of Rrs_angular", "Anguar Mean of Rrs_nadir", "Angular STD of Rrs_angular", "Angular STD of Rrs_nadir"], \
                 ["Anguar Mean of Rrs_angular", "Anguar Mean of Rrs_nadir", "Angular STD of Rrs_angular", "Angular STD of Rrs_nadir"], \
                 ["Anguar Mean of rhos_angular", "Anguar Mean of rhos_nadir", "Angular STD of rhos_angular", "Angular STD of rhos_nadir"], \
                 ["Cost Function (chi2)", "Total Valid Reflectance (nv_ref)", "Total Valid Reflectance (nv_rho)", "Total Valid DoLP (nv_dolp)","Quality Flag", "Timing"],\
                 ["Ozone", "Surface Pressure", "Terrain Height (m)"],\
                ['land_fiso', 'land_kvol', 'land_kgeo', 'land_fvol', 'land_fgeo', 'land_bpol', 'land_white_sky_albedo'],\
                ['rgb_Rrs_angular_mean', 'rgb_Rrs_nadir_mean', 'rgb_Rrs_angular_std', 'rgb_Rrs_nadir_std'],\
                ['rgb_rhos_angular_mean', 'rgb_rhos_nadir_mean', 'rgb_rhos_angular_std', 'rgb_rhos_nadir_std'],\
                ['rgb-40','rgb-20','rgb0','rgb20','rgb40'],\
                ['rp-40','rp-20','rp0','rp20','rp40'],\
                ['dolp-40','dolp-20','dolp0','dolp20','dolp40'],
                ]

sequence = [['globe', 'rgb0',  'rp0', 'dolp0'], \
            ['aot', 'ssa', 'fvf'], \
            ['rgb-40','rgb-20','rgb0','rgb20','rgb40'],\
            ['rp-40','rp-20','rp0','rp20','rp40'],\
            ['dolp-40','dolp-20','dolp0','dolp20','dolp40'],
            ]
titlev_custom = [["", "Reflectance",  "Rp", "DoLP"], \
                ["Total AOD (550nm)", "Total SSA (550nm)", "Fine Mode Volume Fraction"],\
                ['rgb-40','rgb-20','rgb0','rgb20','rgb40'],\
                ['rp-40','rp-20','rp0','rp20','rp40'],\
                ['dolp-40','dolp-20','dolp0','dolp20','dolp40'],
                ]

##########################################################################
aot_max = args.aod_max_plot_default #default 1.0

dict1v = load_dict1v(aot_max=aot_max, nv_max=nv_max)

#only keep the keys already defined in sequence
sequence_keys = {
    key
    for row in sequence
    for key in row
}

dict1v = {
    key: value
    for key, value in dict1v.items()
    if key in sequence_keys
}

#still keep Rrs1 and Rrs2 and ref, for old files

key1v = list(dict1v.keys())
print("l2 keys to plot", key1v)
vmin1v = [dict1v[key][0][0] for key in key1v]
vmax1v = [dict1v[key][0][1] for key in key1v]
cmap1v = [dict1v[key][1] for key in key1v]
scale1v = [dict1v[key][2] for key in key1v]
extend1v = [dict1v[key][3] for key in key1v]

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

##########################################################################


##make plots
#infov: timestamp3, boundingbox, center, aerosols
infov, infov_dict = make_plot(filev2, plot_path, l1c_path=l1c_path, figsize=(8,8),\
                              flag_earthdata_cloud=flag_earthdata_cloud,\
                              aod_min_plot=aod_min_plot,\
                              sensor=sensor, suite1=suite1,suite2=suite2, \
                              ivv=ivv, ivvp=ivvp, ilabelv=ilabelv,\
                              iwvv=iwvv,iwvvp=iwvvp,\
                              iwv_aod=iwv_aod, iwv_rrs=iwv_rrs, \
                              key1v=key1v, vmin1v=vmin1v, vmax1v=vmax1v,\
                              cmap1v=cmap1v, scale1v=scale1v, extend1v=extend1v,\
                             flag_plot_filter=flag_plot_filter)

print(infov_dict)

if(flag_ask_ai):
    base_url="https://llm-api-access.caio.mcp.nasa.gov"
    message1v, message2v = ask_ai_all(infov_dict, api_key, base_url)
    print(message1v)
else:
    message1v=None
    message2v=None

#text_box = message2v
text_box = None


title1 = day1
global_map1= os.path.join(plot_path,sensor+'_'+suite2+'_'+day1+'_boxes.png')
plot_bounding_box_many(infov, title=title1, fileout=global_map1)

#output_file = html_path+sensor+'_'+suite2+'_'+day1+'_n'+str(nfile)+"_aodmin"+str(aod_min)+"_chat5.html"
output_file = os.path.join(html_path,outputfile_header+day1+'_n'+str(nfile)+"_aod"+str(aod_min)+"_chat5.html")




#title = f"{sensor} {suite2} Rapid Data Live View ({tspan[0]})"
title = format_simple_title(sensor, suite2, tspan)
title2 = format_html_info(nfile, criteria, npixel_min, aod_min, aod_min_plot, flag_plot_filter=flag_plot_filter)

image_groups = get_images_from_subfolders(plot_path)
#title2_html=title2_html
hide_after_key = 'fvf'

logo_path = os.path.join(mapol_path, "logo", 'orca_logo_v1.png')
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
