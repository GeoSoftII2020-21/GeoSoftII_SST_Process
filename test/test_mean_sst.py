'''Tests'''

import unittest
import xarray as xr
import dask
import math
import numpy as np

ds = xr.open_dataset("./sst_data/sst.day.mean.1984.nc", chunks={"time": "auto"})

class TestNotebook(unittest.TestCase):
    
    '''test function createSubset'''

    def test_createSubsetNormalCase(self):
        x = createSubset(ds, 0, -20, 100, 20)
        assert(x["lon"].values[0] >= 0)
        assert(x["lon"].values[-1] <= 100)
        assert(x["lat"].values[0] >= -20)
        assert(x["lat"].values[-1] <= 20)
        
    def test_createSubsetMinLonGreaterThanMaxLonCase(self):
        x = createSubset(ds, 300, -20, 50, 20)
        assert(x["lon"].values[0] >= 300)
        assert(x["lon"].values[-1] <= 50)
        assert(x["lat"].values[0] >= -20)
        assert(x["lat"].values[-1] <= 20)
        
    '''test function mean_sst'''
    
    def test_wrapper_mean_sst(self):
        x = wrapper_mean_sst(ds, ['1984-10', '1984-10-07'], [0,-20,70,20])
        x = xr.open_dataset(x)
        assert(x["lon"].values[0] >= 0)
        assert(x["lon"].values[-1] <= 70)
        assert(x["lat"].values[0] >= -20)
        assert(x["lat"].values[-1] <= 20)
        if "time" in str(x.dims): assert False
        if ("sst" in str(x.data_vars) == False): assert False
            
    def test_wrapper_mean_sst_2(self):
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
    
    def test_BboxTooLong(self):
        with self.assertRaises(InvalidBboxLengthError):
            mean_sst(ds, ['1984-10-01','1984-11-01'], [1,1,10,10,1])
            
    def test_BboxTooShort(self):
        with self.assertRaises(InvalidBboxLengthError):
            mean_sst(ds, ['1984-10-01','1984-11-01'], [1,1])
            
    '''test that longitude within parameter bbox is inside bounds'''

    def test_LongitudeOutsideBottomRange(self):
        with self.assertRaises(InvalidLongitudeValueError):
            mean_sst(ds, ['1984-10-01','1984-11-01'],[-90,0,0,90])
            
    def test_LongitudeOutsideTopRange(self):
        with self.assertRaises(InvalidLongitudeValueError):
            mean_sst(ds, ['1984-10-01','1984-11-01'],[0,0,400,90])
            
    '''test that latitude within parameter bbox is inside bounds'''

    def test_LatitudeOutsideBottomRange(self):
        with self.assertRaises(InvalidLatitudeValueError): 
            mean_sst(ds, ['1984-10-01','1984-11-01'],[0,-100,360,1])
            
    def test_LatitudeOutsideTopRange(self):
        with self.assertRaises(InvalidLatitudeValueError): 
            mean_sst(ds, ['1984-10-01','1984-11-01'],[0,-90,360,100])
            
    def test_MinLatitudeGreaterThanMaxLatitude(self):
        with self.assertRaises(InvalidLatitudeValueError): 
            mean_sst(ds, ['1984-10-01','1984-11-01'],[0,90,360,0])
            
    '''test that latitude and longitude difference is big enough'''
    
    def test_LongitudeCellsize(self):
        with self.assertRaises(InvalidBboxValueError):
            mean_sst(ds, ['1984-10-01','1984-11-01'],[0,0,0.24,90])
    
    def test_LatitudeCellsize(self):
        with self.assertRaises(InvalidBboxValueError):
            mean_sst(ds, ['1984-10-01','1984-11-01'],[0,0,360,0.1])
            
    '''test that parameter timeframe has right length'''

    def test_TimeframeTooLong(self):
        with self.assertRaises(InvalidTimeframeLengthError): 
            mean_sst(ds, ['1984-10-01', '1984-10-01', '1984-10-01'])
            
    def test_TimeframeTooShort(self):
        with self.assertRaises(InvalidTimeframeLengthError): 
            mean_sst(ds, ['1984-10-01'])
            
    '''test that dates within parameter timeframe are inside bounds'''
                          
    def test_TimeframeOutsideBottomRangeFirstP(self):
        with self.assertRaises(InvalidTimeframeValueError): 
            mean_sst(ds, ['1983-10-01','1984-11-01'])
            
    def test_TimeframeOutsideTopRangeFirstP(self):
        with self.assertRaises(InvalidTimeframeValueError): 
            mean_sst(ds, ['1985-01-01','1984-11-01'])
            
    def test_TimeframeOutsideBottomRangeSecondP(self):
        with self.assertRaises(InvalidTimeframeValueError): 
            mean_sst(ds, ['1984-10-01','1983-12-31'])
            
    def test_TimeframeOutsideTopRangeSecondP(self):
        with self.assertRaises(InvalidTimeframeValueError): 
            mean_sst(ds, ['1985-01-01','1985-01-01'])
            
    def test_StartDateBiggerThanEndDate(self):
        with self.assertRaises(InvalidTimeframeValueError): 
            mean_sst(ds, ['1985-01-11','1985-01-01'])
            
    '''test that dates within parameter timeframe are real dates'''
                          
    def test_InvalidDateFirstP(self):
        with self.assertRaises(InvalidParameterTypeError):
            mean_sst(ds, ['1984-10-40','1984-11-01'])
            
    def test_InvalidDateSecondP(self):
        with self.assertRaises(InvalidParameterTypeError):
            mean_sst(ds, ['1984-10-01','1984-11-00'])
            
    '''test that dates within parameter timeframe are valid datetimes'''
    
    def test_InvalidDatetimeSyntaxFirstP_1(self):
        with self.assertRaises(InvalidParameterTypeError):
            mean_sst(ds, ['1984.10.40','1984-11-01'])
            
    def test_InvalidDatetimeSyntaxSecondP_1(self):
        with self.assertRaises(InvalidParameterTypeError):
            mean_sst(ds, ['1984-10-40','1984.11.01'])
            
    def test_InvalidDatetimeSyntaxFirstP_2(self):
        with self.assertRaises(InvalidParameterTypeError):
            mean_sst(ds, ['1984-1030','1984-11-01'])
            
    def test_InvalidDatetimeSyntaxSecondP_2(self):
        with self.assertRaises(InvalidParameterTypeError):
            mean_sst(ds, ['1984-10-40','1984-1101'])
            
    def test_InvalidDatetimeSyntaxFirstP_3(self):
        with self.assertRaises(InvalidParameterTypeError):
            mean_sst(ds, ['27-12-1984','1984-12-31'])
            
    def test_InvalidDatetimeSyntaxSecondP_3(self):
        with self.assertRaises(InvalidParameterTypeError):
            mean_sst(ds, ['1984-12-27','31-12-1984'])
            

    unittest.main(argv=['ignored', '-v'], exit=False)
