from dataclasses import dataclass
import typing

from psplib_editor.utils import hidden_field


T_ArticleId: typing.TypeAlias = str
T_ProviderId: typing.TypeAlias = str
T_DemandId: typing.TypeAlias = str
T_ArticleProductionId: typing.TypeAlias = str


@dataclass
class Article:
    id: T_ArticleId

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Article):
            return self.id == other.id
        return False


@dataclass
class Provider:
    id: T_ProviderId
    article: T_ArticleId
    amount: int

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Provider):
            return self.id == other.id
        return False


@dataclass
class Demand:
    id: T_DemandId
    article: T_ArticleId
    amount: int

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Demand):
            return self.id == other.id
        return False


@dataclass
class ArticleProduction:
    id: T_ArticleProductionId
    article: T_ArticleId
    requirements: typing.Collection[typing.Tuple[T_ArticleId, int]]
    duration: int

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, ArticleProduction):
            return self.id == other.id
        return False


@dataclass
class MappingInstance:
    name: str
    articles: typing.Collection[Article]
    demands: typing.Collection[Demand]
    providers: typing.Collection[Provider]
    article_productions: typing.Collection[ArticleProduction]

    _data_built: bool = hidden_field(default=False)
    _articles_by_id: typing.Mapping[T_ArticleId, Article] = hidden_field()
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
    def article_productions_by_article(self) -> typing.Mapping[T_ArticleId, ArticleProduction]:
        # TODO this might need to be a collection, however, for starters, a single production is assumed
        self._build_data_if_needed()
        return self._article_productions_by_article

    def _build_data_if_needed(self):
        if self._data_built:
            return

        self._articles_by_id = {article.id: article
                                for article in self.articles}
        self._article_productions_by_article = {a_production.article: a_production
                                                for a_production in self.article_productions}
        self._data_built = True

# Result ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dataclass
class Mapping:
    provider: T_ProviderId
    demand: T_DemandId
    amount: int

    def __hash__(self):
        return hash((self.provider, self.demand))

    def __eq__(self, other):
        if isinstance(other, Mapping):
            # this is enough as we should only want a single mapping between the two
            return (
                self.provider == other.provider
                and self.demand == other.demand
            )


@dataclass
class MappingResult:
    instance: MappingInstance
    demands: typing.Collection[Demand]
    providers: typing.Collection[Provider]
    mappings: typing.Collection[Mapping]
