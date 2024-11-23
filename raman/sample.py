import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from rampy.spectranization import despiking

from pathlib import Path
from datetime import datetime
from copy import deepcopy

class Sample:
    file_format_keys:list[str] = ["name","grating","laser","exposure","accumulation","year","month","date","hour","minute","second"]

    def __init__(self, path:Path):
        self.path:Path = path
        
        measure:np.ndarray = np.flip(np.genfromtxt(path), axis=0)
        self.x:np.ndarray = deepcopy(measure[:,0])
        self.y:np.ndarray = deepcopy(measure[:,1])
        self._original_x:np.ndarray = deepcopy(measure[:,0])
        self._original_y:np.ndarray = deepcopy(measure[:,1])


        filename:str = self.path.name
        self.name:str = filename.split('_')[0]
        self._info:dict = {}

        datetime_str:list[str] = []
        for i,key in enumerate(self.file_format_keys):
            if(key in ["year","month","date","hour","minute","second"]):
                datetime_str.append(filename.split('_')[i])
            else:
                self._update_info(key, filename.split('_')[i])
        self._update_info('datetime', datetime.strptime( "".join(datetime_str), "%Y%m%d%H%M%S" ))
        self._update_info('sample', self.x.shape[0])
    
    def get_data(self) -> np.ndarray:
        """
        this will return np.ndarray with shape (n_samples, 2)
        """
        return np.hstack([self.x.reshape(-1,1), self.y.reshape(-1,1)])

    def get_info(self) -> dict:
        return self._info

    def _update_info(self, key:str, value):
        self._info[key] = value

    def interpolate(self, step:float):
        minx = np.floor(self._original_x.min())
        maxx = np.ceil(self._original_x.max())
        self.x = np.arange(minx, maxx, step=step)
        y_interp = CubicSpline(self._original_x, self._original_y, bc_type="natural")
        self.y = y_interp(self.x)
        self._update_info('sample', self.x.shape[0])

    def despike(self, window_length:int=5, threshold:int=1):
        """
        neigh = 5, threshold = 1 works great during testing with the `silicon/focuspower` sample set
        """
        self.y = despiking(self.x, self.y, neigh=window_length, threshold=threshold)

    def set_raman_range(self, min:float, max:float):
        cond1 = self.x >= min
        cond2 = self.x <= max
        self.x = self.x[cond1 & cond2]
        self.y = self.y[cond1 & cond2]
        self._update_info('sample', self.x.shape[0])

    def plot(self, label:str=None):
        if( isinstance(label, type(None)) ):
            label = self.name
        plt.plot(self.x, self.y, label=label)
        # plt.show()

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"Sample({self.path})"


if(__name__ == '__main__'):
    path:Path = Path(f"data/silicon/focuspower/silicon-down_600_785 nm_90 s_1_2024_11_19_16_41_27_01.txt")
    sample = Sample(path=path)
    plt.figure(figsize=(16,9))
    sample.plot("None despike")
    sample.despike(window_length=5, threshold=1)
    sample.plot("despike")
    plt.legend()
    plt.grid()
    plt.show()
    # print(sample.get_info())
    # sample.interpolate(step=0.1)
    # print(sample.get_info())
    # print(sample._info)