from raman.helper import bold

import numpy as np
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

from pathlib import Path
import os
from typing import Self
from datetime import datetime
from copy import deepcopy

class Sample:
    """
    `Sample` is a representation of a measurement.
    
    When two `Samples` have the same Raman Shift (`x`), emulating longer `exposure` can be done with `sample1 + sample2`.
    The result is an object `sample1` with the followings update.
    - (1) `sample1.y` + `sample2.y`
    - (2) `sample1.exposure` + `sample2.exposure`
    - (3) `sample1.paths`.union(`sample2.paths`)
    
    When two `Samples` have the same Raman Shift (`x`) and same `exposure`, emulating accumulation can be done with `sample1 | sample2`.
    - (1) ( (`sample1.accumulation` * `sample1.y`) + (`sample2.accumulation` * `sample2.y`) ) / (`sample1.accumulation` + `sample2.accumulation`)
    - (2) `sample1.accumulation` + `sample2.accumulation`
    - (3) `sample1.paths`.union(`sample2.paths`)
    

    Attributes
    ----------
    name : str
        A nme of this `Sample`. Can be any string. By default, it names 'unname'
    x : NDArray of shape (n_samples, )
        A RamanShift of the measurement 
    y : NDArray of shape (n_samples, )
        A measured scattering 
    paths : set of pathlib.Path
        A set of path where the data is loaded from (if it is loaded from file).
    date : datetime
        A datetime when the data is collected.
    exposure : int
        A time in second to collect the sample.
    accumulation : int
        Number of accumulation done for the sample. Generally, more accumulation is give you better SNR.
    grating : str
        The information which grating is used to collect the sample.
    laser : str
        The information which laser (nm) is used to collect the sample.
    
    """

    name   :str = "unname"
    x      :np.ndarray
    y      :np.ndarray
    paths  :set[Path]
    date   :datetime
    exposure:int
    accumulation:int
    grating:str
    laser  :str

    _dx:float

    def __init__(self, x:np.ndarray, y:np.ndarray, path:(str|Path|None)=None, interpolate:bool=True):
        if(isinstance( x, np.ndarray ) == False):
            raise TypeError(f"Expecting `x` to be type of np.ndarray but got {type(x)}")
        if(isinstance( y, np.ndarray ) == False):
            raise TypeError(f"Expecting `y` to be type of np.ndarray but got {type(y)}")
        if(x.shape != y.shape):
            raise ValueError(f"shape mismatch between x={x.shape} and y={y.shape}")
            
        # Original Data that should not be replace so that we can always reset.
        self._x:np.ndarray = deepcopy(x)
        self._y:np.ndarray = deepcopy(y)

        self.paths:set[Path] = set({})
        if(path):
            self.paths.add(Path(path))
        
        self.reset_data()
        if(interpolate):
            self.interpolate(step=1)
        
    @property
    def shape(self) -> np.ndarray.shape:
        return self.data.shape
    
    @property
    def data(self) -> np.ndarray:
        return np.hstack([self.x.reshape(-1,1), self.y.reshape(-1,1)])

    def reset_data(self):
        """
        Use to set/reset the data (`x` and `y`) with the original data.
        """
        self.x:np.ndarray = deepcopy(self._x)
        self.y:np.ndarray = deepcopy(self._y)
        self._dx:float = np.diff(self.x).mean()

    def interpolate(self, step:float):
        """
        Use to interpolate with `scipy.interpolate.CubicSpline` the signal. 

        Parameters
        ----------
        step : float
            The resolution of the interpolated signal.
        """
        minx = np.floor(self.x.min())
        maxx = np.ceil(self.x.max())
        new_x = np.arange(minx, maxx + step, step=step)
        y_interp = CubicSpline(self.x, self.y, bc_type="natural")
        self.y = y_interp(new_x)
        self.x = new_x
        self._dx = step

    def extract_range(self, low:float, high:float):
        """
        Use to extract Raman Shift range [low, high]

        Parameters
        ----------
        low : float
            Start of the Raman Shift to extract
        high : float
            End of the Raman Shift to extract
        """
        cond1 = self.x >= low
        cond2 = self.x <= high
        self.x = self.x[cond1 & cond2]
        self.y = self.y[cond1 & cond2]

    def is_same_range(self, sample:Self) -> bool:
        """
        This will check whether the Raman Shift of the input `sample` is the same with this or not.

        Parameters
        ----------
        sample : Sample
            Another instance of `Sample`

        """
        if( isinstance(sample, Sample) == False ):
            raise TypeError(f"sample must be type={type(self)}. sample is type={type(sample)}")
        a = self.x
        b = sample.x

        if(a.shape != b.shape):
            return False

        return bool((a == b).all())

    def __radd__(self, b) -> Self:
        return self.__add__(b)
    def __add__(self, b:Self) -> Self:
        if(isinstance(b, int)):
            new_sample = deepcopy(self)
            new_sample.y += b
            return new_sample

        if( isinstance(b, Sample) == False):
            raise TypeError(f"Expect a + b to be type={type(self)}. b is type={type(b)}")
            
        if(self.is_same_range(b) == False):
            raise ValueError(f"Expect both a + b to have the same Raman Shift range.")
        
        new_sample = deepcopy(self)
        new_sample.y += b.y
        new_sample.exposure += b.exposure
        new_sample.paths = new_sample.paths.union(b.paths)
        return new_sample
    
    def __rmul__(self, b:float) -> Self:
        return self.__mul__(b)
    def __mul__(self, b:float) -> Self:
        if(isinstance(b, float)):
            new_sample = deepcopy(self)
            new_sample.y *= b
            return new_sample
        else:
            raise TypeError(f"Expect a * b to be type={float}. b is type={type(b)}")

    def __ror__(self, b:Self) -> Self:
        return self.__or__(b)
    def __or__(self, b:Self) -> Self:
        if( isinstance(b, Sample) == False):
            raise TypeError(f"Expect a | b to be type={type(self)}. b is type={type(b)}")
            
        if(self.is_same_range(b) == False):
            raise ValueError(f"Expect both a | b to have the same Raman Shift range.")
        
        if(self.exposure != b.exposure):
            raise ValueError(f"Expect both a | b to have the same exposure.")
        
        new_sample = deepcopy(self)
        acc1 = self.accumulation
        acc2 = b.accumulation
        y1 = acc1 * self.y
        y2 = acc2 * b.y
        new_sample.y = (y1 + y2) / (acc1 + acc2)
        new_sample.accumulation = (acc1 + acc2)
        new_sample.paths = new_sample.paths.union(b.paths)
        return new_sample



    def plot(self, label:str=None):
        if( isinstance(label, type(None)) ):
            label = self.name
        plt.plot(self.x, self.y, label=label, alpha=0.8, linewidth=0.8)

    def __getitem__(self, idx):
        return self.data[idx]

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        rep = f"""
  {bold('Sample')}: {self.name}
    {bold('date')}: {self.date}
 {bold('grating')}: {self.grating}
   {bold('laser')}: {self.laser}
{bold('exposure')}: {self.exposure} s
    {bold('accu')}: {self.accumulation}
"""
        return rep

##########################################
##########################################
################ METHOD ##################
##########################################
##########################################


def _load_raman_from_txt(path:Path) -> tuple[np.ndarray, np.ndarray]:
    measure:np.ndarray = np.flip(np.genfromtxt(path), axis=0)
    return deepcopy(measure[:,0]), deepcopy(measure[:,1])

def read_txt(path:(str|Path), 
    name_format:list[str] = ["name","grating",
                        "laser","exposure",
                        "accumulation","year",
                        "month","date",
                        "hour","minute",
                        "second", "01"]
                        ) -> Sample:
    """
    Load `Sample` from .txt file exported from Horiba LS6 software

    Parameters
    ----------
    path : str or pathlib.Path
        A path to the .txt file. Could be either `str` or `pathlib.Path`
    name_format : list of str, optional
        A list indicates the naming scheme of the file.
        Default naming scheme is `name_grating_laser_exposure_accumelation_year_month_date_hour_minute_second_01`.
    
    Returns
    -------
    Sample
        Object `Sample` is returned.
    """

    # Check if `path` is str
    if( isinstance(path, str) ):
        path:Path = Path(path)
    # Check if path exist
    if( path.exists() == False):
        raise FileNotFoundError(f"Path={path.as_posix()} is not exist.")
    
    # 24_600_785 nm_60 s_1_2024_03_19_10_30_09_01
    filename:str = os.path.splitext(path.name)[0]
    values:list[str] = filename.split('_')
    if(len(values) != len(name_format)):
        raise ValueError(f"name_format ({len(name_format)}) is not match the filename ({len(values)}) after split.\nname_format={name_format}.\nfilename={values}")
    
    x,y = _load_raman_from_txt(path=path)
    
    sample = Sample(x=x, y=y, path=path)

    datetime_str:list[str] = []
    for key, value in zip(name_format, values):
        if(key in ["year","month","date","hour","minute","second"]):
            datetime_str.append(value)
        else:
            if(key in ["exposure"]):
                value = int(value.split(' ')[0])
            elif(key in ["accumulation"]):
                value = int(value)
            elif(key == '01'): continue
            sample.__setattr__(key, value)
    sample.__setattr__('date', datetime.strptime( "".join(datetime_str), "%Y%m%d%H%M%S" ))
    return sample
    
if __name__ == '__main__':
    sample1 = read_txt(path=f"data/silicon/focuspower/silicon-down_600_785 nm_90 s_1_2024_11_19_16_41_27_01.txt")
    sample2 = read_txt(path=f"data/silicon/focuspower/silicon-down_600_785 nm_60 s_1_2024_11_19_16_33_46_01.txt")
    sample3 = read_txt(path=f"data/silicon/focuspower/silicon-down_600_785 nm_30 s_1_2024_11_19_16_28_40_01.txt")
    sample:Sample = sample1 | (sample2 + sample3)
    print(sample)
    print(sample1)
    print(sample2)
    print(sample3)
    sample.plot("sample")
    sample1.plot("sample1")
    sample2.plot("sample2")
    sample3.plot("sample3")
    plt.legend()
    plt.show()