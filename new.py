import xarray as xr
from WRFplot import WRFplot
import matplotlib.pyplot as plt
from pathlib import Path # pathlib should be built in

"""
This code will create a new "Graphs" folder with a folder per model and one for the average among all models
Each model will have 3 folders per model dealing with historical or future data and the difference between them
Each time folder will have all the quadrants

The code may take a minute or 2 due to the code getting a plot for all the cases 
"""

# Average will always be last
models = ['mri-cgcm3', 'access1.0', 'access1.3', 'canesm2', 'miroc5',"AVERAGE"]


# Set geographic range for the map
lat1, lat2 = 40,49.5  # Southern and northern bounds
lon1, lon2 = -124.8,-116.3  # Western and eastern bounds

# Temperature anomaly limits
max = 6  # deg-C
min = -max  # Symetrical colorscale

average = dict() # Storage for the data across models

for model in models:
    # read in the data
    if model != "AVERAGE":
        T2quad_hist = xr.open_dataset(f'Data/T2quad_hist_{model}.nc')
        T2quad_fut = xr.open_dataset(f'Data/T2quad_fut_{model}.nc')
        lats,lons = T2quad_hist["XLAT"],T2quad_hist["XLONG"] # all the lats and lons are the same right


    for quadrant in ["NE","SE","SW","NW"]:
        # Data
        if model != "AVERAGE":
            datas = {"hist": T2quad_hist['T2_' + quadrant] - T2quad_hist['T2_all'],
                     "fut": T2quad_fut['T2_' + quadrant] - T2quad_fut['T2_all'],
                     "diff": (T2quad_fut['T2_' + quadrant] - T2quad_fut['T2_all']) -
                             (T2quad_hist['T2_' + quadrant] - T2quad_hist['T2_all'])
            }

        for time_frame in ["hist","fut","diff"]:
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
            WRFplot(
                data,
                lats, lons,
                min,max,
                f'T2 anomaly {quadrant} {model}', '°C', 'RdYlBu_r',
                domain='custom', map_limits=[lon1, lon2, lat1, lat2], # specify the map limits
                smflg=0, # Smooth the data
                subplot=(1, 1, 1), # Position of the subplot in the figure
            )

            # Creates new folders for data
            folder = Path(f"Graphs/{model}/{time_frame}") # You can change this to a specific path
            folder.mkdir(parents=True, exist_ok=True)

            # Saves data to folders
            filename = f"Graphs/{model}/{time_frame}/{quadrant}.png"
            plt.tight_layout()
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()

    print(f'Saved graphs to {model}')

print()
print("Finished running")






