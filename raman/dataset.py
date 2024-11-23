from raman.sample import Sample
import matplotlib.pyplot as plt

import math
import logging
from pathlib import Path

_logger = logging.getLogger(__name__)

class FolderNotFoundError(Exception):
    pass


class SampleSet:
    _samples:list[Sample] = None
    _range:tuple[float,float] = (-math.inf, math.inf)

    def __init__(self, path:Path, lazy_load:bool=True):
        if(path.exists() == False):
            raise FolderNotFoundError(f"The folder={path.as_posix()} is not found.")
        
        self.path:Path = path

        if(lazy_load == False):
            self._load_samples()

    def  _load_samples(self):
        path:Path = self.path
        self._samples = []
        range_min = math.inf
        range_max = -math.inf
        for sample_path in sorted(list(path.glob("*.txt"))):
            sample = Sample(path=sample_path)
            self._samples.append(sample)
            if(sample.x.min() < range_min): range_min = sample.x.min()
            if(sample.x.max() > range_max): range_max = sample.x.max()
        self._range = (range_min, range_max)
        print(self._range, range_min, range_max)
        _logger.info(f"Load {len(self._samples)} samples in {self}")

    def get_samples(self) -> list[Sample]:
        if( isinstance( self._samples, type(None) ) ):
            self._load_samples()
        return self._samples

    def interpolate(self, step:float):
        for sample in self.get_samples():
            sample.interpolate(step=step)

    def set_raman_range(self, min:float, max:float):
        for sample in self.get_samples():
            sample.set_raman_range(min=min, max=max)
        self._range = (min, max)

    def plot(self):
        plt.figure(figsize=(16,9))
        for sample in self.get_samples():
            plt.plot(sample.x, sample.y, label=sample.name)
        plt.legend()
        plt.grid()
        plt.xlim(self._range[0] - 10, self._range[1] + 10)
        plt.ylim(0, 0xFFFF) #range of 16 bit is 0 - 65536 (0xFFFF is all 1 in 16 bits)
        plt.show()

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"SampleSet({self.path.as_posix()})"


if(__name__ == "__main__"):
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    path:Path = Path(f"data/silicon/focuspower")
    sampleset = SampleSet(path=path)
    sampleset.plot()
    # TODO: Implement despike here


    sampleset.interpolate(step=0.1)
    sampleset.plot()
    sampleset.set_raman_range(min=600, max=1600)
    sampleset.plot()