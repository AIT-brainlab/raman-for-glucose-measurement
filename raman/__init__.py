from pathlib import Path

BASE_PATH:Path = Path(__file__).parent.absolute()

FONT_FOLDER:Path = Path(BASE_PATH, ".fonts")

from .helper import set_thaifont
set_thaifont()


# Export modules
from .sample import Sample, read_txt, accumulate