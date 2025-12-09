"""
Setup the function calls
Meng Gao, Sep 25, 2025

Need specify proper directories
Note that earthaccess download, use a defult folder of ./data
"""

import earthaccess
import requests

import os
import glob
import numpy as np
import xarray as xr

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from pathlib import Path
from matplotlib import rcParams

from tools.orca_html_all import *
from tools.orca_plot_map import *
from tools.orca_download import *
from tools.orca_tool import *

import os
import requests
import subprocess


    
def set_default_values(dict1):
    """
    Handles user-provided value vs. default value.
    dict1 entries are: [provided_value, default_value]

    If default_value is not None → use default_value  
    Otherwise                  → use provided_value
    """

    # Unpack provided values and defaults
    aod_min, aod_min_default = dict1['aod_min']
    aod_min_plot, aod_min_plot_default = dict1['aod_min_plot']
    npixel_min, npixel_min_default = dict1['npixel_min']

    # AOD minimum (event detection)
    if aod_min_default is not None:
        aod_min = aod_min_default
    else:
        aod_min = aod_min   # use provided value

    # AOD minimum for plotting
    if aod_min_plot_default is not None:
        aod_min_plot = aod_min_plot_default
    else:
        aod_min_plot = aod_min_plot

    # Pixel minimum threshold
    if npixel_min_default is not None:
        npixel_min = npixel_min_default
    else:
        npixel_min = npixel_min

    return aod_min, aod_min_plot, npixel_min

def setup_data(tspan, sensor='PACE_HARP2', suite='MAPOL_OCEAN.V3.0', path1='./pace_tmp/'):
    """
    setup folders, and download l2 data
    tspan: time range
    """
    day1 = tspan[0]+'_'+tspan[1]
    ## cannot change, default for download tool
    l2_path = os.path.join(path1,'data_l2',sensor+'_'+suite+'_'+day1)
    os.makedirs(l2_path, exist_ok=True)

    l1c_path = os.path.join(path1,'data_l1c',sensor+'_'+suite+'_'+day1)
    os.makedirs(l1c_path, exist_ok=True)

    plot_path = os.path.join(path1,'plot',sensor+'_'+suite+'_'+day1)
    os.makedirs(plot_path, exist_ok=True)

    html_path = os.path.join(path1,'html')
    os.makedirs(html_path, exist_ok=True)

    print(l2_path, l1c_path, plot_path, html_path)
    
    return l2_path, l1c_path, plot_path, html_path

def select_data(filelist_l2, aod_min = 0.3, npixel_min = 100*100, iwv550=1, criteria = (30, 20, 2.0)):
    """
    select data based on aod_min and min npixel
    """
    filev2 =[]
    for i1 in range(len(filelist_l2)):
        file1 = filelist_l2[i1]
        #print(file1)
    
        npixel_valid0, npixel_valid1,filter1 = filter_data(file1, iwv550=iwv550, aot_min = aod_min, criteria =criteria)
        print('=====non-nan, filtered:', npixel_valid0, npixel_valid1)
        if npixel_valid1 >=npixel_min:
            print(file1)
            filev2.append(file1)
            print(' *** found: non-nan, filtered:', npixel_valid0, npixel_valid1)
    return filev2

def create_dict_by_timestamp(infov):
    """
    Convert a list of dictionaries into a single dictionary with timestamps as keys.

    Args:
        infov (list): List of dictionaries containing aerosol data.

    Returns:
        dict: Dictionary where keys are timestamps and values are corresponding entries.
    """
    return {entry['timestamp']: entry for entry in infov}
    
def make_plot(filev2, plot_path, l1c_path="./data/", \
              flag_earthdata_cloud=True,\
              sensor="PACE_HARP2", suite1="L1C",suite2="L2",\
              iv=[40, 5, 85], iwvv=0, ivp=None, iwvvp=None,\
              iwv_aod=1, iwv_rrs=0,\
              aod_min_plot=None, criteria = (30, 20, 2.0),\
              key1v = ['aot', 'ssa', 'fvf', 'sph'], 
              vmin1v = [0, 0.7, 0, 0],
              vmax1v = [1, 1, 1, 1],
              cmap1v = ['YlOrRd', 'jet', 'jet', 'jet'],
              scale1v = ['linear', 'linear', 'linear', 'linear'],
              flag_plot_filter=False
             ):
    """generate plots according to filev2

    after data selection, we will only plot the data within aod_min_plot, and criteria, 
    aerosol statistics are also computed within this range to ensure quality
    aod will be plot over all available range. 
    """
    
    os.makedirs(plot_path, exist_ok=True)
    os.makedirs(l1c_path, exist_ok=True)

    infov = []
    for file1 in filev2[:]:
        #try:
        info = plot_l1c_l2(file1, plot_path, iwvv=iwvv,iv=iv, iwvvp=iwvvp,ivp=ivp, iwv_aod=iwv_aod, iwv_rrs=iwv_rrs,\
                l1c_path=l1c_path, flag_earthdata_cloud=flag_earthdata_cloud, aod_min_plot=aod_min_plot,\
                sensor=sensor, suite1=suite1, suite2=suite2, criteria=criteria,\
                key1v=key1v, vmin1v=vmin1v, vmax1v=vmax1v, cmap1v=cmap1v,scale1v=scale1v,\
                           flag_plot_filter=flag_plot_filter)
        infov.append(info)
        #except:
        #    print('failed to make plot', file1)
    #create a dictionary
    infov_dict = create_dict_by_timestamp(infov)
    return infov, infov_dict

def create_rules_table_html(rules_selection, rules_plot):
    """
    Generate an HTML table showing granule selection rules and plot rules.

    Parameters:
    - rules_selection: dict of {variable: threshold} for granule selection
    - rules_plot: dict of {variable: threshold} for data plotting

    Returns:
    - HTML string
    """
    html = "<table style='border-collapse: collapse; width: 80%;'>\n"
    html += "<tr style='background-color:#f2f2f2;'>"
    html += "<th style='border:1px solid #ccc; padding:8px;'>Variable</th>"
    html += "<th style='border:1px solid #ccc; padding:8px;'>Selection</th>"
    html += "<th style='border:1px solid #ccc; padding:8px;'>Plot</th>"
    html += "</tr>\n"

    # Get the union of variables
    variables = set(rules_selection.keys()).union(set(rules_plot.keys()))

    for var in variables:
        sel_value = rules_selection.get(var, "-")
        plot_value = rules_plot.get(var, "-")
        html += "<tr>"
        html += f"<td style='border:1px solid #ccc; padding:8px;'>{var}</td>"
        html += f"<td style='border:1px solid #ccc; padding:8px;'>{sel_value}</td>"
        html += f"<td style='border:1px solid #ccc; padding:8px;'>{plot_value}</td>"
        html += "</tr>\n"

    html += "</table>\n"
    
    return html