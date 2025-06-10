from .finger import Finger
from .reference import Reference
from .blood import Blood
from ..sample import Sample as _Sample
from ..database import collection_finger as _collection_finger


def load_spectra_of_subject(subject_id: str) -> list[Finger]:
    """Load all spectra of a subject from the database.

    Args:
        subject_id (str): The subject ID.
    Returns:
        list[Finger]: A list of Finger objects.
    """
    fingers: list[Finger] = []
    for i in _collection_finger.find({"subject_id": subject_id}):
        finger = Finger(**i)
        finger._id = i["_id"]
        fingers.append(finger)
    return fingers


def load_spectra_of_subject_as_sample(subject_id: str) -> list[_Sample]:
    """Load all spectra of a subject from the database.

    Args:
        subject_id (str): The subject ID.
    Returns:
        list[Sample]: A list of Sample objects.
    """
    samples: list[_Sample] = []
    for i in _collection_finger.find({"subject_id": subject_id}):
        finger = Finger(**i)
        finger._id = i["_id"]
        sample = finger.to_sample()
        samples.append(sample)
    return samples
