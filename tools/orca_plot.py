"""
Define function to make plot of l1 and l2 data

Meng Gao, Sep 25, 2025

If sensors other than HARP2 is used, need check file name and RGB index.
A list of keys are used to specify the variables to be plotted. 

To do:
1. bounding box are not accurate, need get real polygon.
2. may need to get chi2, nv_ref, nv_dolp maps
3. check ocean properties too, chla, rrs etc

"""

import os
import glob
import pickle
import numpy as np
import xarray as xr
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.util import add_cyclic_point

from tools.orca_download import *
from tools.orca_utility import *
from tools.orca_data import extract_timestamp, filter_data

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
    
def plot_l1c_l2(file1, plot_path, \
                l1c_path="./data/", iv=[40, 5, 85], ivp=None, iwvv=0, iwvvp=None, iwv_aod=1,iwv_rrs=0,\
                flag_earthdata_cloud=True, \
                key1v = ['aot', 'ssa', 'fvf', 'sph'], 
                vmin1v = [0, 0.7, 0, 0],
                vmax1v = [1, 1, 1, 1],
                cmap1v = ['YlOrRd', 'jet', 'jet', 'jet'],
                scale1v = ['linear', 'linear', 'linear', 'linear'],
                aod_min_plot = None,
                sensor="PACE_HARP2",suite1="L1C",suite2="L2",
                criteria = (30, 20, 2.0),
                flag_plot_filter=False
                ):
    """
    file1: L2 data file
    plot_path: where is the images
    iv: harp2 rgb angles
    lc_folder: where to save
    
    key1v: define a list of data to be plotted

    aod_min_plot: used to screen out data except aod

    Note:
    spexone: rgb: iwvv=[30, 21, 6], iv=2
    spexone: l1c: iwvv=[290, 170, 60], iv=2
    harp2 rgb at nadir: iwvv=0, iv=[40, 5, 85], iangle=0

    iwv_rrs: for the plot of rrs, usually choose 440
    iwv_aod: for all others, and use to select data, usually 440

    if scale=log10, will plot in log10 scale
    flag_plot_filter: true, plot filtered data, false: plot all
    info are still based on filtered information for targeted event
    
    """
    ########## get l2 data ########################
    print(file1)

    info={}
    info['aod_min']=aod_min_plot

    #timestamp3 = file1.split(sensor+".")[1].split(split)[0]
    timestamp3 = extract_timestamp(file1)
    info['timestamp']=timestamp3
    
    print(timestamp3)
    
    datatree = xr.open_datatree(file1)
    dataset2 = xr.merge(datatree.to_dict().values())

    ########### get l1 data #######################
    if(flag_earthdata_cloud):
        #
        filelist_l1c = download_l1c_cloud(file1, l1c_path, sensor=sensor, suite=suite1)
    else:
        #sensor="PACE_HARP2", split=".L2",suite1="L1C.V3.5km"
        filelist_l1c = download_l1c_web(file1, l1c_path, sensor=sensor, suite=suite1)
    
    file4 = filelist_l1c[0]
    print(file4)
    datatree = xr.open_datatree(file4)
    dataset1 = xr.merge(datatree.to_dict().values())
    #############################

    #get lat, lon, and radiance
    lon2=dataset1['longitude'].values
    lat2=dataset1['latitude'].values

    if (iv is not None) and (iwvv is not None):
        tmp2i = dataset1.i[:, :, iv, iwvv].values
    else:
        tmp2i = np.full_like(lon2, None, dtype=object)
    
    if (ivp is not None) and (iwvvp is not None):
        tmp2dolp = dataset1.dolp[:, :, ivp, iwvvp].values
    else:
        tmp2dolp = np.full_like(lon2, None, dtype=object)
    
    #set output path
    plot_path2 = plot_path+'/'+timestamp3+'/'
    os.makedirs(plot_path2, exist_ok=True)
    print(plot_path2)

    #plot bounding box
    fileout= plot_path2+'pace_harp2'+'_'+timestamp3+'_globe.png'
    print(fileout)
    boundingbox, center = plot_bounding_box_one(lat2, lon2, timestamp3, fileout=fileout)
    
    info['boundingbox'] = boundingbox
    info['center'] = center

    #with open("tmp2i.pk", "wb") as f:
    #    pickle.dump([lat2, lon2, tmp2i], f)
    
    #plot l1 rgb
    title = f"{sensor} {suite2}+@{timestamp3}"
    fileout= plot_path2+sensor+suite2+'_'+timestamp3+'_rgb.png'
    print(fileout)
    plot_rgb(lon2, lat2, tmp2i, None, figsize = (10, 5),\
            title=title, fileout=fileout,)

    #plot l1 rgb in dolp
    title = f"{sensor} {suite2}+@{timestamp3}"
    fileout= plot_path2+sensor+suite2+'_'+timestamp3+'_dolp.png'
    print(fileout)
    
    plot_rgb(lon2, lat2, tmp2dolp, None, flag_dolp=True, figsize = (10, 5),\
            title=title, fileout=fileout,)

    #plot l2 data
    #file1: l2 data file, aod_min_plot for data selection

    
    npixel_valid0, npixel_valid1,filter1 = filter_data(file1, iwv550=iwv_aod, aot_min=aod_min_plot, criteria=criteria)

    
    for i1, key1 in enumerate(key1v):
        try:
            if('rrs' in key1.lower()):
                iwv_plot=iwv_rrs
            else:
                iwv_plot=iwv_aod
    
            try:
                tmp3 = dataset2[key1].values[:,:, iwv_plot]
            except:
                tmp3 = dataset2[key1].values[:,:]
    
            if(scale1v[i1]=='log10'):
                #plot in log scale
                tmp3=np.log10(tmp3)
            
            ##only for aerosol statistics
            if(aod_min_plot):
                #check all the data including aot
                tmp4 = np.where(filter1, tmp3, np.nan).copy()
    
                if(key1=='aot'):
                    #add total number of valid pixels in
                    info['pixel']= np.sum(~np.isnan(tmp4))
                    
                #includ the information in info   
                info[key1]=[np.nanmean(tmp4),np.nanstd(tmp4)]
    
            #title = 'PACE HARP2 FastMAPOL L2 @'+ timestamp3
            #cbar_label = key1
            title = key1 + ' (mean:{:0.2f}, std:{:0.2f} for aot>{:0.2f})'.format(\
                info[key1][0],info[key1][1],aod_min_plot) + '@'+ timestamp3
            
            ##only for data plot, tmp3 is used not tmp4
            if(flag_plot_filter):
                #when on, plot variables satisfy the filter rule, otherwise plot all
                if(aod_min_plot and (key1 not in ['aot', 'chi2', 'nv_ref', 'nv_dolp'])):
                #    #if aod_min is valid, screen data, except for aod itself
                    tmp3 = np.where(filter1, tmp3, np.nan)
                    print("****filter out data not within criteria, aod_min_plot:", aod_min_plot)
            else:
                print("****plot all pixels****")
    
            cbar_label = None
            fileout= plot_path2+sensor+suite2+'_'+timestamp3+'_'+key1+'.png'
            print(fileout)
    
            #since chi2, nv, may have different range for harp2 and spexone, redefine them here
            if('harp2' in sensor.lower()):
                if(key1=='chi2'):
                    vmin2, vmax2=0, 3
                elif(key1=='nv_ref'):
                    vmin2, vmax2=0, 90
                elif(key1=='nv_dolp'):
                    vmin2, vmax2=0, 90
                else:
                    vmin2, vmax2 = vmin1v[i1], vmax1v[i1]
            
            if('spexone' in sensor.lower()):
                if(key1=='chi2'):
                    vmin2, vmax2=0, 3
                elif(key1=='nv_ref'):
                    vmin2, vmax2=0, 170
                elif(key1=='nv_dolp'):
                    vmin2, vmax2=0, 170
                else:
                    vmin2, vmax2 = vmin1v[i1], vmax1v[i1]
                
            plot_rgb(lon2, lat2, tmp2i, tmp3, figsize = (10, 5), \
                     vmin1=vmin2, vmax1=vmax2 , cmap=cmap1v[i1], \
                     title=title, fileout=fileout, cbar_label=cbar_label)
        except:
            print(key1, 'not available')
        
    #timestamp3, boundingbox, center
    return info
        
def plot_l2_product(lat, lon, data, plot_range, label, title, vmin, vmax, figsize=(12, 4), cmap="viridis"):
    """Make map and histogram (default)."""

    # Create a figure with two subplots: 1 for map, 1 for histogram
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(1, 2, width_ratios=[3, 1], wspace=0.3)

    # Map subplot
    ax_map = fig.add_subplot(gs[0], projection=ccrs.PlateCarree())
    ax_map.set_extent(plot_range, crs=ccrs.PlateCarree())
    ax_map.coastlines(resolution="110m", color="black", linewidth=0.8)
    ax_map.gridlines(draw_labels=True)

    # Assume lon and lat are defined globally or passed in
    pm = ax_map.pcolormesh(
        lon, lat, data, vmin=vmin, vmax=vmax, transform=ccrs.PlateCarree(), cmap=cmap
    )
    plt.colorbar(pm, ax=ax_map, orientation="vertical", pad=0.1, label=label)
    ax_map.set_title(title, fontsize=12)

    # Histogram subplot
    ax_hist = fig.add_subplot(gs[1])
    flattened_data = data[~np.isnan(data)]  # Remove NaNs for histogram
    valid_count = np.sum(~np.isnan(flattened_data))
    ax_hist.hist(
        flattened_data, bins=40, color="gray", range=[vmin, vmax], edgecolor="black"
    )
    ax_hist.set_xlabel(label)
    ax_hist.set_ylabel("Count")
    ax_hist.set_title("Histogram: N=" + str(valid_count))

    # plt.tight_layout()
    plt.show()

def reset_data_for_rgb(tmp2, scale1=1/250, scale2=0.5, bias=-0.1):
    tmp2 = (tmp2*scale1)**scale2
    tmp2=tmp2+bias
    tmp2[tmp2<0]=0.0
    tmp2[tmp2>0.99] = 0.99
    return tmp2

def reset_lon(i, tmp2, lon2):
    """resolve the issue when lon cross dateline
    i=0: lon<0
    i=1: lon>0
    """
    if(i==0):
        tmp2t = tmp2.copy()
        #print(tmp2t.shape, lon2.shape)
        #lon2t = lon2.copy()
        tmp2t[lon2<-179]=np.nan
        tmp2t[lon2>0]=np.nan
        tmp2t=np.ma.masked_where(np.isnan(tmp2t),tmp2t)
    else:
        tmp2t = tmp2.copy()
        #lon2t = lon2.copy()
        #lon2t[lon2<0]=np.nan
        tmp2t[lon2<0]=np.nan
        tmp2t[lon2>179]=np.nan
        tmp2t=np.ma.masked_where(np.isnan(tmp2t),tmp2t)
    return tmp2t

            
def plot_rgb(lon2, lat2, tmp2, tmp3, flag_dolp=False, figsize = (10, 5), \
            vmin1=0, vmax1=1.0, cmap='YlOrRd', title=None, fileout=None, \
             cbar_label=None, cbar_label_fontsize=14):
    """
    extent: for the map
    vmin1, vmax1: color bar range
    cmap: color style
    """

    extent, proj, flag_crossdateline = plot_crossdateline_extent(lon2, lat2)

    fig = plt.figure(figsize=figsize)
    ax = plt.axes(projection=proj)
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    
    ################################
    ### plot rgb ###################
    if(not flag_dolp):
        tmp2 = reset_data_for_rgb(tmp2)
    else:
        tmp2 = reset_data_for_rgb(tmp2, scale1=2, scale2=0.5, bias=0)

    plot_crossdateline_rgb(ax, lon2, lat2, tmp2)
    #plt.pcolormesh(lon2, lat2, tmp2,transform=ccrs.PlateCarree())

    ################################
    #### plot variable #############

    # Determine if longitudes cross the dateline
    #fixed cross dateline issue: from Kehrli, Matthew
    #flag_crossdateline = (ds['longitude'].max() - ds['longitude'].min()) > 180    
    #if flag_crossdateline:
    #    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)})
    #else:
    #    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    
    try:
        levels = np.linspace(vmin1, vmax1,21)
        ticks = np.linspace(vmin1, vmax1, 6)
        tick_labels = ["{:0.2f}".format(t1) for t1 in ticks]

        plot_crossdateline_scalar(ax, lon2, lat2, tmp3, cmap=cmap, levels=levels,\
                               ticks=ticks, tick_labels=tick_labels, \
                               cbar_label=cbar_label, cbar_label_fontsize=cbar_label_fontsize)
    except:
        pass
    
    ########################
    xbin=5
    ybin=5
    alpha=0.3
    
    gl=ax.gridlines(linewidth=0.5, color='gray', alpha=0.3, linestyle='-')
    cl=ax.coastlines(resolution='50m', color='k', linewidth=0.1) #10m, 110m
    ax.add_feature(cartopy.feature.OCEAN, edgecolor='w',linewidth=0.01)
    ax.add_feature(cartopy.feature.LAND, edgecolor='w',linewidth=0.01)
    gl.top_labels = False #True
    gl.bottom_labels = True
    gl.left_labels = True
    gl.right_labels = False
    gl.xlocator = mticker.FixedLocator(np.arange(-180,180,xbin))
    gl.ylocator = mticker.FixedLocator(np.arange(-90,90,ybin))
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    ax.set_xlabel(r"Longitude($^\circ$)")
    ax.set_ylabel(r"Latitude($^\circ$)")
    plt.tight_layout()
    plt.title(title)

    if(fileout):
        plt.savefig(fileout, dpi=400, bbox_inches='tight', pad_inches=0.1)
    #plt.show()

def plot_crossdateline_extent(lon2, lat2):
    """
    Compute map extent that handles dateline-crossing correctly.

    Parameters
    ----------
    lon2, lat2 : 2D numpy arrays
        Longitude and latitude grids.

    Returns
    -------
    extent : list
        [lon_min, lon_max, lat_min, lat_max]
    projection : ccrs.Projection
        Recommended Cartopy projection.
    flag_crossdateline : bool
        Whether data crosses the dateline.
    """
    lon_flat = lon2.flatten()  # More explicit than concatenate
    lat_flat = lat2.flatten()
    lon_min, lon_max = lon_flat.min(), lon_flat.max()
    lat_min, lat_max = lat_flat.min(), lat_flat.max()

    flag_crossdateline = (lon_max - lon_min) > 180

    if flag_crossdateline:
        print("*************cross dateline detected")
        # Convert longitudes to [-180, 180] range for proper extent calculation
        lon_wrapped = np.where(lon_flat > 180, lon_flat - 360, lon_flat)
        extent = [lon_wrapped.min(), lon_wrapped.max(), lat_min, lat_max]
        projection = ccrs.PlateCarree(central_longitude=180)
    else:
        extent = [lon_min, lon_max, lat_min, lat_max]
        projection = ccrs.PlateCarree()

    return extent, projection, flag_crossdateline

def plot_crossdateline_rgb(ax, lon2, lat2, rgb_array):
    """
    Plot RGB(A) image data that may cross the dateline using Cartopy.
    Works even if longitude coordinates are not equally spaced.

    Parameters
    ----------
    ax : cartopy.mpl.geoaxes.GeoAxesSubplot
        Axis to plot on.
    lon2, lat2 : 2D numpy arrays
        Longitude and latitude grids.
    rgb_array : 3D numpy array (ny, nx, 3 or 4)
        RGB(A) image to plot.
    """
    if lon2.shape != lat2.shape:
        raise ValueError("lon2 and lat2 must have the same shape")
    if rgb_array.shape[:2] != lon2.shape:
        raise ValueError("RGB array first two dimensions must match lon2/lat2")

    ny, nx = lon2.shape
    lon1d = lon2[0, :]
    crosses = (lon1d.max() - lon1d.min()) > 180

    if crosses:
        print("***** Dateline crossing detected (RGB, manual wrap) *****")
        
        # --- Normalize longitudes into [-180, 180] range
        lon2_wrapped = np.where(lon2 > 180, lon2 - 360, lon2)
        
        # --- Plot both halves of the data separately ---
        for i in range(2):
            # Create a copy of the RGB array for this half
            rgb_part = rgb_array.copy()
            
            # Apply the same masking logic as in reset_lon (only to RGB data)
            if i == 0:  # Western hemisphere (lon < 0)
                # Mask out eastern hemisphere and extreme western edge
                rgb_part[lon2_wrapped > 0] = np.nan
                rgb_part[lon2_wrapped < -179] = np.nan
            else:  # Eastern hemisphere (lon > 0)
                # Mask out western hemisphere and extreme eastern edge
                rgb_part[lon2_wrapped < 0] = np.nan
                rgb_part[lon2_wrapped > 179] = np.nan
            
            # Create masked array for RGB only (following your pattern)
            rgb_masked = np.ma.masked_where(np.isnan(rgb_part), rgb_part)
            
            # Plot this hemisphere - lon and lat remain unchanged
            ax.pcolormesh(lon2_wrapped, lat2, rgb_masked, 
                          transform=ccrs.PlateCarree())
            
            print(f"  - Plotting hemisphere {i} ({'WEST' if i == 0 else 'EAST'})")
    else:
        # --- Simple case (no crossing)
        extent = [lon2.min(), lon2.max(), lat2.min(), lat2.max()]
        ax.pcolormesh(lon2, lat2, rgb_array,
                transform=ccrs.PlateCarree()
            )

def plot_crossdateline_scalar(ax, lon2, lat2, data, cmap='viridis', levels=None,
                              ticks=None, tick_labels=None,
                              cbar_label=None, cbar_label_fontsize=None):
    """
    Plot 2D scalar data (e.g., AOD, SST, etc.) that may cross the dateline using Cartopy.
    Works even if longitude coordinates are not equally spaced.

    Parameters
    ----------
    ax : cartopy.mpl.geoaxes.GeoAxesSubplot
        Axis to plot on.
    lon2, lat2 : 2D numpy arrays
        Longitude and latitude grids.
    data : 2D numpy array
        Data to plot.
    """
    if lon2.shape != lat2.shape or lon2.shape != data.shape:
        raise ValueError("lon2, lat2, and data must have the same shape")

    # Set color range
    if levels is not None:
        vmin1, vmax1 = levels[0], levels[-1]
    else:
        vmin1, vmax1 = np.nanmin(data), np.nanmax(data)

    # Detect dateline crossing
    lon1d = lon2[0, :]
    crosses = (lon1d.max() - lon1d.min()) > 180

    if crosses:
        print("***** Dateline crossing detected (scalar, manual wrap) *****")

        # Normalize longitudes into [-180, 180]
        lon2_wrapped = np.where(lon2 > 180, lon2 - 360, lon2)

        # Split east/west sides
        east_mask = lon2_wrapped >= 0
        west_mask = lon2_wrapped < 0

        lat_min, lat_max = np.nanmin(lat2), np.nanmax(lat2)

        # Plot east side
        if np.any(east_mask):
            lon_east = np.where(east_mask, lon2_wrapped, np.nan)
            lat_east = np.where(east_mask, lat2, np.nan)
            data_east = np.where(east_mask, data, np.nan)
            extent = [np.nanmin(lon_east), np.nanmax(lon_east), lat_min, lat_max]
            mesh_east = ax.pcolormesh(
                lon_east, lat_east, data_east,
                transform=ccrs.PlateCarree(),
                cmap=cmap, vmin=vmin1, vmax=vmax1, shading='auto'
            )

        # Plot west side
        if np.any(west_mask):
            lon_west = np.where(west_mask, lon2_wrapped, np.nan)
            lat_west = np.where(west_mask, lat2, np.nan)
            data_west = np.where(west_mask, data, np.nan)
            extent = [np.nanmin(lon_west), np.nanmax(lon_west), lat_min, lat_max]
            mesh_west = ax.pcolormesh(
                lon_west, lat_west, data_west,
                transform=ccrs.PlateCarree(),
                cmap=cmap, vmin=vmin1, vmax=vmax1, shading='auto'
            )

        # Keep one handle for colorbar
        mesh = mesh_east if np.any(east_mask) else mesh_west

    else:
        # Normal case (no crossing)
        mesh = ax.pcolormesh(
            lon2, lat2, data,
            transform=ccrs.PlateCarree(),
            cmap=cmap, shading='auto'
        )
        mesh.set_clim(vmin1, vmax1)

    # Optional colorbar
    if ticks is not None:
        cbar = plt.colorbar(mesh, ax=ax, shrink=0.8, pad=0.02)
        cbar.set_ticks(ticks)
        if tick_labels is not None:
            cbar.set_ticklabels(tick_labels)
        if cbar_label:
            cbar.ax.xaxis.set_label_position('top')
            cbar.ax.set_xlabel(cbar_label, labelpad=10, fontsize=cbar_label_fontsize)

    return mesh


def plot_crossdateline_data(ax, lon2, lat2, tmp3, cmap='viridis', levels=None, \
                            ticks=None, tick_labels=None, cbar_label=None, cbar_label_fontsize=None):
    """
    Plot both rgb and scalar, not handeling crossdateline well, 
    2D data that may cross the dateline using Cartopy.

    Parameters
    ----------
    ax : cartopy.mpl.geoaxes.GeoAxesSubplot
        Axis to plot on.
    lon2, lat2 : 2D numpy arrays
        Longitude and latitude grids.
    tmp3 : 2D numpy array
        Data to plot.
    cmap : str
        Matplotlib colormap name.
    levels : list or tuple, optional
        Contour levels or (vmin, vmax) bounds for color scale.
    """
    flag_crossdateline = (lon2.max() - lon2.min()) > 180

    # Set color scale
    if levels is not None:
        vmin1, vmax1 = levels[0], levels[-1]
    else:
        vmin1, vmax1 = None, None

    if flag_crossdateline:
        print("*************cross dateline")
        mesh = ax.pcolormesh(
            lon2, lat2, tmp3,
            transform=ccrs.PlateCarree(central_longitude=180),
            cmap=cmap, vmin=vmin1, vmax=vmax1
        )
    else:
        mesh = ax.pcolormesh(
            lon2, lat2, tmp3,
            transform=ccrs.PlateCarree(),
            cmap=cmap, vmin=vmin1, vmax=vmax1
        )
        
    if(ticks):
        cbar=plt.colorbar(shrink=0.8, pad=0.02) #shrink=0.9, pad=0.1 
        cbar.set_ticks(ticks)
        cbar.set_ticklabels(tick_labels)
        cbar.ax.xaxis.set_label_position('top')  # Position the label on the top
        cbar.ax.set_xlabel(cbar_label, labelpad=10, fontsize=cbar_label_fontsize)  # Customize label
        
    return mesh


def add_bounding_box_text(ax, lon1, lat1, timestamp1=None, transform1=ccrs.Geodetic()):
    """Plot the timestamp text on the map."""
    if timestamp1:
        ax.text(
            lon1, lat1, f"{timestamp1}",
            transform=transform1, fontsize=10, color="blue",
            ha="center", va="center",
            bbox=dict(facecolor="white", edgecolor="blue", alpha=0.5),
            rotation=10
        )

def plot_crossdateline_boundingbox(ax, lons, lats, timestamp1=None,
                                   transform1=ccrs.Geodetic(), color='red', linewidth=2):
    """
    Plot a rectangular bounding box that may cross the dateline.
    """
    # Detect dateline crossing
    flag_crossdateline = (max(lons) - min(lons)) > 180

    if flag_crossdateline:
        print("*************cross dateline")

        # Wrap longitudes into range [-180, 180]
        lons_wrapped = np.array(lons, dtype=float)
        lons_wrapped[lons_wrapped > 180] -= 360
        lons_wrapped[lons_wrapped < -180] += 360

        # Split into two segments if large longitude jump exists
        split_idx = np.where(np.abs(np.diff(lons_wrapped)) > 180)[0]
        if len(split_idx) > 0:
            i_split = split_idx[0] + 1

            # First segment
            ax.plot(lons_wrapped[:i_split], lats[:i_split],
                    transform=transform1, color=color, linewidth=linewidth)
            lon1, lat1 = np.min(lons_wrapped[:i_split]), np.min(lats[:i_split])-1
            add_bounding_box_text(ax, lon1, lat1, timestamp1=timestamp1, transform1=transform1)

            # Second segment
            ax.plot(lons_wrapped[i_split:], lats[i_split:],
                    transform=transform1, color=color, linewidth=linewidth)
            lon2, lat2 = np.min(lons_wrapped[i_split:]), np.min(lats[i_split:])
            add_bounding_box_text(ax, lon2, lat2, timestamp1=timestamp1, transform1=transform1)
        else:
            # If no split, just plot normally
            ax.plot(lons_wrapped, lats,
                    transform=transform1, color=color, linewidth=linewidth)
            lon1, lat1 = np.min(lons_wrapped), np.min(lats)-1
            add_bounding_box_text(ax, lon1, lat1, timestamp1=timestamp1, transform1=transform1)
    else:
        # Normal (non-dateline-crossing) bounding box
        ax.plot(lons, lats, transform=transform1,
                color=color, linewidth=linewidth)
        lon1, lat1 = np.min(lons), np.min(lats)-1
        add_bounding_box_text(ax, lon1, lat1, timestamp1=timestamp1, transform1=transform1)

def plot_bounding_box_one(lat, lon, timestamp1, xbin=15, ybin=15, title=None, fileout=None):
    """
    Plot a bounding box on a global map with a text annotation displaying the timestamp.
    """
    # Step 1: Extract bounding box coordinates
    min_lat, max_lat = np.min(lat), np.max(lat)
    min_lon, max_lon = np.min(lon), np.max(lon)
    
    # Step 2: Calculate the central latitude and longitude for the bounding box
    central_lat = (min_lat + max_lat) / 2
    central_lon = (min_lon + max_lon) / 2
    center = [central_lat, central_lon]
    print(f"Central Latitude: {central_lat}, Central Longitude: {central_lon}")
    
    # Step 3: Set up the Orthographic projection centered on the bounding box
    proj = ccrs.Orthographic(central_longitude=central_lon, central_latitude=central_lat)
    fig, ax = plt.subplots(figsize=(10, 5), subplot_kw={'projection': proj})
    ax.set_global()
    
    # Add map features
    ax.add_feature(cartopy.feature.OCEAN, edgecolor='w', linewidth=0.01)
    ax.add_feature(cartopy.feature.LAND, edgecolor='w', linewidth=0.01)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
    
    # Step 4: Plot the bounding box as a polygon
    lons = [lon[0,0], lon[0,-1], lon[-1,-1], lon[-1,0], lon[0,0]]
    lats = [lat[0,0], lat[0,-1], lat[-1,-1], lat[-1,0], lat[0,0]]

    boundingbox = [lats, lons]
    print(f"boundingbox: lats: {lats}, lons: {lons}")
    
    plot_crossdateline_boundingbox(ax, lons, lats, timestamp1=timestamp1)
    
    # Add gridlines for reference
    gridlines = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    gridlines.top_labels = False
    gridlines.right_labels = False
    gridlines.left_labels = False
    gridlines.bottom_labels = False
    gridlines.xlocator = mticker.FixedLocator(np.arange(-180, 180, xbin))
    gridlines.ylocator = mticker.FixedLocator(np.arange(-90, 90, ybin))
    
    # Add title
    if title:
        plt.title(title, fontsize=14)

    # Save to file if fileout is provided
    if fileout:
        plt.savefig(fileout, dpi=300, bbox_inches='tight', pad_inches=0.1)
        print(f"✅ Plot saved to {fileout}")
        
    return boundingbox, center

def plot_bounding_box_many(infov, title=None, fileout=None):
    """
    Plot bounding boxes with text labels for timestamps on a global map.
    """
    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_global()

    ax.add_feature(cartopy.feature.OCEAN, edgecolor='w', linewidth=0.01)
    ax.add_feature(cartopy.feature.LAND, edgecolor='w', linewidth=0.01)
    ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

    for info in infov:
        try:
            timestamp1 = info["timestamp"]
            bbox_lats, bbox_lons = info["boundingbox"]
            center_lat, center_lon = info["center"]
    
            plot_crossdateline_boundingbox(ax, bbox_lons, bbox_lats, timestamp1=timestamp1)

        except Exception as e:
            print("❌ Failed to generate bounding box:", info)
            print("Error:", e)

    if title:
        plt.title(title, fontsize=14)

    if fileout:
        plt.savefig(fileout, dpi=300, bbox_inches="tight", pad_inches=0.1)
        print(f"✅ Plot saved to {fileout}")
