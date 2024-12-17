from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MaxNLocator, PercentFormatter

from dex_sonar.time_series import TimeSeries


Symbol = str


@dataclass
class Pair:
    symbol: Symbol
    prices: TimeSeries[float]
    turnovers: TimeSeries[float]
    turnover: float
    open_interest: float
    funding_rate: Optional[float]
    next_funding_time: datetime

    def update(self, turnover, open_interest, funding_rate, next_funding_time):
        self.turnover = turnover
        self.open_interest = open_interest
        self.funding_rate = funding_rate
        self.next_funding_time = next_funding_time

    def create_chart(
            self,
            width=16,
            height_ratio=0.25,

            color='#4287f5',
            prices_as_percents=False,
            timestamp_format='%H:%M',

            size_tick=1.0,

            alpha_tick=0.6,
            alpha_turnover=0.1,
            alpha_grid=0.2,

            max_ticks_x=None,
            max_ticks_y=None,
    ) -> plt.Figure:

        fig, ax1 = plt.subplots(figsize=(width, width * height_ratio))
        ax1: plt.Axes
        ax2: plt.Axes = ax1.twinx()
        axes = ax1, ax2

        # create graphs
        ax1.plot(
            self.prices.get_timestamps(),
            self.prices.get_values(),
            color=color,
            linewidth=1.5,
        )
        ax2.bar(
            self.turnovers.get_timestamps(),
            self.turnovers.get_values(),
            color=color,
            alpha=alpha_turnover,
            width=0.001 * width / 16,
        )

        # remove edges
        for ax in axes:
            for edge in [
                'left',
                'right',
                'top',
                'bottom'
            ]:
                ax.spines[edge].set_visible(False)

        # remove margins
        for ax in axes: ax.margins(x=0, y=0)

        # remove ticks and move tick labels
        for ax in axes: ax.tick_params(left=False, bottom=False, right=False)
        ax1.tick_params(
            labelleft=False,
            labelright=True,
        )
        ax2.tick_params(
            labelleft=True,
            labelright=False,
            labelbottom=False,
        )

        # set tick size and opacity
        ax1.tick_params(axis='both', labelsize=size_tick * 10, colors=(0, 0, 0, alpha_tick))
        ax2.tick_params(axis='y', labelsize=size_tick * 10, colors=(0, 0, 0, alpha_tick))

        # format ticks
        ax1.xaxis.set_major_formatter(DateFormatter(timestamp_format))
        if not prices_as_percents: ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,g}'))
        else: ax1.yaxis.set_major_formatter(PercentFormatter(xmax=self.prices[-1]))
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))

        # limit the number of ticks
        if max_ticks_x: ax1.xaxis.set_major_locator(MaxNLocator(nbins=max_ticks_x))
        if max_ticks_y: ax1.yaxis.set_major_locator(MaxNLocator(nbins=max_ticks_y))
        if max_ticks_y: ax2.yaxis.set_major_locator(MaxNLocator(nbins=max_ticks_y))

        # add grid
        ax1.grid(
            color='#000000',
            alpha=alpha_grid,
            linewidth=0.5,
        )

        return fig
