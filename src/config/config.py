import sys
from configparser import RawConfigParser
from datetime import timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from src.utils.paths import Paths


DEFAULT_PRESET = 'default'

CONFIG = None


class Config(RawConfigParser):
    def __init__(self, directory_path: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directory_path = directory_path
        
    def load(self, name: str, **kwargs):
        self.read(self.directory_path / (name + '.ini'), **kwargs)

    def getint(self, section, option, default: int = None, **kwargs) -> int | None:
        return super().getint(section, option, **kwargs) if self.get(section, option, **kwargs) else default

    def getfloat(self, section, option, default: float = None, **kwargs) -> float | None:
        return super().getfloat(section, option, **kwargs) if self.get(section, option, **kwargs) else default

    def get_timedelta_from_seconds(self, section, option, default: timedelta = None, **kwargs) -> timedelta | None:
        return timedelta(seconds=self.getint(section, option, **kwargs)) if self.get(section, option, **kwargs) else default

    def get_timedelta_from_minutes(self, section, option, default: timedelta = None, **kwargs) -> timedelta | None:
        return timedelta(minutes=self.getint(section, option, **kwargs)) if self.get(section, option, **kwargs) else default

    def get_timedelta_from_hours(self, section, option, default: timedelta = None, **kwargs) -> timedelta | None:
        return timedelta(hours=self.getint(section, option, **kwargs)) if self.get(section, option, **kwargs) else default

    def get_timezone(self, section, option, default: ZoneInfo = None, **kwargs) -> ZoneInfo | None:
        return ZoneInfo(self.get(section, option, **kwargs)) if self.get(section, option, **kwargs) else default


_preset_path = Paths.CONFIGS / (DEFAULT_PRESET if len(sys.argv) == 1 else sys.argv[1])
if len(sys.argv) > 1 and not _preset_path.exists(): raise ValueError(f"Preset doesn't exist: '{sys.argv[1]}' ({_preset_path})")

CONFIG = Config(directory_path=_preset_path)
CONFIG.load('config')
CONFIG.load('dev')
if CONFIG.getboolean('Bot', 'test mode'): CONFIG.load('test')
