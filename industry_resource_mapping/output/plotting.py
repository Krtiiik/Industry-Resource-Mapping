from typing import Iterable, Literal, Tuple

import matplotlib.artist
import matplotlib.axes
from matplotlib.collections import PathCollection
from matplotlib.path import Path
import matplotlib.patches
import matplotlib.text
import matplotlib.transforms

from industry_resource_mapping.instances import MappingResult
from industry_resource_mapping.output.utils import points_on_circle

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TLoc = Tuple[float, float]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TextPathProperties:
    letter_width: float = 0.602
    font_size: float = 1.0
    font_properties = {
        "family": "monospace",
        "weight": "light",
    }


class ProviderProperties:
    height: float = 2.0
    text_margin_horizontal: float = 0.1
    article_offset: TLoc = (0.1, 0.1)
    amount_offset: TLoc = (0.1, -1 + 0.1)


class DemandProperties:
    height: float = 2.0
    text_margin_horizontal: float = 0.1
    article_offset: TLoc = (0.1, 0.1)
    amount_offset: TLoc = (0.1, -1 + 0.1)


class MappingProperties:
    arrow_width: float = 5.0

# Utils ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def add_artists(ax: matplotlib.axes.Axes, artists: Iterable[matplotlib.artist.Artist]):
    for artist in artists:
        ax.add_artist(artist)


def loc_offset(loc: TLoc, offset: TLoc) -> TLoc:
    return (loc[0] + offset[0], loc[1] + offset[1])

# Building Blocks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def _box(loc: TLoc, width: float, height: float,
         ) -> matplotlib.path.Path:
    loc_x, loc_y = loc

    verts = [
        (loc_x, loc_y),  # left, bottom
        (loc_x, loc_y + height),  # left, top
        (loc_x + width, loc_y + height),  # right, top
        (loc_x + width, loc_y),  # right, bottom
        (loc_x, loc_y),  # ignored
    ]
    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.CLOSEPOLY,
    ]

    return Path(verts, codes)


def _text_in_circle(text: str,
                   center: TLoc, radius: float,
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

# Plotting ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def demand(loc: TLoc, article: str, amount: int,
           ax: matplotlib.axes.Axes = None,
           ) -> tuple[TLoc, list[matplotlib.artist.Artist]]:
    amount_str = str(amount)

    width = (max(len(article), len(amount_str)) * TextPathProperties.letter_width) + (2*DemandProperties.text_margin_horizontal)
    loc = loc_offset(loc, (-width, 0))

    loc_article = loc_offset(loc, DemandProperties.article_offset)
    loc_amount = loc_offset(loc, DemandProperties.amount_offset)

    if len(article) > len(amount_str):
        offset = (len(article) - len(amount_str)) * TextPathProperties.letter_width
        loc_amount = loc_offset(loc_amount, (offset, 0))
    elif len(article) < len(amount_str):
        offset = (len(amount_str) - len(article)) * TextPathProperties.letter_width
        loc_article = loc_offset(loc_article, (offset, 0))

    paths = [
        matplotlib.text.TextPath(loc_article,
                                 article,
                                 size=TextPathProperties.font_size, prop=TextPathProperties.font_properties),
        matplotlib.text.TextPath(loc_amount,
                                 amount_str,
                                 size=TextPathProperties.font_size, prop=TextPathProperties.font_properties),
    ]

    artists = [
        matplotlib.patches.PathPatch(_box(loc_offset(loc, (0, -DemandProperties.height/2)), width, ProviderProperties.height),
                                     color="red"),
        PathCollection(paths, color="black"),
    ]

    if ax:
        add_artists(ax, artists)

    anchor = loc
    return anchor, artists


def producer(loc: TLoc, article: str, amount: int,
             ax: matplotlib.axes.Axes = None,
             ) -> tuple[TLoc, list[matplotlib.artist.Artist]]:
    amount_str = str(amount)

    width = max(len(article), len(amount_str)) * TextPathProperties.letter_width + 2*ProviderProperties.text_margin_horizontal

    paths = [
        matplotlib.text.TextPath(loc_offset(loc, ProviderProperties.article_offset),
                                 article,
                                 size=TextPathProperties.font_size, prop=TextPathProperties.font_properties),
        matplotlib.text.TextPath(loc_offset(loc, ProviderProperties.amount_offset),
                                 amount_str,
                                 size=TextPathProperties.font_size, prop=TextPathProperties.font_properties),
    ]

    artists = [
        matplotlib.patches.PathPatch(_box(loc_offset(loc, (0, -(ProviderProperties.height/2))), width, ProviderProperties.height),
                                     color="green"),
        PathCollection(paths, color="black"),
    ]

    if ax:
        add_artists(ax, artists)

    anchor = loc_offset(loc, (width, 0))
    return anchor, artists


def mapping(provider: TLoc, demand: TLoc, amount: int, label: str = None,
            ax: matplotlib.axes.Axes = None,
            ) -> list[matplotlib.artist.Artist]:
    amount_str = str(amount)

    provider_x, provider_y = provider
    demand_x, demand_y = demand
    arrow_dx = demand_x - provider_x
    arrow_dy = demand_y - provider_y

    paths = [
        # TODO rotate with arrow, if needed
        matplotlib.text.TextPath(loc_offset(provider, (arrow_dx/2, arrow_dy/2)),
                                 amount_str,
                                 size=TextPathProperties.font_size, prop=TextPathProperties.font_properties),
    ]

    artists = [
        matplotlib.patches.Arrow(provider_x, provider_y, arrow_dx, arrow_dy, width=MappingProperties.arrow_width),
        PathCollection(paths, color="black"),
    ]

    if ax:
        add_artists(ax, artists)
    return artists


def plot_mapping_result(mapping_result: MappingResult):
    # TODO need to calculate positions of the nodes
    # - draw demands as red rectangles [[===]]
    # - draw providers as green semicircles [D]
    # - Mappings between corresponding demands and providers as lines

    origins_providers = mapping_result.providers_by_origin.keys()
    origins_demands = mapping_result.demands_by_origin.keys()
    origins_both = origins_providers & origins_demands
    origins_just_providers = origins_providers - origins_both
    origins_just_demands = origins_demands - origins_both
