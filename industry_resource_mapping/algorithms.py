from .instances import Demand, Mapping, MappingInstance, MappingResult, Provider


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
    def new_provider(_article, _amount):
        nonlocal id_providers
        id_providers += 1
        return Provider(construct_id("P", id_providers), _article, _amount)
    def new_demand(_article, _amount):
        nonlocal id_demands
        id_demands += 1
        return Demand(construct_id("D", id_demands), _article, _amount)

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
                push(new_demand(required_article, required_amount))

            # create a provider of the demanded produced article
            provider = new_provider(article, demand.amount)
            providers.append(provider)
            mapping = Mapping(provider.id, demand.id, demand.amount)
            mappings.append(mapping)

        demands_satisfied.append(demand)

    return MappingResult(instance, demands_satisfied, providers, mappings)
