import logging
from configparser import ConfigParser
from datetime import timedelta
from os import environ, getcwd, path


class Config(ConfigParser):
    def read(self, file_name, directory_path='configs', **kwargs):
        super().read(path.join(getcwd(), directory_path, file_name))

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


config = Config()
config.read('config.ini')
config.read('dev.ini')
if config.getboolean('Bot', 'testing_mode'): config.read('testing.ini')


TESTING_MODE = config.getboolean('Bot', 'testing_mode')
PRODUCTION_MODE = not TESTING_MODE

LOGGING_LEVEL = logging.INFO if not config.getboolean('Logging', 'debug_mode') else logging.DEBUG
LOGGING_FORMAT = (
    '%(name)s :: %(levelname)s :: %(message)s'
    if PRODUCTION_MODE else
    '%(asctime)s :: %(name)s :: %(message)s'
)
LOGGING_TIMESTAMP_FORMAT = '%m-%d %H:%M:%S'

BOT_TOKEN = environ.get('BOT_TOKEN' if PRODUCTION_MODE else 'TESTING_BOT_TOKEN')
SILENT_BOT_TOKEN = environ.get('SILENT_BOT_TOKEN' if PRODUCTION_MODE else 'TESTING_SILENT_BOT_TOKEN')
