import abc
from collections import defaultdict, deque
from collections.abc import Collection, Iterable
from dataclasses import dataclass
from typing import ClassVar

from industry_resource_mapping.data import Article, Demand, Mapping, MappingInstance, MappingResult, Provider
from industry_resource_mapping.data.entities import T_ArticleId, T_ArticleProductionId
from industry_resource_mapping.utils import IdManager

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

    def __call__(self, instance: MappingInstance):
        return self.solve(instance)

# Iterative ------------------------------------------------------------------------------------------------------------

@dataclass
class ProviderAmount:
    provider: Provider
    amount: int

    def __iter__(self):
        yield self.provider
        yield self.amount


class IterativeMappingAlgorithm(MappingAlgorithm):
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

class IterativeMappingAlgorithmIgnoringExistingProviders(IterativeMappingAlgorithm):
    def _find_providers(self, article, amount):
        return [], amount  # Ignoring existing providers
