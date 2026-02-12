import abc
from collections import defaultdict, deque, namedtuple
from dataclasses import dataclass
from typing import Callable, ClassVar, Collection, Generator, Iterable, TypeAlias

from .instances import Article, Demand, Mapping, MappingInstance, MappingResult, Provider, T_ArticleId, T_ArticleProductionId


def _plan_name(instance_name: str, fmt: str = None):
    if fmt is None:
        fmt = "{instance_name}.plan"
    return fmt.format(instance_name, instance_name=instance_name)


def plan_production_ignoring_existing(instance: MappingInstance) -> MappingResult:
    # Assuming no other plan-ids are present
    id_prefix = "[Plan]"
    id_demands = 0
    id_providers = 0
    demands = list(instance.demands)  # TODO priority queue based on demand properties

    def pop(): return demands.pop()
    def push(_demand): demands.append(_demand)
    def not_empty(): return len(demands) > 0
    def construct_id(_prefix, _id):
        return f"{id_prefix}{_prefix}{_id}"
    def new_provider(_article, _amount, _article_production):
        nonlocal id_providers
        id_providers += 1
        return Provider(construct_id("P", id_providers), _article, _amount, _article_production)
    def new_demand(_article, _amount, _article_production):
        nonlocal id_demands
        id_demands += 1
        return Demand(construct_id("D", id_demands), _article, _amount, _article_production)

    demands_satisfied = []
    providers = []
    mappings = []
    while not_empty():
        demand = pop()
        article = demand.article

        article_production = instance.article_productions_by_article.get(article, None)
        if article_production is None:
            # we ignore existing providers or other forms of providing articles than production, for now
            pass
        else:  # article production exists
            # create demands for required articles
            for requirement in article_production.requirements:
                required_article, required_amount = requirement
                required_amount *= demand.amount
                push(new_demand(required_article, required_amount, article_production.id))

            # create a provider of the demanded produced article
            provider = new_provider(article, demand.amount, article_production.id)
            providers.append(provider)
            mapping = Mapping(provider.id, demand.id, demand.amount)
            mappings.append(mapping)

        demands_satisfied.append(demand)

    return MappingResult(_plan_name(instance.name), instance, demands_satisfied, providers, mappings)

# Utils ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

# Errors ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MappingError(Exception):
    """
    Common base class for all mapping-related exceptions.
    """
    def __init__(self, instance: MappingInstance, *args):
        super().__init__(*args)
        self.instance = instance


class UndefinedProductionError(MappingError):
    """
    Raised when a production is required for an article but none is defined in the mapping instance.
    """
    def __init__(self, instance: MappingInstance, article: Article, *args):
        super().__init__(instance, "Mapping instance is missing defined production for a required article.")
        self.article = article

# Algorithms ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MappingAlgorithm(abc.ABC):
    gen_id: ClassVar[str] = "[Gen]"

    def __init__(self):
        super().__init__()
        self._demand_id_manager = IdManager((f"{self.gen_id}D-{{}}").format)
        self._provider_id_manager = IdManager((f"{self.gen_id}P-{{}}").format)

    def solve(self, instance: MappingInstance) -> MappingResult:
        self._init(instance)
        result = self._solve(instance)
        return result

    def _init(self, instance: MappingInstance):
        self._instance = instance
        self._demand_id_manager.reset()
        self._provider_id_manager.reset()

    @abc.abstractmethod
    def _solve(self, instance: MappingInstance) -> MappingResult:
        ...

    def _new_demand(self, article_id: T_ArticleId, amount: int, origin: T_ArticleProductionId=None) -> Demand:
        return Demand(id=self._demand_id_manager.new(), article=article_id, amount=amount, origin=origin)

    def _new_provider(self, article_id: T_ArticleId, amount: int, origin: T_ArticleProductionId=None) -> Provider:
        return Provider(id=self._provider_id_manager.new(), article=article_id, amount=amount, origin=origin)

    def _construct_result(self,
                          demands: Collection[Demand], providers: Collection[Provider], mappings: Collection[Mapping]
                          ) -> MappingResult:
        return MappingResult(
            name=self._name_result(), instance=self._instance,
            demands=demands, providers=providers, mappings=mappings,
        )

    def _name_result(self) -> str:
        return f"{self._instance.name}.plan"

# Iterative ------------------------------------------------------------------------------------------------------------

@dataclass
class ProviderAmount:
    provider: Provider
    amount: int

    def __iter__(self):
        yield self.provider
        yield self.amount


class Iterative(MappingAlgorithm):
    def __init__(self):
        super().__init__()
        self._demands_to_satisfy: deque[Demand] = None
        self._unmapped_providers: defaultdict[T_ArticleId, list[ProviderAmount]] = None

    def _init(self, instance):
        super()._init(instance)
        self._demands_to_satisfy = deque(instance.demands)
        self._unmapped_providers = defaultdict(list)
        for provider in instance.providers:
            self._unmapped_providers[provider.article].append(ProviderAmount(provider, provider.amount))

    def _q_empty(self) -> bool:
        return len(self._demands_to_satisfy) == 0

    def _q_pop(self) -> Demand:
        return self._demands_to_satisfy.popleft()

    def _q_push(self, demand: Demand):
        self._demands_to_satisfy.append(demand)

    def _find_providers(self, article: T_ArticleId, amount: int) -> tuple[Iterable[ProviderAmount] | None, int]:
        unmapped_providers = self._unmapped_providers[article]
        if not unmapped_providers:
            return [], amount

        needed_providers = []
        amount_remaining = amount
        while unmapped_providers and amount_remaining > 0:
            unmapped_provider = unmapped_providers[-1]
            if amount_remaining < unmapped_provider.amount:
                needed_providers.append(ProviderAmount(unmapped_provider.provider, amount_remaining))
                unmapped_provider.amount -= amount_remaining
                amount_remaining = 0
            else:
                needed_providers.append(unmapped_provider)
                unmapped_providers.pop()
                amount_remaining -= unmapped_provider.amount

        return needed_providers, amount_remaining

    def _generate_production(self, article: T_ArticleId, amount: int) -> Iterable[ProviderAmount]:
        article_production = self._instance.article_productions_by_article.get(article, None)

        if article_production is None:
            raise UndefinedProductionError(self._instance, article)

        # create demands for required articles
        for requirement in article_production.requirements:
            required_article, required_amount = requirement
            required_amount *= amount
            self._q_push(self._new_demand(required_article, required_amount, article_production.id))

        # create a provider of the demanded produced article
        provider = self._new_provider(article, amount, article_production.id)
        return [ProviderAmount(provider, provider.amount)]

    def _map_demand_providers(self, demand: Demand, providers: Iterable[ProviderAmount]) -> list[Mapping]:
        mappings = []
        for provider, amount in providers:
            mappings.append(Mapping(provider.id, demand.id, amount))
        return mappings

    def _solve(self, instance):
        demands = []
        providers = []
        mappings = []
        while not self._q_empty():
            demand = self._q_pop()
            article = demand.article

            demand_mappings = []

            # Map existing providers
            providers_existing, amount_not_provided = self._find_providers(article, demand.amount)
            if providers_existing:
                demand_mappings.extend(self._map_demand_providers(demand, providers_existing))
                providers.extend(provider for provider, _ in providers_existing)

            if amount_not_provided > 0:
                # Generate new providers
                providers_generated = self._generate_production(article, amount_not_provided)
                demand_mappings.extend(self._map_demand_providers(demand, providers_generated))
                providers.extend(provider for provider, _ in providers_generated)

            assert sum(m.amount for m in demand_mappings) == demand.amount

            demands.append(demand)
            mappings.extend(demand_mappings)

        return self._construct_result(demands, providers, mappings)

# Iterative Ignoring Existing Providers --------------------------------------------------------------------------------

class IterativeIgnoringExistingProviders(Iterative):
    def _find_providers(self, article, amount):
        return [], amount  # Ignoring existing providers
