from typing import Any, Iterable
import typing
import networkx as nx

from psplib_editor.graphs import build_instance_graph
from psplib_editor.instances import ProblemInstance, Job, T_JobId

from .data import Article, ArticleProduction, Demand, MappingInstance, Provider, T_ArticleId
from ..utils import range_randomizer_function


class Naming:
    separator = "-"
    mapping_instance = "Instance"
    article = "Article"
    article_production = "ArticleProduction"
    provider = "Provider"
    demand = "Demand"

    @staticmethod
    def name_instance(psplib_name: str, details: str = None) -> str:
        name = f"{Naming.mapping_instance}.{psplib_name}"
        if details:
            name += f"{Naming.separator}{details}"
        return name

    @staticmethod
    def name_article(id: T_JobId) -> str:
        return Naming.name(Naming.article, id)

    @staticmethod
    def name_article_production(article: T_ArticleId) -> str:
        return Naming.name(Naming.article_production, article)

    @staticmethod
    def name_provider(article: T_ArticleId) -> str:
        return Naming.name(Naming.provider, article)

    @staticmethod
    def name_demand(article: T_ArticleId) -> str:
        return Naming.name(Naming.demand, article)

    @staticmethod
    def name(prefix: str, id: Any) -> str:
        return f"{prefix}{Naming.separator}{id}"

# Builders ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class InstanceDataBuilder:
    def __init__(self):
        self._instance: ProblemInstance | None = None
        self._instance_graph: nx.DiGraph | None = None
        self._articles_by_job_id: typing.Mapping[T_JobId, Article] | None = None  # Assumed to be update externally, only a reference

    def init(self, instance: ProblemInstance, instance_graph: nx.DiGraph, articles_by_job_id: typing.Mapping[T_JobId, Article]):
        self._instance = instance
        self._instance_graph = instance_graph
        self._articles_by_job_id = articles_by_job_id

# Production Builders --------------------------------------------------------------------------------------------------

class ProductionBuilder(InstanceDataBuilder):
    def __call__(self, article: Article, job: Job) -> ArticleProduction:
        ...


class UnitaryProductionBuilder(ProductionBuilder):
    def __call__(self, article, job):
        requirements = [self._articles_by_job_id[p].id  # assume all predecessors were processed and indexed prior
                        for p in self._instance_graph.predecessors(job.id)]
        return ArticleProduction(
            id=Naming.name_article_production(job.id),
            article=article.id,
            requirements=[(req, 1) for req in requirements],
            duration=job.duration,
        )

# Provider Builders ----------------------------------------------------------------------------------------------------

class ProviderBuilder(InstanceDataBuilder):
    def __call__(self, article: Article, job: Job) -> Iterable[Provider]:
        ...


class NoProviderBuilder(ProviderBuilder):
    def __call__(self, article, job):
        return []  # No providers for any article


class SourceJobProviderBuilder(ProviderBuilder):
    def __init__(self, rand_range: tuple[int, int]):
        super().__init__()
        self._rand = range_randomizer_function(rand_range)

    def __call__(self, article, job):
        if self._instance_graph.in_degree(job.id) == 0:
            amount = self._rand()
            return [Provider(Naming.name_provider(article.id), article.id, amount)]
        else:
            return []  # No providers for non-source job-articles

# Demand Builders ------------------------------------------------------------------------------------------------------

class DemandBuilder(InstanceDataBuilder):
    def __call__(self, article: Article, job: Job) -> Iterable[Demand]:
        ...


class NoDemandBuilder(DemandBuilder):
    def __call__(self, article, job):
        return []  # No demands for any article


class SinkJobDemandBuilder(DemandBuilder):
    def __init__(self, rand_range: tuple[int, int]):
        super().__init__()
        self._rand = range_randomizer_function(rand_range)

    def __call__(self, article, job):
        if self._instance_graph.out_degree(job.id) == 0:
            amount = self._rand()
            return [Demand(Naming.name_demand(article.id), article.id, amount)]
        else:
            return []

# Data Building ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def _build_mapping_instance(
        instance: ProblemInstance,
        production_builder: ProductionBuilder,
        provider_builder: ProviderBuilder,
        demand_builder: DemandBuilder,
        ) -> MappingInstance:
    instance_graph = build_instance_graph(instance, ignore_dummy_jobs=True)
    jobs_ordered = nx.topological_sort(instance_graph)
    articles_by_job_id = {}

    for builder in (production_builder, provider_builder, demand_builder):
        builder.init(instance, instance_graph, articles_by_job_id)

    articles, article_productions, providers, demands = [], [], [], []
    for job_id in jobs_ordered:
        article_id = Naming.name_article(job_id)
        job = instance.jobs_by_id[job_id]
        article = Article(article_id)
        articles_by_job_id[job.id] = article

        articles.append(article)
        article_productions.append(production_builder(article, job))
        providers.extend(provider_builder(article, job))
        demands.extend(demand_builder(article, job))

    return MappingInstance(Naming.name_instance(instance.name), articles, demands, providers, article_productions)
