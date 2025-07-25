import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as crs
from WRFplotSUB import WRFplot
from pathlib import Path

cart_proj = crs.LambertConformal(
        central_longitude=-121.0,
        central_latitude=45.665584564208984,
        false_easting=0.0,
        false_northing=0.0,
        standard_parallels=[30., 60.],
        globe=None,
        cutoff=-30)

# Average will always be last
models = ['mri-cgcm3', 'access1.0', 'access1.3', 'canesm2', 'miroc5',"AVERAGE"]


# Set geographic range for the map
lat1, lat2 = 40,49.5  # Southern and northern bounds
lon1, lon2 = -124.8,-116.3  # Western and eastern bounds

# Temperature anomaly limits
max = 6  # deg-C
min = -max  # Symetrical colorscale

average = dict() # Storage for the data across models



for time_frame in ["hist","fut","diff"]:


    for quadrant in ["NW", "NE", "SW", "SE"]:
        fig, axs = plt.subplots(3, 2, subplot_kw={'projection': cart_proj})
        for i in range(len(models)):
            model = models[i]

            # read in the data
            if model != "AVERAGE":
                T2quad_hist = xr.open_dataset(f'Data/T2quad_hist_{model}.nc')
                T2quad_fut = xr.open_dataset(f'Data/T2quad_fut_{model}.nc')
                lats, lons = T2quad_hist["XLAT"], T2quad_hist["XLONG"]  # all the lats and lons are the same right

            # Data
            if model != "AVERAGE":
                datas = {"hist": T2quad_hist['T2_' + quadrant] - T2quad_hist['T2_all'],
                         "fut": T2quad_fut['T2_' + quadrant] - T2quad_fut['T2_all'],
                         "diff": (T2quad_fut['T2_' + quadrant] - T2quad_fut['T2_all']) -
                                 (T2quad_hist['T2_' + quadrant] - T2quad_hist['T2_all'])
                         }


            # Gets the correct data
            name = f"{time_frame}_{quadrant}"
            if model != "AVERAGE":
                data = datas[time_frame]

                # Puts the data into average
                if name in average:
                    average[name] += data
                else:
                    average[name] = data
            else:
                # Average data
                data = average[name] / (len(models) - 1)

            # Creates the plot
            row,column = i//2, i%2

            WRFplot(
                axs[row,column],
                data,
                lats, lons,
                min, max,
                f'{model}', '°C', 'RdYlBu_r',
                domain='custom', map_limits=[lon1, lon2, lat1, lat2],  # specify the map limits
                smflg=0  # Smooth the data
                )
            plt.tight_layout()
            #fig.subplots_adjust(wspace=0.3, hspace=0.2)
            #plt.show()
            #"""
            # Creates new folders for data
            folder = Path(f"Graphs2/{quadrant}")  # You can change this to a specific path
            folder.mkdir(parents=True, exist_ok=True)

        # Saves data to folders
        filename = f"Graphs2/{quadrant}/{time_frame}.png"
        plt.suptitle(f"T2 anomaly {quadrant}",x=0.625)
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        #"""







