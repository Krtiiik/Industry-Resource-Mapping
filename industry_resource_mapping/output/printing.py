from industry_resource_mapping.instances.data import MappingResult


def print_mapping_result(mapping_result: MappingResult):
    print("Mapping Result")
    print("Instance", mapping_result.instance.name)
    print("Demands")
    for demand in mapping_result.demands:
        print("\t", demand)
    print("Providers")
    for provider in mapping_result.providers:
        print("\t", provider)
    print("Mappings")
    for mapping in mapping_result.mappings:
        print("\t", mapping)