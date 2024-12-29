from typing import Callable

import numpy as np
from matplotlib import pyplot as plt


Function = Callable[[float], float]


def get_line(p1, p2) -> Function:
    m = (p2[1] - p1[1]) / (p2[0] - p1[0])
    b = p1[1] - m * p1[0]
    return lambda x: m * x + b


def get_monotone_parabola(p1, p2, p3, visualize=False) -> Function:
    x, y = np.array([p1, p2, p3]).T
    A = np.array([x ** 2, x, np.ones(3)]).T
    a, b, c = np.linalg.solve(A, y)
    f = lambda x: a * x ** 2 + b * x + c
    x_vertex = -b / (2 * a)

    if x.min() <= x_vertex <= x.max():
        raise ValueError(f'Defined parabola is not monotone in given range (x_vertex={x_vertex}). Choose another points')

    if visualize:
        x = range(int(x.min()), int(x.max()) + 1)
        plt.title(f'Parabola in given range (x_vertex={x_vertex:.2f})')
        plt.plot(x, [f(x) for x in x])
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.grid(True)

    return f
