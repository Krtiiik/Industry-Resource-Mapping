from __future__ import annotations
from typing import Any, Iterable, Literal, Tuple

import matplotlib
import matplotlib.artist
import matplotlib.axes
import matplotlib.patches
import matplotlib.text
import numpy as np

from .instances import MappingResult

# Plotting ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def plot_mapping_result(mapping_result: MappingResult):
    # TODO need to calculate positions of the nodes
    # - draw demands as red rectangles [[===]]
    # - draw providers as green semicircles [D]
    # - Mappings between corresponding demands and providers as lines
    ...


def add_artists(ax: matplotlib.axes.Axes, artists: Iterable[matplotlib.artist.Artist]):
    for artist in artists:
        ax.add_artist(artist)


def points_on_circle(center: Tuple[float, float],
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


def text_in_circle(text: str,
                   center: Tuple[float, float], radius: float,
                   num_points: int, start: float = 0, stop: float = 360,
                   start_point: bool = True, end_point: bool = False,
                   text_alignment: Literal["left", "center", "right"] = "left",
                   font_properties: dict = None, correction: Literal[None, "odd", "even"] = None,
                   ax: matplotlib.axes.Axes = None,
                   ) -> list[matplotlib.artist.Artist]:
    match correction:
        case None:
            pass
        case "odd":
            if len(text) % 2 == 1:
                num_points += 1
        case "even":
            if len(text) % 2 == 0:
                num_points += 1
        case _:
            raise ValueError("Unrecognized text correction")

    xs, ys, rots = points_on_circle(center, radius, num_points, start, stop, start_point, end_point)

    match text_alignment:
        case "left":
            pass  # locations as-is
        case "center" | "right":
            text_length, num_points = len(text), len(xs)
            if text_length >= num_points:
                pass  # text fills all the points
            else:
                empty_points = num_points - text_length
                if text_alignment == "center":
                    offset = empty_points // 2
                elif text_alignment == "right":
                    offset = empty_points

                xs = xs[offset:]
                ys = ys[offset:]
                rots = rots[offset:]
        case _:
            raise ValueError("Unrecognized text alignment option")

    letter_artists = []
    for letter, x, y, rot in zip(text, xs, ys, rots):
        letter_artists.append(matplotlib.text.Text(x, y, letter,
                                                   rotation=rot, rotation_mode="anchor",
                                                   ha="center", va="center",
                                                   font_properties=font_properties))

    if ax:
        add_artists(ax, letter_artists)

    return letter_artists


def producer(loc: Tuple[float, float], article: str, amount: int,
             article_font_properties: dict[str, Any] = None, amount_font_properties: dict[str, Any] = None,
             ax: matplotlib.axes.Axes = None,
             ) -> list[matplotlib.patches.artist.Artist]:
    if article_font_properties is None:
        article_font_properties = {
            "size": 20,
            "family": "monospace",
        }
    if amount_font_properties is None:
        amount_font_properties = {
            # "size": 1,
            "size": 30,
        }
    loc_x, loc_y = loc

    artists = [
        matplotlib.patches.Wedge(loc, 1, 270, 90, color="green"),
        *text_in_circle(text=article, center=loc,
                        radius=0.9, num_points=15, start=270, stop=450, start_point=False, end_point=False,
                        text_alignment="center", font_properties=article_font_properties, correction="even"),
        # matplotlib.patches.PathPatch(matplotlib.textpath.TextPath((loc_x + 0.1, loc_y-0.35), str(amount), prop=amount_font_properties), color="black"),
        matplotlib.text.Text(loc_x + 0.1, loc_y, amount,
                             font_properties=amount_font_properties, va="center"),
    ]

    if ax:
        add_artists(ax, artists)
    return artists


def demand(loc: Tuple[float, float], article: str, amount: int,
           article_font_properties: dict[str, Any] = None, amount_font_properties: dict[str, Any] = None,
           ax: matplotlib.axes.Axes = None,
           ) -> list[matplotlib.patches.artist.Artist]:
    if article_font_properties is None:
        article_font_properties = {
            "size": 20,
            "family": "monospace",
        }
    if amount_font_properties is None:
        amount_font_properties = {
            "size": 20,
        }
    loc_x, loc_y = loc

    artists = [
        matplotlib.patches.Rectangle((loc_x - 1.5, loc_y - 0.25), 1.5, 0.5, color="firebrick"),
        matplotlib.text.Text(loc_x - 1.4, loc_y, article, font_properties=article_font_properties, va="center"),
        matplotlib.text.Text(loc_x - 0.35, loc_y, amount, font_properties=amount_font_properties, va="center"),
    ]

    if ax:
        add_artists(ax, artists)
    return artists


# Printing ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def print_mapping_result(mapping_result: MappingResult):
    print("Mapping Result")
    print("Instance", mapping_result.instance.name)
    print("Demands")
    for demand in mapping_result.demands:
        print("\t", demand)
    print("Providers")
    for provider in mapping_result.providers:
        print("\t", provider)
    print("Mappings")
    for mapping in mapping_result.mappings:
        print("\t", mapping)
