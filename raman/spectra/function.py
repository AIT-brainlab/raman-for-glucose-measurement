from pathlib import Path
import numpy as np
from numpy.typing import NDArray
from copy import deepcopy

def load_raman_from_txt(path: Path) -> tuple[NDArray, NDArray]:
    """Load a raman spectrum from a file

    Args:
        path (Path): Path to the file
    Returns:
        tuple[NDArray, NDArray]: Wavelength and intensity
    """
    measure:NDArray = np.flip(np.genfromtxt(path), axis=0)
    return deepcopy(measure[:, 0]), deepcopy(measure[:, 1])
