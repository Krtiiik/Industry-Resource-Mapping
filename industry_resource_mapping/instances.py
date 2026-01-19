from dataclasses import dataclass
from typing import Collection, Mapping, Tuple, TypeAlias

from psplib_editor.utils import hidden_field


T_ArticleId: TypeAlias = str
T_ProviderId: TypeAlias = str
T_DemandId: TypeAlias = str
T_ArticleProductionId: TypeAlias = str


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
    requirements: Collection[Tuple[T_ArticleId, int]]
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
    articles: Collection[Article]
    demands: Collection[Demand]
    providers: Collection[Provider]
    article_productions: Collection[ArticleProduction]

    _data_built: bool = hidden_field(default=False)
    _articles_by_id: Mapping[T_ArticleId, Article] = hidden_field()
    _article_productions_by_article: Mapping[T_ArticleId, ArticleProduction] = hidden_field()

    def __init__(self, name: str,
                 articles: Collection[Article],
                 demands: Collection[Demand],
                 providers: Collection[Provider],
                 article_productions: Collection[ArticleProduction],
                 build_data: bool = False):
        self.name = name
        self.articles = articles
        self.demands = demands
        self.providers = providers
        self.article_productions = article_productions

        if build_data:
            self._build_data_if_needed()

    @property
    def articles_by_id(self) -> Mapping[T_ArticleId, Article]:
        self._build_data_if_needed()
        return self._articles_by_id

    def productions_for_article(self) -> Mapping[T_ArticleId, Collection[ArticleProduction]]:
        self._build_data_if_needed()
        return self._article_productions_by_article

    def _build_data_if_needed(self):
        if self._data_built:
            return

        self._articles_by_id = {article.id: article for article in self.articles}
        self._data_built = True
