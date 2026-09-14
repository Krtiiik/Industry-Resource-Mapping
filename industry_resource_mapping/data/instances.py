import typing
from dataclasses import dataclass

from industry_resource_mapping.data.entities import (
    Article,
    ArticleProduction,
    Demand,
    Job,
    Precedence,
    Provider,
    T_ArticleId,
    T_ArticleProductionId,
    T_DemandId,
    T_JobId,
    T_ProviderId,
)
from industry_resource_mapping.data.utils import hidden_field
from industry_resource_mapping.utils import groupby

# Mapping ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dataclass
class MappingInstance:
    name: str
    articles: typing.Collection[Article]
    demands: typing.Collection[Demand]
    providers: typing.Collection[Provider]
    article_productions: typing.Collection[ArticleProduction]

    _data_built: bool = hidden_field(default=False)
    _articles_by_id: typing.Mapping[T_ArticleId, Article] = hidden_field()
    _demands_by_id: typing.Mapping[T_DemandId, Demand] = hidden_field()
    _providers_by_id: typing.Mapping[T_ProviderId, Provider] = hidden_field()
    _article_productions_by_id: typing.Mapping[T_ArticleProductionId, ArticleProduction] = hidden_field()
    _article_productions_by_article: typing.Mapping[T_ArticleId, ArticleProduction] = hidden_field()

    def __init__(self, name: str,
                 articles: typing.Collection[Article],
                 demands: typing.Collection[Demand],
                 providers: typing.Collection[Provider],
                 article_productions: typing.Collection[ArticleProduction],
                 build_data: bool = False):
        self.name = name
        self.articles = articles
        self.demands = demands
        self.providers = providers
        self.article_productions = article_productions

        if build_data:
            self._build_data_if_needed()

    @property
    def articles_by_id(self) -> typing.Mapping[T_ArticleId, Article]:
        self._build_data_if_needed()
        return self._articles_by_id

    @property
    def demands_by_id(self) -> typing.Mapping[T_DemandId, Demand]:
        self._build_data_if_needed()
        return self._demands_by_id

    @property
    def providers_by_id(self) -> typing.Mapping[T_ProviderId, Provider]:
        self._build_data_if_needed()
        return self._providers_by_id

    @property
    def article_productions_by_id(self) -> typing.Mapping[T_ArticleProductionId, ArticleProduction]:
        self._build_data_if_needed()
        return self._article_productions_by_id

    @property
    def article_productions_by_article(self) -> typing.Mapping[T_ArticleId, ArticleProduction]:
        # TODO this might need to be a collection, however, for starters, a single production is assumed
        self._build_data_if_needed()
        return self._article_productions_by_article

    def _build_data_if_needed(self):
        if self._data_built:
            return

        self._articles_by_id = {article.id: article for article in self.articles}
        self._demands_by_id = {demand.id: demand for demand in self.demands}
        self._providers_by_id = {provider.id: provider for provider in self.providers}
        self._article_productions_by_id = {a_production.id: a_production for a_production in self.article_productions}
        self._article_productions_by_article = {a_production.article: a_production
                                                for a_production in self.article_productions}
        self._data_built = True

# Scheduling ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SchedulingInstance:
    name: str
    articles: typing.Collection[Article]
    jobs: typing.Collection[Job]
    precedences: typing.Collection[Precedence]

    _data_built: bool = hidden_field(default=False)
    _articles_by_id: typing.Mapping[T_ArticleId, Article] = hidden_field()
    _jobs_by_id: typing.Mapping[T_JobId, Job] = hidden_field()
    _precedences_by_predecessor: typing.Mapping[T_JobId, typing.Collection[Precedence]] = hidden_field()
    _precedences_by_successor: typing.Mapping[T_JobId, typing.Collection[Precedence]] = hidden_field()

    def __init__(self, name: str,
                 articles: typing.Collection[Article],
                 jobs: typing.Collection[Job],
                 precedences: typing.Collection[Precedence],
                 build_data: bool = False):
        self.name = name
        self.articles = articles
        self.jobs = jobs
        self.precedences = precedences

        if build_data:
            self._build_data_if_needed()

    @property
    def articles_by_id(self) -> typing.Mapping[T_ArticleId, Article]:
        self._build_data_if_needed()
        return self._articles_by_id

    @property
    def jobs_by_id(self) -> typing.Mapping[T_JobId, Job]:
        self._build_data_if_needed()
        return self._jobs_by_id

    @property
    def precedences_by_predecessor(self) -> typing.Mapping[T_JobId, typing.Collection[Precedence]]:
        self._build_data_if_needed()
        return self._precedences_by_predecessor

    @property
    def precedences_by_successor(self) -> typing.Mapping[T_JobId, typing.Collection[Precedence]]:
        self._build_data_if_needed()
        return self._precedences_by_successor

    def _build_data_if_needed(self):
        if self._data_built:
            return

        self._articles_by_id = {article.id: article for article in self.articles}
        self._jobs_by_id = {job.id: job for job in self.jobs}
        self._precedences_by_predecessor = groupby(self.precedences, lambda p: p.predecessor)
        self._precedences_by_successor = groupby(self.precedences, lambda p: p.successor)
        self._data_built = True

    @classmethod
    def from_mapping_result(cls, mapping_result: MappingInstance) -> "SchedulingInstance":
        from industry_resource_mapping.data.building import build_scheduling_instance_from_mapping_result
        return build_scheduling_instance_from_mapping_result(mapping_result)
