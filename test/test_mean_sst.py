import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 

import xarray as xr
import pytest
from dask.distributed import Client, LocalCluster

@pytest.fixture(scope="module")
def dask_client():
    cluster = LocalCluster()
    client = Client(cluster)
    yield client
    ''' teardown '''
    client.close()
    cluster.close()

from mean_sst import *

os.getcwd()
ds = xr.open_dataset("./GeoSoftII_SST_Process/test/sst.day.mean.1984-03-4days.nc", chunks={"time": "auto"})

'''test function createSubset'''

def test_createSubsetNormalCase():
    x = createSubset(ds, 0, -20, 100, 20)
    for i in x["lon"].values:
        assert(i >= 0 and i <= 100)
    for i in x["lat"].values:
        assert(i >= -20 and i <= 20)
        
def test_createSubsetMinLonGreaterThanMaxLonCase():
    x = createSubset(ds, 300, -20, 50, 20)
    assert(x["lon"].values[0] >= 300)
    assert(x["lon"].values[-1] <= 50)
    assert(x["lat"].values[0] >= -20)
    assert(x["lat"].values[-1] <= 20)
        
'''test function wrapper_mean_sst'''
    
def test_wrapper_mean_sst():
    x = wrapper_mean_sst(ds, ['1984-03-01', '1984-03-04'], [0,-20,70,20])
    assert(x["lon"].values[0] >= 0)
    assert(x["lon"].values[-1] <= 70)
    assert(x["lat"].values[0] >= -20)
    assert(x["lat"].values[-1] <= 20)
    if "time" in str(x.dims): assert False
    if len(x.values) == 0: assert False
            
def test_wrapper_mean_sst_2():
    x = wrapper_mean_sst(ds, ['1984-03-01','1984-03-01'])
    assert(x["lon"].values[0] >= 0)
    assert(x["lon"].values[-1] <= 360)
    assert(x["lat"].values[0] >= -90)
    assert(x["lat"].values[-1] <= 90)
    if "time" in str(x.dims): assert False
    if ("sst" in str(x.data_vars) == False): assert False
        
'''test function mean_sst'''
    
def test_mean_sst():
    x = mean_sst(ds, ['1984-03-01', '1984-03-04'], [0,-20,70,20])
    assert(x["lon"].values[0] >= 0)
    assert(x["lon"].values[-1] <= 70)
    assert(x["lat"].values[0] >= -20)
    assert(x["lat"].values[-1] <= 20)
    if "time" in str(x.dims): assert False
    if len(x.values) == 0: assert False
            
def test_mean_sst_2():
    x = mean_sst(ds, ['1984-03-01','1984-03-01'])
    assert(x["lon"].values[0] >= 0)
    assert(x["lon"].values[-1] <= 360)
    assert(x["lat"].values[0] >= -90)
    assert(x["lat"].values[-1] <= 90)
    if "time" in str(x.dims): assert False
    if ("sst" in str(x.data_vars) == False): assert False
    
'''test function exceptions_mean_sst'''

'''test that all necessary parameters were given in right order'''

def test_NoParameters():
    with pytest.raises(TypeError):
        exceptions_mean_sst()
        
def test_OnlyParameterData():
    with pytest.raises(TypeError):
        exceptions_mean_sst(ds)
        
def test_OnlyParameterTimeframe():
    with pytest.raises(TypeError):
        exceptions_mean_sst(['1984-03-01','1984-03-01'])
        
def test_ParametersTimeframeDataSwitched():
    with pytest.raises(AttributeError):
        exceptions_mean_sst(['1984-03-01','1984-03-01'], ds)
    
def test_ParametersTimeframeBboxSwitched():
    with pytest.raises(BboxLengthError):
        exceptions_mean_sst(ds, [0,-20,70,20], ['1984-03-01', '1984-03-04'])

'''test that parameter data has necessary attributes'''

def test_NoDataVars():
    with pytest.raises(DatasetAttributesError):
        x = ds.drop_vars("sst")
        exceptions_mean_sst(x, ['1984-03-01','1984-03-01'])
        
def test_UpperCaseSSTVar():
    with pytest.raises(DatasetAttributesError):
        x = ds.rename({"sst": "SST"})
        exceptions_mean_sst(x, ['1984-03-01','1984-03-01'])
        
def test_UpperCaseLonDim():
    with pytest.raises(DatasetAttributesError):
        x = ds.rename({"lon": "Lon"})
        exceptions_mean_sst(x, ['1984-03-01','1984-03-01'])
        
def test_UpperCaseLatDim():
    with pytest.raises(DatasetAttributesError):
        x = ds.rename({"lat": "LAT"})
        exceptions_mean_sst(x, ['1984-03-01','1984-03-01'])
        
def test_UpperCaseTimeDim():
    with pytest.raises(DatasetAttributesError):
        x = ds.rename({"time": "Time"})
        exceptions_mean_sst(x, ['1984-03-01','1984-03-01'])
    
'''test that parameter bbox has right length'''
    
def test_BboxTooLong():
    with pytest.raises(BboxLengthError):
        exceptions_mean_sst(ds, ['1984-03-01','1984-03-01'], [1,1,10,10,1])
            
def test_BboxTooShort():
    with pytest.raises(BboxLengthError):
        exceptions_mean_sst(ds, ['1984-03-01','1984-03-01'], [1,1])
        
'''test that values within parameter bbox are right type'''
    
def test_BboxIsInt():
    with pytest.raises(ParameterTypeError):
        exceptions_mean_sst(ds, ['1984-03-01','1984-03-01'], [1,1,10,'10'])
        
def test_BboxIsFloat():
    with pytest.raises(ParameterTypeError):
        exceptions_mean_sst(ds, ['1984-03-01','1984-03-01'], ['1.65',1,10,10])
            
'''test that longitude within parameter bbox is inside bounds'''

def test_LongitudeOutsideBottomRange():
    with pytest.raises(LongitudeValueError):
        exceptions_mean_sst(ds, ['1984-03-01','1984-03-01'],[-90,0,0,90])
            
def test_LongitudeOutsideTopRange():
    with pytest.raises(LongitudeValueError):
        exceptions_mean_sst(ds, ['1984-03-01','1984-03-01'],[0,0,400,90])
            
'''test that latitude within parameter bbox is inside bounds'''

def test_LatitudeOutsideBottomRange():
    with pytest.raises(LatitudeValueError): 
        exceptions_mean_sst(ds, ['1984-03-01','1984-03-01'],[0,-100,360,1])
            
def test_LatitudeOutsideTopRange():
    with pytest.raises(LatitudeValueError): 
        exceptions_mean_sst(ds, ['1984-03-01','1984-03-01'],[0,-90,360,100])
            
def test_MinLatitudeGreaterThanMaxLatitude():
    with pytest.raises(LatitudeValueError): 
        exceptions_mean_sst(ds, ['1984-03-01','1984-03-01'],[0,90,360,0])
            
'''test that latitude and longitude difference is big enough'''
    
def test_LongitudeCellsize():
    with pytest.raises(BboxCellsizeError):
        exceptions_mean_sst(ds, ['1984-03-01','1984-03-01'],[0,0,0.24,90])
        
def test_LongitudeCellsize_2():
    with pytest.raises(BboxCellsizeError):
        exceptions_mean_sst(ds, ['1984-03-01','1984-03-01'],[360,0,0,90])
    
def test_LatitudeCellsize():
    with pytest.raises(BboxCellsizeError):
        exceptions_mean_sst(ds, ['1984-03-01','1984-03-01'],[0,0,360,0.1])
            
'''test that parameter timeframe has right length'''

def test_TimeframeTooLong():
    with pytest.raises(TimeframeLengthError): 
        exceptions_mean_sst(ds, ['1984-03-01', '1984-03-01', '1984-03-01'])
            
def test_TimeframeTooShort():
    with pytest.raises(TimeframeLengthError): 
        exceptions_mean_sst(ds, ['1984-03-01'])
            
'''test that dates within parameter timeframe are inside bounds'''
                          
def test_TimeframeOutsideBottomRangeFirstP():
    with pytest.raises(TimeframeValueError): 
        exceptions_mean_sst(ds, ['1984-02-01','1984-03-01'])
            
def test_TimeframeOutsideTopRangeFirstP():
    with pytest.raises(TimeframeValueError): 
        exceptions_mean_sst(ds, ['1984-04-01','1984-03-01'])
            
def test_TimeframeOutsideBottomRangeSecondP():
    with pytest.raises(TimeframeValueError): 
        exceptions_mean_sst(ds, ['1984-03-01','1984-02-01'])
            
def test_TimeframeOutsideTopRangeSecondP():
    with pytest.raises(TimeframeValueError): 
        exceptions_mean_sst(ds, ['1984-03-01','1984-04-01'])
            
def test_StartDateBiggerThanEndDate():
    with pytest.raises(TimeframeValueError): 
        exceptions_mean_sst(ds, ['1984-03-04','1984-03-01'])
            
'''test that dates within parameter timeframe are real dates'''
                          
def test_InvalidDateFirstP():
    with pytest.raises(ParameterTypeError):
        exceptions_mean_sst(ds, ['1984-03-00','1984-03-02'])
            
def test_InvalidDateSecondP():
    with pytest.raises(ParameterTypeError):
        exceptions_mean_sst(ds, ['1984-03-01','1984-03-40'])
            
'''test that dates within parameter timeframe are valid datetimes'''
    
def test_InvalidDatetimeSyntaxFirstP_1():
    with pytest.raises(ParameterTypeError):
        exceptions_mean_sst(ds, ['1984.03.01','1984-03-02'])
            
def test_InvalidDatetimeSyntaxSecondP_1():
    with pytest.raises(ParameterTypeError):
        exceptions_mean_sst(ds, ['1984-03-01','1984.03.02'])
            
def test_InvalidDatetimeSyntaxFirstP_2():
    with pytest.raises(ParameterTypeError):
        exceptions_mean_sst(ds, ['1984-0301','1984-03-02'])
            
def test_InvalidDatetimeSyntaxSecondP_2():
    with pytest.raises(ParameterTypeError):
        exceptions_mean_sst(ds, ['1984-03-01','1984-0302'])
            
def test_InvalidDatetimeSyntaxFirstP_3():
    with pytest.raises(ParameterTypeError):
        exceptions_mean_sst(ds, ['01-03-1984','1984-03-02'])
            
def test_InvalidDatetimeSyntaxSecondP_3():
    with pytest.raises(ParameterTypeError):
        exceptions_mean_sst(ds, ['1984-03-01','02-03-1984'])

def test_InvalidDatetimeSyntaxFirstP_4():
    with pytest.raises(ParameterTypeError):
        exceptions_mean_sst(ds, ['1984-03','02-03-1984'])
        
def test_InvalidDatetimeSyntaxSecondP_4():
    with pytest.raises(ParameterTypeError):
        exceptions_mean_sst(ds, ['1984-03-01','1984-03'])
