import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
import cartopy
import warnings
import cartopy.crs as crs
from WRFplotSUB import WRFplot
import WRF_wind as Wwnd
from pathlib import Path

#models = ['mri-cgcm3', 'access1.0', 'access1.3', 'canesm2', 'miroc5']
model = "mri-cgcm3" # ['mri-cgcm3', 'access1.0', 'access1.3', 'canesm2', 'miroc5']

# Set geographic range from ERA5 PNW
lat1, lat2 = 40,49.5  # Southern and northern bounds
lon1, lon2 = -124.8,-116.3  # Western and eastern bounds

# file paths for importing data and saving figures
data_path = 'Data/'
figure_path = 'Graphics/'

# Import data as xarray
hist_path = f'{data_path}1970wrf850UVT{model}.nc'

ds_hist = Wwnd.get_wrf850UVT(hist_path, mask_range=[lon1-1,lon2+1,lat1-1,lat2+1])

wind_dir_array = np.array([[0,90],[90,180],[180,270],[270,360]])
wind_dir_labels = ['NE', 'SE', 'SW', 'NW']

stuff = input("average temperature or amount of winds (temp/winds) ")
while stuff not in ["temp", "winds"]:
    print("pick a valid choice")
    stuff = input("average temperature or amount of winds (temp/winds) ")

heat_filter = input("heatwave filter? (y/n) ")
while heat_filter not in ["y","n"]:
    print("pick a valid choice")
    heat_filter = input("heatwave filter? (y/n) ")

if heat_filter == "n":
    T2quad_hist = Wwnd.avg_from_wind(ds_hist, wind_dir_array, wind_dir_labels, WindMin=1,
                                     stat=50) if stuff == "temp" else Wwnd.count_wind_days(ds_hist, wind_dir_array,
                                                                                           wind_dir_labels, WindMin=1)
else:
    T2quad_hist = Wwnd.avg_from_wind(ds_hist, wind_dir_array, wind_dir_labels, WindMin=1,
                                     stat=50, hw_filt=True) if stuff == "temp" else Wwnd.count_wind_days(ds_hist,
                                                                                                         wind_dir_array,
                                                                                                         wind_dir_labels,
                                                                                                         WindMin=1,
                                                                                                         hw_filt=True)

lats = T2quad_hist['XLAT']
lons = T2quad_hist['XLONG']



label = 'NE'
title_suffix = '1970'



subplt=[2,4,3,1] # note the order of the subplots is left-right top-bottom



cart_proj = crs.LambertConformal(
        central_longitude=-121.0,
        central_latitude=45.665584564208984,
        false_easting=0.0,
        false_northing=0.0,
        standard_parallels=[30., 60.],
        globe=None,
        cutoff=-30)
fig, axs = plt.subplots(2, 2, subplot_kw={'projection': cart_proj})

maximum = max([T2quad_hist['wind_days_' + label].max() for label in wind_dir_labels]) if stuff=="winds" else 0

for idr, label in enumerate(wind_dir_labels):
    data = T2quad_hist['T2_' + label] - T2quad_hist['T2_all'] if stuff == "temp" else T2quad_hist['wind_days_' + label]
    #T2quad_hist = T2quad_hist.fillna(0)
    min = -6 if stuff == "temp" else 0
    max = -min if stuff == "temp" else maximum

    row,column = (subplt[idr]-1)//2,(subplt[idr]-1)%2

    #print(f"Has NaN: {np.isnan(data).any()}")
    #print(f"Number of NaN values: {np.isnan(data).sum()}")

    """
    All of the supported map colors (try out some they may make things easier to see)

     'Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r',
     'CMRmap', 'CMRmap_r', 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Grays', 'Grays_r', 'Greens', 'Greens_r', 'Greys', 
     'Greys_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 
     'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 
     'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn',
     'RdYlGn_r', 'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia', 
     'Wistia_r', 'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r', 
     'autumn', 'autumn_r', 'berlin', 'berlin_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r', 
     'cividis', 'cividis_r', 'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 'cubehelix', 'cubehelix_r', 
     'flag', 'flag_r', 'gist_earth', 'gist_earth_r', 'gist_gray', 'gist_gray_r', 'gist_grey', 'gist_grey_r', 'gist_heat', 
     'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow', 'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 
     'gist_yarg_r', 'gist_yerg', 'gist_yerg_r', 'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 'gray', 'gray_r', 'grey', 
     'grey_r', 'hot', 'hot_r', 'hsv', 'hsv_r', 'inferno', 'inferno_r', 'jet', 'jet_r', 'magma', 'magma_r', 'managua', 
     'managua_r', 'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 
     'prism_r', 'rainbow', 'rainbow_r', 'seismic', 'seismic_r', 'spring', 'spring_r', 'summer', 'summer_r', 'tab10', 
     'tab10_r', 'tab20', 'tab20_r', 'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r', 'terrain', 'terrain_r', 'turbo', 'turbo_r', 
     'twilight', 'twilight_r', 'twilight_shifted', 'twilight_shifted_r', 'vanimo', 'vanimo_r', 'viridis', 'viridis_r', 
     'winter', 'winter_r'
    """

    WRFplot(
        axs[row, column],
        data,
        lats, lons,
        min, max,
        f'T2 {title_suffix} {label}', '°C'if stuff=="temp"else"Wind Amount", 'RdYlBu_r', #"grey_r"
        domain='custom', map_limits=[lon1, lon2, lat1, lat2],
        smflg=0
    )


#plt.show()
folder = Path(f"WindSpeedGraphs/{stuff}") # You can change this to a specific path
folder.mkdir(parents=True, exist_ok=True)

filename = f"WindSpeedGraphs/{stuff}/hw_filt_{heat_filter}.png"
plt.tight_layout()
plt.savefig(filename, dpi=300, bbox_inches='tight')
#plt.show() uncomment for the graph to pop up
plt.close()

