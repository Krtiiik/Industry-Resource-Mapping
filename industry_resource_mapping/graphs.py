from typing import Any
import networkx as nx

from .instances.data import MappingResult
from .utils import IdManager


def build_mapping_graph(mapping_result: MappingResult) -> nx.DiGraph:
    """
    Builds a graph for a given mapping result.
    Vertices are providers and demands, edges are mappings from providers to demands.
    TODO
    """
    providers_origin = mapping_result.providers_origin
    demands_origin = mapping_result.demands_origin

    virtual_node_ids = IdManager(lambda id: f"Virtual{str(id)}")
    def virtual_node():
        return virtual_node_ids.new()

    edges = []
    for mapping in mapping_result.mappings:
        provider_origin = providers_origin[mapping.provider]
        demand_origin = demands_origin[mapping.demand]
        n_provider = provider_origin if (provider_origin is not None) else virtual_node()
        n_demand = demand_origin if (demand_origin is not None) else virtual_node()
        edges.append((n_provider, n_demand))

    graph = nx.DiGraph(edges)

    return graph


def is_virtual_node(node: Any) -> bool:
    return isinstance(node, str) and node.startswith("Virtual")
