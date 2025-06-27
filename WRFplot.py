#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 16:25:11 2022

@author: salathe
"""

def WRFplot(
    plotvar,lats,lons,  
    vmin,vmax, 
    maptitle,varname, 
    ColMap, 
    smflg=1, 
    domain='auto', 
    map_limits=[0,0,0,0],
    subplot=[1,1,1]):
    
    from matplotlib.pyplot import colorbar, axes, pcolormesh, colorbar, title

    import numpy as np
    import matplotlib.pyplot as plt

    # Add this to get cartopy from ~salathe:
    # import sys
    # sys.path.insert(0, "/home/disk/margaret/salathe/.local/lib/python3.7/site-packages/cartopy")

    from matplotlib.cm import get_cmap
    import cartopy
    import cartopy.crs as crs
    import os

 #   cartopy.config['pre_existing_data_dir'] = '/mmfs1/gscratch/uwb/salathe/cartopy-data/'

    from cartopy.feature import NaturalEarthFeature
    
    # Set the cartopy mapping object for the WRF domain
    #  (Taken from wrf getcartopy and cartopy_xlim)
    cart_proj = cartopy.crs.LambertConformal(
            central_longitude=-121.0, 
            central_latitude=45.665584564208984, 
            false_easting=0.0, 
            false_northing=0.0, 
            standard_parallels=[30.,60.], 
            globe=None, 
            cutoff=-30)

    fig = plt.gcf()
    ax = fig.add_subplot(subplot[0],subplot[1],subplot[2], projection=cart_proj)

    # Set map limits based on domain (ideally use lat-lon and transform...)
    data_crs = cartopy.crs.PlateCarree()  # because lat/lon are in PlateCarree

    if domain=='pnw02':
        ax.set_xlim([-875806.9669240027, 1056192.549175313])
        ax.set_ylim([-733768.6404772081, 730230.3670079684])
    elif domain=='pnw01':
        ax.set_xlim([-3.7e6, 1.6e6])
        ax.set_ylim([-2.15e6, 2.3e6])
    elif domain=='west02':
        ax.set_xlim([-8.8e5, 1.2e6])
        ax.set_ylim([-1.58e6, 7.3e5])
    elif domain=='custom':
        ax.set_extent(map_limits, crs=data_crs)

    # Use field min/max if -999
    if vmin==-999: vmin=plotvar.min()
    if vmax==-999: vmax=plotvar.max()        
    
    # Color in the data on the map with smoothing

    if smflg == 1:
        smooth = 'gouraud'
    else:
        smooth = 'nearest'
        
    pcolormesh(lons,lats,
                   plotvar,vmin=vmin,vmax=vmax,
                   transform=crs.PlateCarree(),
                   shading=smooth,
                   cmap=get_cmap(ColMap)
                   )
    
    # Add a color bar
    cbar=colorbar(ax=ax, shrink=.6)#, orientation='horizontal')
    cbar.set_label(varname)


    # plt.contour(lons,lats,plotvar, vmin=vmin,vmax=vmax, colors='gray', linewidths=0.5, transform=crs.PlateCarree())


    # Download and add the states and coastlines
    states = NaturalEarthFeature(category='cultural', scale='50m',
                             facecolor='none',
                             name='admin_1_states_provinces_lines')
    ax.add_feature(states, linewidth=.25, edgecolor='grey')
    borders = NaturalEarthFeature(category='cultural', scale='50m',
                             facecolor='none',
                             name='admin_0_boundary_lines_land')
    ax.add_feature(borders, linewidth=.25, edgecolor='grey')
    ax.coastlines('50m', linewidth=0.25)
    

    
    # Add gridlines
    #ax.gridlines(color='black', linestyle='dotted')
    
    # Add a title
    title(maptitle)
