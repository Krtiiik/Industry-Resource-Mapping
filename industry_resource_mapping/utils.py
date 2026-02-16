from collections import defaultdict
import functools
import random
from typing import Callable, Iterable


def groupby[T, TProperty](iterable: Iterable[T], f_by: Callable[[T], TProperty]
                          ) -> dict[TProperty, list[T]]:
    """
    Groups the items of a given iterable by properties extracted by a given extractor function.

    Args:
        iterable: Iterable of items to group into groups by a selector.
        by: The selector function extracting a property to group by.

    Returns:
        The items grouped into groups based on the selector function.
    """
    grouped = defaultdict(list)
    for item in iterable:
        prop = f_by(item)
        grouped[prop].append(item)
    return grouped


def range_randomizer_function(range: tuple[int, int]) -> Callable[[], int]:
    return functools.partial(random.Random().randint, *range)


class IdManager[T]:
    def __init__(self, format_f: Callable[[int], T]):
        self._format_f = format_f
        self._counter = 0

    def new(self) -> T:
        self._counter += 1
        return self._format_f(self._counter)

    def reset(self):
        self._counter = 0

    @property
    def counter(self) -> int:
        return self._counter
