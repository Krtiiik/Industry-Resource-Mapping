from typing import Any
import networkx as nx

from .instances.data import MappingResult


def build_mapping_graph(mapping_result: MappingResult) -> nx.DiGraph:
    """
    Builds a graph for a given mapping result.
    Vertices are 
    """
    providers_origin = mapping_result.providers_origin
    demands_origin = mapping_result.demands_origin

    virtual_node_counter = 0
    def virtual_node():
        nonlocal virtual_node_counter
        virtual_node_counter -= 1
        return virtual_node_counter

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
    return isinstance(node, int) and node < 0
