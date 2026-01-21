import unittest

from industry_resource_mapping.algorithms import plan_production_ignoring_existing
from industry_resource_mapping.instances import Article, ArticleProduction, Demand, MappingInstance


class plan_production_ignoring_existing_Tests(unittest.TestCase):
    INSTANCES = [
        MappingInstance(
            name="Empty",
            articles=[],
            demands=[],
            providers=[],
            article_productions=[],
        ),
        MappingInstance(
            name="Simple_NoProduction",
            articles=[Article("1")],
            demands=[Demand("D1", "1", 1)],
            providers=[],
            article_productions=[],
        ),
        MappingInstance(
            name="Simple_WithProduction",
            articles=[Article("1"), Article("2")],
            demands=[Demand("D1", "1", 1)],
            providers=[],
            article_productions=[ArticleProduction("AP1", "1", [("2", 2)], 10)],
        ),
    ]

    def test_no_error(self):
        for instance in self.INSTANCES:
            with self.subTest(instance=instance.name):
                _ = plan_production_ignoring_existing(instance)
