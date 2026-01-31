from collections import defaultdict
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
