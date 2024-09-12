import pandas as pd
import numpy as np
import os
from pathlib import Path
from glob import glob
from datetime import datetime
import rampy as rp

def get_file_list(path:Path) -> list[str]:
    path_str:str = str(path.joinpath("*"))
    names:list[str] = []
    for name in glob(path_str):
        _,fname = os.path.split(name)
        names.append(fname)
    return names

def create_data_from_paths(paths:list[str], 
                            keys:list[str]=["name","grating","laser","exposure","accumulation","year","month","date","hour","minute","second"]
                            ) -> pd.DataFrame:
    rows = []
    for path in paths:
        row = {}
        row['path'] = path
        row['spectrum'] = rp.flipsp(np.genfromtxt(path))
        for i, key in enumerate(keys):
            _, fname = os.path.split(path)
            row[key] = fname.split("_")[i]
        rows.append(row)
    data = pd.DataFrame(rows)

    def merge_date(row):
        date_str = "".join(list(row[["year","month","date","hour","minute","second"]]))
        return datetime.strptime(date_str, '%Y%m%d%H%M%S')
    data['datetime'] = data.apply(merge_date, axis=1)
    data.drop(columns=["year","month","date","hour","minute","second"], inplace=True)


    return data

def extract_range(spectrum:np.ndarray, range_from:float, range_to:float) -> np.ndarray:
    x = spectrum[:,0]
    cond1 = x >= 900
    cond2 = x <= 1600
    return spectrum[cond1 & cond2]