from pydantic import BaseModel, ConfigDict
from datetime import datetime
from pathlib import Path
import numpy as np
from copy import deepcopy
from typing import Self
from pymongo.errors import DuplicateKeyError

from raman.database import collection_finger, collection_ref
from raman.sample import Sample


def _load_raman_from_txt(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load a raman spectrum from a file

    Args:
        path (Path): Path to the file
    Returns:
        tuple[np.ndarray, np.ndarray]: Wavelength and intensity
    """
    measure: np.ndarray = np.flip(np.genfromtxt(path), axis=0)
    return deepcopy(measure[:, 0]), deepcopy(measure[:, 1])


class Finger(BaseModel):
    """
    Class to represent a single raman spectrum of Finger
    """

    _id = None  # MongoDB ObjectId
    id: int
    grating: int
    laser: int
    exposure: int
    accumulation: int
    timestamp: datetime
    lens: str = "x10"
    power: float = 7.0

    subject_id: str | None = None
    glucose: float | None = None
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
                    Finger object
        """
        if not path.exists():
            raise FileNotFoundError(f"File {path} does not exist")

        format = [
            "id",
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

        # "0_600_785 nm_60 s_1_2024_03_19_08_31_34_01.txt"
        filename = path.name
        x, y = _load_raman_from_txt(path=path)

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
                    item[key] = int(value)

        item["timestamp"] = datetime.strptime("".join(datetime_str), "%Y%m%d%H%M%S")  # type: ignore
        item["raman_shift"] = list(x)  # type: ignore
        item["intensity"] = list(y)  # type: ignore
        finger = Finger(**item)

        return finger  # type: ignore

    @classmethod
    def from_database(cls, subject_id: str, timestamp: datetime) -> Self:
        """
        Load a raman spectrum from the database
        Args:
            subject_id (str): Subject ID
            timestamp (datetime): Timestamp
        Returns:
            Finger object
        """
        query = {"subject_id": subject_id, "timestamp": timestamp}
        item = collection_finger.find_one(query)
        if item is None:
            raise ValueError(
                f"Item with subject_id {subject_id} and timestamp {timestamp} not found"
            )

        finger = Finger(**item)
        finger._id = item["_id"]
        return finger  # type: ignore

    def to_sample(self, interpolate: bool = True, verbose: bool = True) -> Sample:
        """Convert the spectrum to a sample object

        Returns:
            Sample: Sample object
        """
        x = np.array(self.raman_shift)
        y = np.array(self.intensity)
        sample = Sample(x=x, y=y, interpolate=interpolate, verbose=verbose)
        sample.name = f"{self.subject_id}_{self.id}"  # type: ignore
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
        if self.subject_id is None:
            raise ValueError("subject_id is not set")
        # if self.glucose is None:
        #     raise ValueError("glucose is not set")
        if self._id is None:
            try:
                item = collection_finger.insert_one(self.model_dump())
                self._id = item.inserted_id
            except DuplicateKeyError:
                raise DuplicateKeyError(
                    f"Duplicate entry for {self.subject_id} at {self.timestamp}"
                )
        else:
            collection_finger.update_one({"_id": self._id}, {"$set": self.model_dump()})

    def delete(self):
        if self._id is None:
            pass
        collection_finger.delete_one({"_id": self._id})


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
        x, y = _load_raman_from_txt(path=path)

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


def load_spectra_of_subject(subject_id: str) -> list[Finger]:
    """Load all spectra of a subject from the database.

    Args:
        subject_id (str): The subject ID.
    Returns:
        list[Finger]: A list of Finger objects.
    """
    finger_samples: list[Finger] = []
    for i in collection_finger.find({"subject_id": subject_id}):
        finger = Finger(**i)
        finger._id = i["_id"]
        finger_samples.append(finger)
    return finger_samples


def load_spectra_of_subject_as_sample(subject_id: str) -> list[Sample]:
    """Load all spectra of a subject from the database.

    Args:
        subject_id (str): The subject ID.
    Returns:
        list[Sample]: A list of Sample objects.
    """
    samples: list[Sample] = []
    for i in collection_finger.find({"subject_id": subject_id}):
        finger = Finger(**i)
        finger._id = i["_id"]
        sample = finger.to_sample()
        samples.append(sample)
    return samples
