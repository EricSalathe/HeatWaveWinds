"""
WRF_wind.py

This module provides functions for processing WRF (Weather Research and Forecasting) model output data,
specifically for analyzing surface temperature (T2) in relation to wind direction and speed.

Functions:
    - avg_from_wind(ds, wind_dir, wind_label, WindMin=0, stat='mean'):
        Computes average or percentile T2 values for specified wind direction ranges and minimum wind speed thresholds.
    - get_wrf850UVT(path, mask_range=[-999,0,0,0]):
        Loads WRF output data from a NetCDF file and optionally applies a spatial mask based on latitude and longitude.

Dependencies:
    - numpy
    - xarray
    - warnings

Intended for use in ensemble and heatwave analysis of WRF model outputs.
"""


def avg_from_wind(ds, wind_dir, wind_label, WindMin=0, stat='mean', field='T2', hw_filt=False):
    import numpy as np
    import xarray as xr
    import warnings
    warnings.filterwarnings("ignore", message="All-NaN slice encountered")
    
    """
    Compute average or percentile surface temperature (T2) for specified wind direction ranges and minimum wind speed.

    Parameters:
        ds (xarray.Dataset): Input dataset containing 'U', 'V', and 'T2' variables, with 'datetime' dimension.
        wind_dir (array-like): Array of wind direction limits, shape (N, 2). Each row is [start_deg, end_deg].
                               If start > end, range wraps around 360 degrees.
        wind_label (list of str): List of labels for each wind direction range, used for output variable names.
        WindMin (float, optional): Minimum wind speed threshold. Default is 0 (no threshold).
        stat (str or float, optional): 'mean' for mean T2, or a percentile (0-100) for quantile T2. Default is 'mean'.
        field (str, optional): The field to compute statistics on. Default is 'T2'. If 'WSPD', computes wind speed from 'U' and 'V'.
        hw_filt (bool, optional): Heat Wave Filter. If True, filter out data below the 95th percentile of T2 before computing averages. Default is False.
    Returns:
        xarray.Dataset: Dataset with T2 averaged (or quantiled) over each wind direction range and over all directions.

    Raises:
        ValueError: If 'stat' is not 'mean' or a float between 0 and 100.

    Notes:
        - Wind direction is computed from U and V components.
        - Handles wind direction ranges that wrap around 360 degrees.
        - Filters out data below WindMin threshold if specified.
    """
        

    # Check the selected field exists in the dataset
    if field not in ds:
        if field=='WSPD': 
            # If WSPD is not in the dataset, compute it from U and V
            ds['WSPD'] = np.hypot(ds['U'], ds['V'])
        else:
            raise ValueError(f"Field '{field}' not found in dataset.")

    # Create an output dataset with coordinates
    ds_out = xr.Dataset(
        coords={
           'XLAT': ds.coords['XLAT'],
           'XLONG': ds.coords['XLONG'],
        }
    )
    
    # apply heat wave filter if specified
    if hw_filt: 
        T2_95 = ds['T2'].quantile(0.95, dim='datetime')
        ds = ds.where(ds['T2'] > T2_95, drop=True)

    # Compute mean or percentile for the specified field over all directions
    if stat == 'mean':
        ds_out[field + '_all'] = ds[field].mean(dim='datetime')
    elif isinstance(stat, (int, float)) and stat >= 0 and stat <= 100:
        ds_out[field + '_all'] = ds[field].quantile(stat/100, dim='datetime')
    else:
        raise ValueError("Please set 'stat' to 'mean' or a float percentile between 0 and 100.")

    # get wind direction
    ds = ds.assign(
        wind_dir = (180 + np.degrees(np.arctan2(ds['U'], ds['V']))) % 360,
    )

    # Filter on minimum wind threshold
    if WindMin > 0:
        ds = ds.where(np.hypot(ds['U'], ds['V']) > WindMin)

    # loop over wind direction ranges
    for idr in range(wind_dir.shape[0]):
        # Filter on wind direction (note wrap around)
        wd = ds['wind_dir']
        if wind_dir[idr][0] > wind_dir[idr][1]:
            mask = (wd > wind_dir[idr][0]) | (wd < wind_dir[idr][1])
        else:
            mask = (wd > wind_dir[idr][0]) & (wd < wind_dir[idr][1])

        ds_filtered = ds.where(mask)

        # Compute mean or percentile for the specified field over time
        if stat == 'mean':
            ds_out[field + '_' + wind_label[idr]] = ds_filtered[field].mean(dim='datetime')
        elif isinstance(stat, (int, float)) and stat >= 0 and stat <= 100:
            ds_out[field + '_' + wind_label[idr]] = ds_filtered[field].quantile(stat/100, dim='datetime')
        else:
            raise ValueError("Please set 'stat' to 'mean' or a float percentile between 0 and 100.")

    return ds_out

def get_wrf850UVT(path, mask_range=[-999,0,0,0]):
    """
    Load WRF output data from a NetCDF file and optionally apply a spatial mask.

    Parameters:
        path (str): Path to the NetCDF file containing WRF output.
        mask_range (list, optional): List of [lon1, lon2, lat1, lat2] to define a spatial mask.
                                     If mask_range[0] is -999, no mask is applied.
                                     Default is [-999, 0, 0, 0].
    """
    import xarray as xr

    da = xr.open_dataset(path)

    if mask_range[0] != -999:
        lon1, lon2, lat1, lat2 = mask_range
        mask = (
            (da.XLAT >= lat1) & (da.XLAT <= lat2) &
            (da.XLONG >= lon1) & (da.XLONG <= lon2)
        )
        da = da.where(mask, drop=True)

    return da

