import subprocess
from math import log10
from os import environ

from src.config.config import CONFIG
from src.pairs.pair import Contract


TEST_MODE = CONFIG.getboolean('Bot', 'test mode')
PROD_MODE = not TEST_MODE


BOT_TOKEN = environ.get('BOT_TOKEN' if PROD_MODE else 'TEST_BOT_TOKEN')
SILENT_BOT_TOKEN = environ.get('SILENT_BOT_TOKEN' if PROD_MODE else 'TEST_SILENT_BOT_TOKEN')

USER_ID = int(environ.get('USER_ID'))

if not CONFIG.getboolean('Bot', 'cloud'):  # use CLI to fetch URL
    result = subprocess.run(
        ['heroku', 'config:get', 'DATABASE_URL', '-a', CONFIG.get('Heroku', 'app name')],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode == 0: DATABASE_URL = result.stdout.strip()
    else: raise ValueError(f'Error fetching `DATABASE_URL` via CLI: {result.stderr.strip()}')

else:  # otherwise Heroku will add it to environment variables
    DATABASE_URL = environ.get('DATABASE_URL')

DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+asyncpg://', 1)  # ensure compatibility with asynchronous paradigm


PAIRS_FILTER = (
    lambda pairs: [
        x for x in pairs if
        x.turnover >= CONFIG.getfloat('Pairs', 'min turnover', default=0)
    ]
)

class UpspikeDetector:
    @staticmethod
    def _create_threshold_linear_piecewise_interpolation(*points: tuple[int, float]):
        """
        :param points: tuples of (minute, percentage)
        """
        xs, ys = [p[0] for p in points], [p[1] / 100 for p in points]

        def linear_piecewise_function(x):
            for i in range(len(xs) - 1):
                if xs[i] <= x <= xs[i + 1]:
                    x1, y1 = xs[i], ys[i]
                    x2, y2 = xs[i + 1], ys[i + 1]
                    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)

            raise ValueError(f'{x} is outside of interpolation range')

        return linear_piecewise_function

    THRESHOLD_FUNCTION = (
        _create_threshold_linear_piecewise_interpolation(
            (1, 6),
            (2, 11),
            (3, 15),
            (5, 20),
            (10, 30),
            (30, 40),
        )
        if PROD_MODE else
        lambda _: 0
    )

    @staticmethod
    def _create_turnover_based_log_scaling(base_turnover, scaling_factor=2):
        """
        :param base_turnover: in millions of $
        """
        return lambda x: 1 / (scaling_factor ** (log10(x) - log10(base_turnover * 1e6)))

    TURNOVER_MULTIPLIER = _create_turnover_based_log_scaling(
        base_turnover=200,
        scaling_factor=2,
    )
