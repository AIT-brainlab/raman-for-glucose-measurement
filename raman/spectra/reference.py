
from ..database import collection_ref
from ..sample import Sample
from .function import load_raman_from_txt

from pydantic import BaseModel, ConfigDict
from typing import Self
from pymongo.errors import DuplicateKeyError


import numpy as np
from datetime import datetime
from pathlib import Path

class Reference(BaseModel):
    """
    Class to represent a single raman spectrum of Finger
    """

    _id = None  # MongoDB ObjectId
    name: str
    grating: int
    laser: int
    exposure: int
    accumulation: int
    timestamp: datetime
    lens: str = "x10"
    power: float = 7.1

    raman_shift: list[float]
    intensity: list[float]

    model_config = ConfigDict(revalidate_instances="always")

    def __init__(self, **data):
        super().__init__(**data)

    @classmethod
    def from_file(cls, path: Path) -> Self:
        """Load a raman spectrum from a file
        re
                Args:
                    path (Path): Path to the file

                Returns:
                    Reference object
        """
        if not path.exists():
            raise FileNotFoundError(f"File {path} does not exist")

        format = [
            "name",
            "grating",
            "laser",
            "exposure",
            "accumulation",
            "year",
            "month",
            "date",
            "hour",
            "minute",
            "second",
            "01",
        ]

        # "glucose_600_785 nm_60 s_1_2024_03_19_08_31_34_01.txt"
        filename = path.name
        x, y = load_raman_from_txt(path=path)

        item = {}

        datetime_str = []
        for key, value in zip(format, filename.split("_")):
            if key in ["year", "month", "date", "hour", "minute", "second"]:
                datetime_str.append(value)
            else:
                if key in ["exposure", "laser"]:
                    item[key] = int(value.split(" ")[0])
                elif key in ["power"]:
                    item[key] = float(value.replace("-", "."))  # type: ignore
                elif key in ["accumulation", "grating"]:
                    item[key] = int(value)
                elif key == "01":
                    continue
                else:
                    item[key] = value  # type: ignore

        item["timestamp"] = datetime.strptime("".join(datetime_str), "%Y%m%d%H%M%S")  # type: ignore
        item["raman_shift"] = list(x)  # type: ignore
        item["intensity"] = list(y)  # type: ignore
        ref = Reference(**item)

        return ref  # type: ignore

    @classmethod
    def from_database(cls, name: str) -> Self:
        """
        Load a raman spectrum from the database
        Args:
            name (str): Reference name
        Returns:
            Reference object
        """
        query = {"name": name}
        item = collection_ref.find_one(query)
        if item is None:
            raise ValueError(
                f"Item with name {name} and timestamp not found"
            )

        ref = Reference(**item)
        ref._id = item["_id"]
        return ref  # type: ignore

    def to_sample(self, interpolate: bool = True, verbose: bool = True) -> Sample:
        """Convert the spectrum to a sample object

        Returns:
            Sample: Sample object
        """
        x = np.array(self.raman_shift)
        y = np.array(self.intensity)
        sample = Sample(x=x, y=y, interpolate=interpolate, verbose=verbose)
        sample.name = f"{self.name}"  # type: ignore
        sample.exposure = self.exposure
        sample.accumulation = self.accumulation
        sample.grating = int(self.grating)  # type: ignore
        sample.laser = str(self.laser)
        sample.power = self.power
        sample.lens = self.lens
        sample.date = self.timestamp
        return sample

    def save(self):
        self.model_validate(obj=self)
        if self.name is None:
            raise ValueError("name is not set")
        if self._id is None:
            try:
                item = collection_ref.insert_one(self.model_dump())
                self._id = item.inserted_id
            except DuplicateKeyError:
                raise DuplicateKeyError(
                    f"Duplicate entry for {self.name} at {self.timestamp}"
                )
        else:
            collection_ref.update_one({"_id": self._id}, {"$set": self.model_dump()})

    def delete(self):
        if self._id is None:
            pass
        collection_ref.delete_one({"_id": self._id})
