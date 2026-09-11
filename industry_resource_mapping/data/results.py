from dataclasses import dataclass
import typing

from industry_resource_mapping.data.entities import Demand, Mapping, Provider, T_ArticleProductionId, T_DemandId, T_JobId, T_ProviderId, T_Time
from industry_resource_mapping.data.instances import MappingInstance, SchedulingInstance
from industry_resource_mapping.data.utils import hidden_field
from industry_resource_mapping.utils import groupby


# Mapping ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dataclass
class MappingResult:
    name: str
    instance: MappingInstance
    demands: typing.Collection[Demand]
    providers: typing.Collection[Provider]
    mappings: typing.Collection[Mapping]

    _data_built: bool = hidden_field(default=False)
    _demands_by_origin: typing.Mapping[T_ArticleProductionId, typing.Collection[Demand]]
    _providers_by_origin: typing.Mapping[T_ArticleProductionId, typing.Collection[Provider]]
    _demands_origin: typing.Mapping[T_DemandId, T_ArticleProductionId]
    _providers_origin: typing.Mapping[T_ProviderId, T_ArticleProductionId]

    def __init__(self, name: str,
                 instance: MappingInstance,
                 demands: typing.Collection[Demand],
                 providers: typing.Collection[Provider],
                 mappings: typing.Collection[Mapping],
                 build_data: bool = False):
        self.name = name
        self.instance = instance
        self.demands = demands
        self.providers = providers
        self.mappings = mappings

        if build_data:
            self._build_data_if_needed

    @property
    def demands_by_origin(self) -> typing.Mapping[T_ArticleProductionId, typing.Collection[Demand]]:
        self._build_data_if_needed()
        return self._demands_by_origin

    @property
    def providers_by_origin(self) -> typing.Mapping[T_ArticleProductionId, typing.Collection[Provider]]:
        self._build_data_if_needed()
        return self._providers_by_origin

    @property
    def demands_origin(self) -> typing.Mapping[T_DemandId, T_ArticleProductionId]:
        self._build_data_if_needed()
        return self._demands_origin

    @property
    def providers_origin(self) -> typing.Mapping[T_ProviderId, T_ArticleProductionId]:
        self._build_data_if_needed()
        return self._providers_origin

    def _build_data_if_needed(self):
        if self._data_built:
            return

        self._demands_by_origin = groupby(self.demands, lambda d: d.origin)
        self._providers_by_origin = groupby(self.providers, lambda p: p.origin)
        self._demands_origin = {demand.id: demand.origin for demand in self.demands}
        self._providers_origin = {provider.id: provider.origin for provider in self.providers}

        self._data_built = True

# Scheduling ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dataclass
class SchedulingResult:
    name: str
    instance: SchedulingInstance
    job_starts: typing.Mapping[T_JobId, T_Time]
