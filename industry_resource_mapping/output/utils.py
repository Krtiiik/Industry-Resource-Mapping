import numpy as np


def points_on_circle(center: tuple[float, float],
                     radius: float,
                     num: int,
                     start: float = 0,
                     stop: float = 360,
                     startpoint = False,
                     endpoint=False,
                     ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if not startpoint:
        num += 1
    start, stop = (start/360) * 2*np.pi, (stop/360) * 2*np.pi
    phis = np.linspace(start, stop, num, endpoint=endpoint)
    x_center, y_center = center
    xs = x_center + (radius * np.cos(phis))
    ys = y_center + (radius * np.sin(phis))
    rots = (phis - (1.5 * np.pi)) / (2*np.pi) * 360
    if not startpoint:
        xs = xs[1:]
        ys = ys[1:]
        rots = rots[1:]
    return xs, ys, rots
