import typing
from dataclasses import dataclass

T_ArticleId: typing.TypeAlias = str
T_Time: typing.TypeAlias = int

T_ProviderId: typing.TypeAlias = str
T_DemandId: typing.TypeAlias = str
T_ArticleProductionId: typing.TypeAlias = str

T_JobId: typing.TypeAlias = str

# Common ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dataclass
class Article:
    id: T_ArticleId

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Article):
            return self.id == other.id
        return False

# Mapping ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dataclass
class Provider:
    id: T_ProviderId
    article: T_ArticleId
    amount: int
    release_date: T_Time | None = None
    origin: T_ArticleProductionId | None = None

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
    due_date: T_Time | None = None
    origin: T_ArticleProductionId | None = None

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
    requirements: typing.Collection[tuple[T_ArticleId, int]]
    duration: int

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, ArticleProduction):
            return self.id == other.id
        return False


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

# Scheduling ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dataclass
class Job:
    id: T_JobId
    article: T_ArticleId
    duration: int
    due_date: T_Time | None = None


@dataclass
class Precedence:
    predecessor: T_JobId
    successor: T_JobId
