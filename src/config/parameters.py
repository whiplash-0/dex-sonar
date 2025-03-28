import logging
from os import environ

from src.config.config import CONFIGS_DIR, config, TEST_MODE  # noqa: F40


PROD_MODE = not TEST_MODE

BOT_TOKEN = environ.get('BOT_TOKEN' if PROD_MODE else 'TESTING_BOT_TOKEN')
SILENT_BOT_TOKEN = environ.get('SILENT_BOT_TOKEN' if PROD_MODE else 'TESTING_SILENT_BOT_TOKEN')

USER_ID = int(environ.get('USER_ID'))

LOGGING_FORMAT = (
    '%(name)s :: %(levelname)s :: %(message)s'
    if PROD_MODE else
    '%(asctime)s :: %(name)s :: %(message)s'
)
LOGGING_LEVEL = (
    logging.INFO
    if not config.getboolean('Logging', 'debug') else
    logging.DEBUG
)
LOGGING_TIMESTAMP_FORMAT = '%m-%d %H:%M:%S'
