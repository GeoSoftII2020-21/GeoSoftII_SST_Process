#!/usr/bin/env python
# coding: utf-8

# In[1]:


'''packages'''
import xarray as xr
import dask
import math
import numpy as np




# In[2]:


'''Dask Cluster'''
from dask.distributed import Client, LocalCluster
cluster = None
client = None
firstRun = True


# In[189]:


'''Exceptions'''

class InvalidParameterTypeError(Exception):
  def __init__(self, message):
    self.message = message
    
class InvalidBboxLengthError(Exception):
  def __init__(self, message):
    self.message = message
    
class InvalidBboxValueError(Exception):
  def __init__(self, message):
    self.message = message
    
class InvalidLongitudeValueError(Exception):
  def __init__(self, message):
    self.message = message
    
class InvalidLatitudeValueError(Exception):
  def __init__(self, message):
    self.message = message
    
class InvalidTimeframeLengthError(Exception):
  def __init__(self, message):
    self.message = message

class InvalidTimeframeValueError(Exception):
  def __init__(self, message):
    self.message = message
    


# In[4]:


def createSubset(ds, minLon, minLat, maxLon, maxLat): 
  '''
  Creates a spatial subset.
  
  Parameters:
    ds (dask dataset): dataset, from which a Subset is generates
    minLon (double): left value
    minLat (double): bottom value
    maxLon (double): right value
    maxLat (double): top value
    
  Returns:
    ds_subset (dask dataset): spatially limited dataset 
  '''
  if (minLon > maxLon):
    ds_subset1 = ds.sel(lon=slice(minLon, ds["lon"].actual_range[1]), lat=slice(minLat, maxLat))
    ds_subset2 = ds.sel(lon=slice(ds["lon"].actual_range[0], maxLon), lat=slice(minLat, maxLat))
    ds_subset_concat = xr.concat([ds_subset1, ds_subset2], "lon")
    '''update metadata'''
    ds_subset_concat["lon"].actual_range[0] = ds_subset_concat["lon"].values[0]
    ds_subset_concat["lon"].actual_range[1] = ds_subset_concat["lon"].values[-1]
    ds_subset_concat["lat"].actual_range[0] = ds_subset_concat["lat"].values[0]
    ds_subset_concat["lat"].actual_range[1] = ds_subset_concat["lat"].values[-1]
    return ds_subset_concat
  else:
    ds_subset = ds.sel(lon=slice(minLon, maxLon), lat=slice(minLat, maxLat))
    '''update metadata'''
    ds_subset["lon"].actual_range[0] = ds_subset["lon"].values[0]
    ds_subset["lon"].actual_range[1] = ds_subset["lon"].values[-1]
    ds_subset["lat"].actual_range[0] = ds_subset["lat"].values[0]
    ds_subset["lat"].actual_range[1] = ds_subset["lat"].values[-1]
    return ds_subset


# In[190]:


def wrapper_mean_sst(data, timeframe, bbox = [-999,-999,-999,-999]):
    '''
    Passes parameters on to function mean_sst and catches exceptions.
  
    Parameters:
        ds (dask dataset): dataset
        timeframe ([str]): tuple with values for start and end dates, e.g. ['1981-10-01','1981-11-01']
        bbox ([double]): optional, Array with four values: [min Longitude, min Latitude, max Longitude, max Latitude]
    
    Returns:
        ds_nc (netcdf): dataset with mean sea surface temperature
    '''
    global cluster
    global client
    global firstRun
    if firstRun:
        cluster = LocalCluster()
        client = Client(cluster)
        client
        firstRun = False
    
    try: 
        x = mean_sst(data, timeframe, bbox)
        return x
    
    except InvalidParameterTypeError as e:
        print(e.message)
    except InvalidBboxLengthError as e:
        print(e.message)
    except InvalidLongitudeValueError as e:
        print(e.message)
    except InvalidLatitudeValueError as e:
        print(e.message)
    except InvalidBboxValueError as e:
        print(e.message)
    except InvalidTimeframeLengthError as e:
        print(e.message)
    except InvalidTimeframeValueError as e:
        print(e.message)


# In[216]:


def mean_sst(data, timeframe, bbox = [-999,-999,-999,-999]):
    '''
    Calculates mean sea surface temperature.
  
    Parameters:
        timeframe ([str]): tuple with values for start and end dates, e.g. ['1981-10-01','1981-11-01']
        bbox ([double]): optional, Array with four values: [min Longitude, min Latitude, max Longitude, max Latitude]
    
    Returns:
        ds_nc (netcdf): dataset with mean sea surface temperature
    '''
    
    '''Checks parameters and raises exceptions'''
   
    '''Checks parameter bbox'''
    
    lon_cellsize = abs(data["lon"].values[0] - data["lon"].values[1])
    lat_cellsize = abs(data["lat"].values[0] - data["lat"].values[1])
    
    if len(bbox) != 4:
        raise InvalidBboxLengthError("Parameter bbox is an array with four values: [min Longitude, min Latitude, max Longitude, max Latitude]. Please specify an array with exactly four values.")
    elif (bbox != [-999,-999,-999,-999]):
        if (type(bbox[0]) != int and type(bbox[0]) != float) or (type(bbox[1]) != int and type(bbox[1]) != float) or (type(bbox[2]) != int and type(bbox[2]) != float) or (type(bbox[3]) != int and type(bbox[3]) != float):
            raise InvalidParameterTypeError("Values of Parameter bbox must be numbers and values of parameter timeframe must be strings of the format 'year-month-day'. For example '1981-01-01'. Please specify timeframe values that follow this.")
        elif bbox[0] < math.floor(data["lon"].actual_range[0]) or bbox[0] > math.ceil(data["lon"].actual_range[1]) or bbox[2] < math.floor(data["lon"].actual_range[0]) or bbox[2] > math.ceil(data["lon"].actual_range[1]): 
            raise InvalidLongitudeValueError("Longitude values are out of bounds. Please check the range of the dataset.")
        elif bbox[1] > bbox[3] or bbox[1] < math.floor(data["lat"].actual_range[0]) or bbox[1] > math.ceil(data["lat"].actual_range[1]) or bbox[3] < math.floor(data["lat"].actual_range[0]) or bbox[3] > math.ceil(data["lat"].actual_range[1]): 
            raise InvalidLatitudeValueError("Latitude values are out of bounds. Please check the range of the dataset.")
        elif abs(bbox[2] - bbox[0]) < lon_cellsize or abs(bbox[3] - bbox[1]) < lat_cellsize:
            raise InvalidBboxValueError("Latitude or Longitude difference is too small. Please check the cellsize of the dataset.")
  
    '''Checks parameter timeframe'''

    if len(timeframe) != 2:
        raise InvalidTimeframeLengthError("Parameter timeframe is an array with two values: [start date, end date]. Please specify an array with exactly two values.")
    
    try:
        x = isinstance(np.datetime64(timeframe[0]),np.datetime64)
        x = isinstance(np.datetime64(timeframe[1]),np.datetime64)

    except ValueError:
        raise InvalidParameterTypeError("Values of Parameter bbox must be numbers and values of parameter timeframe must be strings of the format 'year-month-day'. For example '1981-01-01'. Please specify timeframe values that follow this.")
    
    if (type(timeframe[0]) != str) or (type(timeframe[1]) != str):
        raise InvalidParameterTypeError("Values of Parameter bbox must be numbers and values of parameter timeframe must be strings of the format 'year-month-day'. For example '1981-01-01'. Please specify timeframe values that follow this.")                               
    elif timeframe[0] > timeframe[1] or np.datetime_as_string(data["time"][0], unit='D') > timeframe[0] or np.datetime_as_string(data["time"][0], unit='D') > timeframe[1] or timeframe[1] > np.datetime_as_string(data["time"][-1], unit='D') or timeframe[0] > np.datetime_as_string(data["time"][-1], unit='D'):
        raise InvalidTimeframeValueError("Timeframe values are out of bounds. Please check the range of the dataset.")
    
    '''Compute mean and temporal and spatial subset'''
    
    start = timeframe[0]
    end = timeframe[1]
    
    if (start == end):
        ds_day = data.sel(time = start)
        if (bbox != [-999,-999,-999,-999]):
            ds_day = createSubset(ds_day, bbox[0], bbox[1], bbox[2], bbox[3])
        ds_day = ds_day.compute()
        #ds_nc = ds_day.to_netcdf() Alte Codezeile
        ds_nc = ds_day #Neue Codezeile
        return ds_nc
    else:
        ds_timeframe = data.sel(time=slice(start, end))
        if (bbox != [-999,-999,-999,-999]):
            ds_timeframe = createSubset(ds_timeframe, bbox[0], bbox[1], bbox[2], bbox[3])
        ds_timeframe_mean = ds_timeframe.sst.mean(dim=('time'))
        ds_timeframe_mean = ds_timeframe_mean.compute()
        #ds_nc = ds_timeframe_mean.to_netcdf() Alte Codezeile
        ds_nc = ds_timeframe_mean #Neue Codezeile
        return ds_nc

# Hilfsfunktion: falls lon > 180, werden 360 abgezogen
# wandelt lon werte von 0 bis 360 in -180 bis 180 um
# nur zur Visualisierung in einem Spzeialfall verwendet

def min360(x):
  if x > 180:
    return x-360
  else:
    return x


# In[220]:


