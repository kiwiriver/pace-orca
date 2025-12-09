
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

from tools.orca_html import *
from tools.orca_plot import *
from tools.orca_download import *
from tools.orca_utility import *

import requests
import subprocess

def format_html_info(nfile, criteria, npixel_min, aod_min, aod_min_plot, flag_plot_filter=True):
    """
    <h3 style="color: #0066cc; margin-bottom: 15px;">PACE Polarimetric Data Analysis Summary</h3>
    """
    # Common sections that appear in both cases
    nv_ref_min, nv_dolp_min, chi2_max = criteria
    
    common_header = f"""
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 10px 0; font-family: Arial, sans-serif;">
        
        
        <div style="background-color: white; padding: 15px; border-radius: 6px; margin-bottom: 15px;">
            <h4 style="color: #333; margin-bottom: 10px;">Data selection summary</h4>
            <p><strong>Total Granules Found:</strong> {nfile}</p>
            
            <!-- Collapsible Data Selection Criteria and Visualization Strategy -->
            <div style="margin: 10px 0;">
                <button id="criteriaToggle" onclick="toggleDataCriteria()" 
                        style="background: #0066cc; color: white; border: none; padding: 8px 16px; 
                               border-radius: 4px; cursor: pointer; font-size: 14px; margin-bottom: 10px;
                               transition: background-color 0.3s ease;">
                    📊 Show Data Selection Criteria & Visualization Strategy
                </button>
                
                <div id="dataCriteria" style="display: none; background-color: #f8f9fa; 
                                              padding: 15px; border-radius: 4px; border-left: 4px solid #0066cc;
                                              transition: all 0.3s ease; overflow: hidden;">
                    <p><strong>Valid Pixel Threshold:</strong> >{npixel_min} pixels per granule</p>
                    
                    <h5 style="color: #555; margin: 10px 0 5px 0;">Quality Control Criteria:</h5>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>Aerosol Optical Depth (550nm): >{aod_min}</li>
                        <li>Number of valid reflectance angles: ≥{nv_ref_min}</li>
                        <li>Number of valid DoLP angles: ≥{nv_dolp_min}</li>
                        <li>Chi-squared Goodness of Fit: <{chi2_max}</li>
                    </ul>
                    
                    <h5 style="color: #555; margin: 15px 0 5px 0;">Visualization Strategy:</h5>"""
    
    # Variable section based on filter flag - now part of the collapsible content
    if flag_plot_filter:
        visualization_section = f"""
                    <p><strong>All plots:</strong> AOD, Chi², number of valid reflectance and DolP angles include all available pixels</p>
                    <p><strong>Filtered plots:</strong> Other variables display only pixels where AOD(550nm) >{aod_min_plot}</p>
                </div>
            </div>"""
    else:
        visualization_section = """
                    <p><strong>Visualization:</strong> All plots include data from all available pixels meeting the quality control criteria.</p>
                </div>
            </div>"""
    
    # Updated common footer with the JavaScript function
    common_footer = """
        </div>
        
        <div style="background-color: #e8f4f8; padding: 15px; border-radius: 6px; margin-bottom: 15px;">
            <h4 style="color: #0066cc; margin-bottom: 10px;">About PACE Polarimetric Data</h4>
            <p><strong>Data Version:</strong> This analysis utilizes <strong>PACE FastMAPOL (NASA) and RemoTAP (SRON) Level-2 provisional data (Version 3.0, Provisional) </strong>.</p>                  
            <p><strong>Data Usage:</strong> This page is made by PACE FastMAPOL team for preliminary data visulization and discoveries. Please contact Meng Gao (meng.gao@nasa.gov) for further questions. </p> 
        </div>
        
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 6px; border-left: 4px solid #ffc107;">
            <h4 style="color: #856404; margin-bottom: 10px;"> Disclaimers</h4>
            <p><strong> Known Data Limitations:</strong> Users should exercise caution when interpreting aerosol optical and microphysical properties, as these products are still under active validation and may contain systematic bias and uncertainties. </p>
            <p><strong> Aerosol Event AI Descriptions:</strong> Atmospheric event interpretations are generated using ChatGSFC API portal provided by the NASA GSFC CAIO (Chief AI Office). These AI-generated descriptions are intended for preliminary assessment and should be verified with additional meteorological and satellite observations.</p>
        </div>
    </div>
    
    <script>
    function toggleDataCriteria() {
        var criteria = document.getElementById('dataCriteria');
        var toggleButton = document.getElementById('criteriaToggle');
        
        if (criteria.style.display === 'none' || criteria.style.display === '') {
            criteria.style.display = 'block';
            toggleButton.innerHTML = '📊 Hide Data Selection Criteria & Visualization Strategy';
            toggleButton.style.backgroundColor = '#dc3545';
        } else {
            criteria.style.display = 'none';
            toggleButton.innerHTML = '📊 Show Data Selection Criteria & Visualization Strategy';
            toggleButton.style.backgroundColor = '#0066cc';
        }
    }
    
    // Add hover effects
    document.addEventListener('DOMContentLoaded', function() {
        var button = document.getElementById('criteriaToggle');
        if (button) {
            button.addEventListener('mouseenter', function() {
                this.style.opacity = '0.9';
            });
            button.addEventListener('mouseleave', function() {
                this.style.opacity = '1';
            });
        }
    });
    </script>"""
    
    # Combine all sections
    title2 = common_header + visualization_section + common_footer
    return title2

def format_simple_title(sensor, suite2, tspan):
    """Simple improved title formatting"""
    date_str = tspan[0] if tspan else "Unknown Date"
    
    # Format the product name nicely
    #product_name = f"{sensor} {suite2}".replace('_', ' ').replace('.', ' ')
    product_name = f"{sensor}; {suite2}"

    formatted_title = f"""
        <h1 style="margin: 0; font-size: 2em; color: #333; font-weight: 500;">
            PACE Polarimetric L2 Data View ({product_name})
        </h1>
        <p style="margin: 10px 0 0 0; font-size: 1.1em; color: #666; font-weight: 400;">
            {date_str}
        </p>
    """
    return formatted_title