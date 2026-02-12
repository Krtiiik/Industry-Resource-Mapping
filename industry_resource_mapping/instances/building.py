from typing import Any, Iterable, Protocol
import networkx as nx

from psplib_editor.graphs import build_instance_graph
from psplib_editor.instances import ProblemInstance, Job, T_JobId

from .data import Article, ArticleProduction, T_ArticleId


class Naming:
    separator = "-"
    article = "Article"
    article_production = "ArticleProduction"

    @staticmethod
    def name_article(id: T_JobId):
        return Naming.name(Naming.article, id)

    @staticmethod
    def name_article_production(id: T_JobId):
        return Naming.name(Naming.article_production, id)

    @staticmethod
    def name(prefix: str, id: Any) -> str:
        return f"{prefix}{Naming.separator}{id}"


# Builders ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Production Builders --------------------------------------------------------------------------------------------------

class ProductionBuilder(Protocol):
    def __call__(self, job: Job, article: Article, requirements: Iterable[Article]) -> ArticleProduction:
        ...


class UnitaryProductionBuilder(ProductionBuilder):
    def __call__(self, job, article, requirements):
        return ArticleProduction(
            id=Naming.name_article_production(job.id),
            article=article.id,
            requirements=[(req, 1) for req in requirements],
            duration=job.duration,
        )

# Data Building ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def _build_articles_with_productions(
        instance: ProblemInstance,
        production_builder: ProductionBuilder,
        ) -> tuple[list[Article], list[ArticleProduction]]:
    instance_graph = build_instance_graph(instance, ignore_dummy_jobs=True)
    jobs_ordered = nx.topological_sort(instance_graph)
    jobs_by_id = instance.jobs_by_id

    articles_by_job_id: dict[T_JobId, Article] = {}
    article_productions = []
    for job_id in jobs_ordered:
        article_id = Naming.name_article(job_id)
        article = Article(article_id)
        job = jobs_by_id[job_id]
        required_articles = [articles_by_job_id[p] for p in instance_graph.predecessors(job_id)]
        article_production = production_builder(job, required_articles, article)

        articles_by_job_id[job_id] = article
        article_productions.append(article_production)

    return articles_by_job_id.values(), article_productions
