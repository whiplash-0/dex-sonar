import logging
import sys
from datetime import tzinfo
from logging import CRITICAL, DEBUG, ERROR, Formatter, INFO, LogRecord, StreamHandler, WARNING, getLogger
from math import floor
from statistics import mean
from zoneinfo import ZoneInfo

import colorama
from colorama import Fore

from src.utils.time import Timestamp



VERBOSE = floor(mean([
    INFO,
    WARNING,
]))


def verbose(self, msg, *args, **kwargs):
    if self.isEnabledFor(VERBOSE):
        self._log(VERBOSE, msg, args, **kwargs)



class ColoredFormatter(Formatter):
    def format(self, record: LogRecord):
        return {
            logging.DEBUG:    Fore.BLUE,
            VERBOSE:          Fore.MAGENTA,
            logging.INFO:     Fore.BLACK,
            logging.WARNING:  Fore.YELLOW,
            logging.ERROR:    Fore.RED,
            logging.CRITICAL: Fore.RED,
        }[record.levelno] + super().format(record)



def setup_logging(
        level: str,
        format: str,
        timestamp_format: str,
        timezone: tzinfo = ZoneInfo('UTC'),
        forward_to_stdout=False,
):
    root_logger = getLogger()

    # remove all handlers (prevents duplicates in Jupyter)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    logging.Formatter.converter = lambda *args: Timestamp.now(timezone).timetuple()

    colorama.init(autoreset=True)
    logging.addLevelName(VERBOSE, 'VERBOSE')
    logging.Logger.verbose = verbose

    root_logger.setLevel(level=level)

    handler = StreamHandler(None if not forward_to_stdout else sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(ColoredFormatter(format, datefmt=timestamp_format))
    root_logger.addHandler(handler)

    for scope, default_level, debug_level in [
        ('telegram',   WARNING,  None    ),
        ('pybit',      WARNING,  None    ),
        ('websocket',  CRITICAL, WARNING ),
        ('asyncio',    WARNING,  None    ),
        ('httpx',      WARNING,  None    ),
        ('httpcore',   INFO,     None    ),
        ('matplotlib', INFO,     None    ),
        ('urllib3',    ERROR,    None    ),
    ]:
        getLogger(scope).setLevel(
            default_level
            if level > DEBUG or debug_level is None else
            debug_level
        )
