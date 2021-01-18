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
    # teardown
    client.close()
    cluster.close()

from mean_sst import InvalidParameterTypeError, InvalidBboxLengthError, InvalidBboxValueError, InvalidLongitudeValueError, InvalidLatitudeValueError, InvalidTimeframeLengthError, InvalidTimeframeValueError  
from mean_sst import createSubset, wrapper_mean_sst, mean_sst

ds = xr.open_dataset("../sst_data/sst.day.mean.1984.nc", chunks={"time": "auto"})
        
'''test function createSubset'''

def test_createSubsetNormalCase():
    x = createSubset(ds, 0, -20, 100, 20)
    assert(x["lon"].values[0] >= 0)
    assert(x["lon"].values[-1] <= 100)
    assert(x["lat"].values[0] >= -20)
    assert(x["lat"].values[-1] <= 20)
        
def test_createSubsetMinLonGreaterThanMaxLonCase():
    x = createSubset(ds, 300, -20, 50, 20)
    assert(x["lon"].values[0] >= 300)
    assert(x["lon"].values[-1] <= 50)
    assert(x["lat"].values[0] >= -20)
    assert(x["lat"].values[-1] <= 20)
        
'''test function mean_sst'''
    
def test_wrapper_mean_sst():
    x = wrapper_mean_sst(ds, ['1984-10', '1984-10-07'], [0,-20,70,20])
    x = xr.open_dataset(x)
    assert(x["lon"].values[0] >= 0)
    assert(x["lon"].values[-1] <= 70)
    assert(x["lat"].values[0] >= -20)
    assert(x["lat"].values[-1] <= 20)
    if "time" in str(x.dims): assert False
    if ("sst" in str(x.data_vars) == False): assert False
            
def test_wrapper_mean_sst_2():
    x = wrapper_mean_sst(ds, ['1984-02-25','1984-02-25'])
    x = xr.open_dataset(x)
    assert(x["lon"].values[0] >= 0)
    assert(x["lon"].values[-1] <= 360)
    assert(x["lat"].values[0] >= -90)
    assert(x["lat"].values[-1] <= 90)
    if "time" in str(x.dims): assert False
    if ("sst" in str(x.data_vars) == False): assert False
    
'''test exceptions'''

'''test that parameter bbox has right length'''
    
def test_BboxTooLong():
    with pytest.raises(InvalidBboxLengthError):
        mean_sst(ds, ['1984-10-01','1984-11-01'], [1,1,10,10,1])
            
def test_BboxTooShort():
    with pytest.raises(InvalidBboxLengthError):
        mean_sst(ds, ['1984-10-01','1984-11-01'], [1,1])
        
'''test that values within parameter bbox are right type'''
    
def test_BboxIsInt():
    with pytest.raises(InvalidParameterTypeError):
        mean_sst(ds, ['1984-10-01','1984-11-01'], [1,1,10,'10'])
        
def test_BboxIsFloat():
    with pytest.raises(InvalidParameterTypeError):
        mean_sst(ds, ['1984-10-01','1984-11-01'], ['1.65',1,10,10])
            
'''test that longitude within parameter bbox is inside bounds'''

def test_LongitudeOutsideBottomRange():
    with pytest.raises(InvalidLongitudeValueError):
        mean_sst(ds, ['1984-10-01','1984-11-01'],[-90,0,0,90])
            
def test_LongitudeOutsideTopRange():
    with pytest.raises(InvalidLongitudeValueError):
        mean_sst(ds, ['1984-10-01','1984-11-01'],[0,0,400,90])
            
'''test that latitude within parameter bbox is inside bounds'''

def test_LatitudeOutsideBottomRange():
    with pytest.raises(InvalidLatitudeValueError): 
        mean_sst(ds, ['1984-10-01','1984-11-01'],[0,-100,360,1])
            
def test_LatitudeOutsideTopRange():
    with pytest.raises(InvalidLatitudeValueError): 
        mean_sst(ds, ['1984-10-01','1984-11-01'],[0,-90,360,100])
            
def test_MinLatitudeGreaterThanMaxLatitude():
    with pytest.raises(InvalidLatitudeValueError): 
        mean_sst(ds, ['1984-10-01','1984-11-01'],[0,90,360,0])
            
'''test that latitude and longitude difference is big enough'''
    
def test_LongitudeCellsize():
    with pytest.raises(InvalidBboxValueError):
        mean_sst(ds, ['1984-10-01','1984-11-01'],[0,0,0.24,90])
    
def test_LatitudeCellsize():
    with pytest.raises(InvalidBboxValueError):
        mean_sst(ds, ['1984-10-01','1984-11-01'],[0,0,360,0.1])
            
'''test that parameter timeframe has right length'''

def test_TimeframeTooLong():
    with pytest.raises(InvalidTimeframeLengthError): 
        mean_sst(ds, ['1984-10-01', '1984-10-01', '1984-10-01'])
            
def test_TimeframeTooShort():
    with pytest.raises(InvalidTimeframeLengthError): 
        mean_sst(ds, ['1984-10-01'])
            
'''test that dates within parameter timeframe are inside bounds'''
                          
def test_TimeframeOutsideBottomRangeFirstP():
    with pytest.raises(InvalidTimeframeValueError): 
        mean_sst(ds, ['1983-10-01','1984-11-01'])
            
def test_TimeframeOutsideTopRangeFirstP():
    with pytest.raises(InvalidTimeframeValueError): 
        mean_sst(ds, ['1985-01-01','1984-11-01'])
            
def test_TimeframeOutsideBottomRangeSecondP():
    with pytest.raises(InvalidTimeframeValueError): 
        mean_sst(ds, ['1984-10-01','1983-12-31'])
            
def test_TimeframeOutsideTopRangeSecondP():
    with pytest.raises(InvalidTimeframeValueError): 
        mean_sst(ds, ['1985-01-01','1985-01-01'])
            
def test_StartDateBiggerThanEndDate():
    with pytest.raises(InvalidTimeframeValueError): 
        mean_sst(ds, ['1985-01-11','1985-01-01'])
            
'''test that dates within parameter timeframe are real dates'''
                          
def test_InvalidDateFirstP():
    with pytest.raises(InvalidParameterTypeError):
        mean_sst(ds, ['1984-10-40','1984-11-01'])
            
def test_InvalidDateSecondP():
    with pytest.raises(InvalidParameterTypeError):
        mean_sst(ds, ['1984-10-01','1984-11-00'])
            
'''test that dates within parameter timeframe are valid datetimes'''
    
def test_InvalidDatetimeSyntaxFirstP_1():
    with pytest.raises(InvalidParameterTypeError):
        mean_sst(ds, ['1984.10.40','1984-11-01'])
            
def test_InvalidDatetimeSyntaxSecondP_1():
    with pytest.raises(InvalidParameterTypeError):
        mean_sst(ds, ['1984-10-40','1984.11.01'])
            
def test_InvalidDatetimeSyntaxFirstP_2():
    with pytest.raises(InvalidParameterTypeError):
        mean_sst(ds, ['1984-1030','1984-11-01'])
            
def test_InvalidDatetimeSyntaxSecondP_2():
    with pytest.raises(InvalidParameterTypeError):
        mean_sst(ds, ['1984-10-40','1984-1101'])
            
def test_InvalidDatetimeSyntaxFirstP_3():
    with pytest.raises(InvalidParameterTypeError):
        mean_sst(ds, ['27-12-1984','1984-12-31'])
            
def test_InvalidDatetimeSyntaxSecondP_3():
    with pytest.raises(InvalidParameterTypeError):
        mean_sst(ds, ['1984-12-27','31-12-1984'])
