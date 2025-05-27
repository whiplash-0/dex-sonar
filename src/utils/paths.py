import inspect
from pathlib import Path



CODE_DIRECTORY = 'src'

class Paths:
    CONFIGS = 'configs'



MODULE_PATH = Path(inspect.getfile(inspect.currentframe()))
PROJECT_PATH = Path(*MODULE_PATH.parts[:MODULE_PATH.parts.index(CODE_DIRECTORY)])

for attribute, value in vars(Paths).items():
    if not attribute.startswith('__'): setattr(Paths, attribute, PROJECT_PATH / value)
