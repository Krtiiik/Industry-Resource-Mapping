from typing import Any
import networkx as nx

from .instances.data import Demand, MappingResult, Provider
from .utils import IdManager


def build_mapping_graph(mapping_result: MappingResult) -> nx.DiGraph:
    """
    Builds a graph for a given mapping result.
    Vertices are providers and demands, edges are mappings from providers to demands.
    TODO
    """
    providers_origin = mapping_result.providers_origin
    demands_origin = mapping_result.demands_origin

    virtual_nodes = {}
    virtual_node_ids = IdManager(lambda id: f"Virtual{str(id)}")
    def virtual_node(provider: Provider = None, demand: Demand = None) -> str:
        new = virtual_node_ids.new()
        virtual_nodes[new] = (provider, demand)
        return new

    edges = []
    for mapping in mapping_result.mappings:
        provider_origin = providers_origin[mapping.provider]
        demand_origin = demands_origin[mapping.demand]
        n_provider = provider_origin if (provider_origin is not None) else virtual_node(provider=mapping.provider)
        n_demand = demand_origin if (demand_origin is not None) else virtual_node(demand=mapping.demand)
        edges.append((n_provider, n_demand, mapping))

    graph = nx.DiGraph()
    for edge in edges:
        graph.add_edge(edge[0], edge[1], mapping=edge[2])
    graph.graph["virtual_nodes"] = virtual_nodes

    return graph


def is_virtual_node(node: Any) -> bool:
    return isinstance(node, str) and node.startswith("Virtual")
