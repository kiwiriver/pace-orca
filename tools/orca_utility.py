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
import re
import requests
import subprocess
import numpy as np
import xarray as xr

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from pathlib import Path
from matplotlib import rcParams

#from tools.orca_html import *
#from tools.orca_plot import *
#from tools.orca_download import *

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