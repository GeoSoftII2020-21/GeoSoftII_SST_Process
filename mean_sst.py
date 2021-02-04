'''Packages'''
import xarray as xr
import math
import numpy as np

'''Exceptions'''

class ParameterTypeError(Exception):
  def __init__(self, message):
    self.message = message

class BboxLengthError(Exception):
  def __init__(self, message):
    self.message = message

class BboxCellsizeError(Exception):
  def __init__(self, message):
    self.message = message

class LongitudeValueError(Exception):
  def __init__(self, message):
    self.message = message

class LatitudeValueError(Exception):
  def __init__(self, message):
    self.message = message

class TimeframeLengthError(Exception):
  def __init__(self, message):
    self.message = message

class TimeframeValueError(Exception):
  def __init__(self, message):
    self.message = message

class DatasetAttributesError(Exception):
  def __init__(self, message):
    self.message = message

'''Functions'''

def createSubset(ds, minLon, minLat, maxLon, maxLat):
  '''
  Creates a spatial subset.

  Parameters:
    ds (dask dataset): dataset from which a subset is generated
    minLon (double): left value
    minLat (double): bottom value
    maxLon (double): right value
    maxLat (double): top value

  Returns:
    ds_subset (dask dataset): spatially limited dataset
  '''
  if (minLon > maxLon):
    ds_subset1 = ds.sel(lon=slice(minLon, ds["lon"].values[-1]), lat=slice(minLat, maxLat))
    ds_subset2 = ds.sel(lon=slice(ds["lon"].values[0], maxLon), lat=slice(minLat, maxLat))
    ds_subset_concat = xr.concat([ds_subset1, ds_subset2], "lon")
    '''update metadata'''
    if hasattr(ds_subset_concat["lon"], 'actual_range'):
    	ds_subset_concat["lon"].actual_range[0] = ds_subset_concat["lon"].values[0]
    	ds_subset_concat["lon"].actual_range[1] = ds_subset_concat["lon"].values[-1]
    if hasattr(ds_subset_concat["lat"], 'actual_range'):
    	ds_subset_concat["lat"].actual_range[0] = ds_subset_concat["lat"].values[0]
    	ds_subset_concat["lat"].actual_range[1] = ds_subset_concat["lat"].values[-1]
    return ds_subset_concat
  else:
    ds_subset = ds.sel(lon=slice(minLon, maxLon), lat=slice(minLat, maxLat))
    '''update metadata'''
    if hasattr(ds_subset["lon"], 'actual_range'):
    	ds_subset["lon"].actual_range[0] = ds_subset["lon"].values[0]
    	ds_subset["lon"].actual_range[1] = ds_subset["lon"].values[-1]
    if hasattr(ds_subset["lat"], 'actual_range'):
        ds_subset["lat"].actual_range[0] = ds_subset["lat"].values[0]
        ds_subset["lat"].actual_range[1] = ds_subset["lat"].values[-1]
    return ds_subset

def wrapper_mean_sst(data, timeframe, bbox = [-999,-999,-999,-999]):
    '''
    Executes function exceptions_mean_sst.

    Parameters:
        data (dask dataset): dataset
        timeframe ([str]): tuple with values for start and end dates, e.g. ['1981-10-01','1981-11-01']
        bbox ([float]): optional, Array with four values: [min Longitude, min Latitude, max Longitude, max Latitude]

    Returns:
        ds (xarray dataset): dataset with mean sea surface temperature
    '''

    ds = exceptions_mean_sst(data, timeframe, bbox)
    return ds

def exceptions_mean_sst(data, timeframe, bbox = [-999,-999,-999,-999]):
    '''
    Passes parameters on to function mean_sst and throws exceptions.

    Parameters:
        data (dask dataset): dataset
        timeframe ([str]): tuple with values for start and end dates, e.g. ['1981-10-01','1981-11-01']
        bbox ([float]): optional, Array with four values: [min Longitude, min Latitude, max Longitude, max Latitude]

    Returns:
        ds (xarray dataset): dataset with mean sea surface temperature
    '''

    '''Checks parameter data'''

    if ('sst' not in data.data_vars
            or 'lon' not in data.dims
            or 'lat' not in data.dims
            or 'time' not in data.dims):
        raise DatasetAttributesError("Parameter data must include dimensions 'lat', 'lon' and 'time' and a data variable named 'sst'.")

    '''Checks parameter bbox'''

    minLon = data["lon"].values[0]
    maxLon = data["lon"].values[-1]
    minLat = data["lat"].values[0]
    maxLat = data["lat"].values[-1]
    lon_cellsize = abs(minLon - data["lon"].values[1])
    lat_cellsize = abs(minLat - data["lat"].values[1])

    if len(bbox) != 4:
        raise BboxLengthError("Parameter bbox is an array with four values: [min Longitude, min Latitude, max Longitude, max Latitude]. Please specify an array with exactly four values.")
    elif (bbox != [-999,-999,-999,-999]):
        if ((type(bbox[0]) != int and type(bbox[0]) != float)
                or (type(bbox[1]) != int and type(bbox[1]) != float)
                or (type(bbox[2]) != int and type(bbox[2]) != float)
                or (type(bbox[3]) != int and type(bbox[3]) != float)):
            raise ParameterTypeError("Values of Parameter bbox must be numbers and values of parameter timeframe must be strings of the format 'year-month-day'. For example '1981-01-01'. Please specify values that follow this.")
        elif (bbox[0] < math.floor(minLon)
                or bbox[0] > math.ceil(maxLon)
                or bbox[2] < math.floor(minLon)
                or bbox[2] > math.ceil(maxLon)):
            raise LongitudeValueError("Longitude values are out of bounds. Please check the range of the dataset.")
        elif (bbox[1] > bbox[3]
                or bbox[1] < math.floor(minLat)
                or bbox[1] > math.ceil(maxLat)
                or bbox[3] < math.floor(minLat)
                or bbox[3] > math.ceil(maxLat)):
            raise LatitudeValueError("Latitude values are out of bounds. Please check the range of the dataset.")
        elif (abs(abs(bbox[2]) - abs(bbox[0])) < lon_cellsize
                or abs(bbox[1] - bbox[3]) < lat_cellsize
                or bbox[0] > maxLon and bbox[2] < minLon):
            raise BboxCellsizeError("Difference between first and second Latitude or first and second Longitude value is too small. Please check the cellsize of the dataset.")

    '''Checks parameter timeframe'''

    if len(timeframe) != 2:
        raise TimeframeLengthError("Parameter timeframe is an array with two values: [start date, end date]. Please specify an array with exactly two values.")

    try:
        x = isinstance(np.datetime64(timeframe[0]),np.datetime64)
        x = isinstance(np.datetime64(timeframe[1]),np.datetime64)

    except ValueError:
        raise ParameterTypeError("Values of Parameter bbox must be numbers and values of parameter timeframe must be strings of the format 'year-month-day'. For example '1981-01-01'. Please specify values that follow this.")

    if (type(timeframe[0]) != str or type(timeframe[1]) != str
            or len(timeframe[0]) != 10 or len(timeframe[1]) != 10):
        raise ParameterTypeError("Values of Parameter bbox must be numbers and values of parameter timeframe must be strings of the format 'year-month-day'. For example '1981-01-01'. Please specify values that follow this.")
    elif (timeframe[0] > timeframe[1]
            or np.datetime_as_string(data["time"][0], unit='D') > timeframe[0]
            or np.datetime_as_string(data["time"][0], unit='D') > timeframe[1]
            or timeframe[1] > np.datetime_as_string(data["time"][-1], unit='D')
            or timeframe[0] > np.datetime_as_string(data["time"][-1], unit='D')):
        raise TimeframeValueError("Timeframe values are out of bounds. Please check the range of the dataset.")

    ds = mean_sst(data, timeframe, bbox)
    return ds

def mean_sst(data, timeframe, bbox = [-999,-999,-999,-999]):
    '''
    Calculates mean sea surface temperature and creates temporal and spatial subset.

    Parameters:
        data (dask dataset): dataset
        timeframe ([str]): tuple with values for start and end dates, e.g. ['1981-10-01','1981-11-01']
        bbox ([float]): optional, Array with four values: [min Longitude, min Latitude, max Longitude, max Latitude]

    Returns:
        ds (xarray dataset): dataset with mean sea surface temperature
    '''

    start = timeframe[0]
    end = timeframe[1]

    if (start == end):
        ds = data.sel(time = start)
        if (bbox != [-999,-999,-999,-999]):
            ds = createSubset(ds, bbox[0], bbox[1], bbox[2], bbox[3])
        ds = ds.load()
        return ds
    else:
        ds = data.sel(time=slice(start, end))
        if (bbox != [-999,-999,-999,-999]):
            ds = createSubset(ds, bbox[0], bbox[1], bbox[2], bbox[3])
        ds = ds.sst.mean(dim=('time'))
        ds = ds.load()
        return ds
