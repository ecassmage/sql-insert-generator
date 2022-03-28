def set_order_friendly_to_foreign_keys(entities): return __set_order_friendly_to_foreign_keys(entities)


def __set_order_friendly_to_foreign_keys(entities):
    entity_list_ordered = []
    new_ordered_entity_list = {}

    for entity in entities:

        if len(entities[entity].entity_siblings) == 0:
            continue
        if entities[entity].name not in entity_list_ordered:
            entity_list_ordered.append(entities[entity].name)

        for attribute in entities[entity].attributes:

            if entities[entity].attributes[attribute].is_foreign():
                foreign_values = entities[entity].attributes[attribute].get_foreign()
                index_foreign = entity_list_ordered.index(foreign_values[0]) if foreign_values[0] in entity_list_ordered else -1
                index_self = entity_list_ordered.index(entities[entity].name) if entities[entity].name in entity_list_ordered else -1

                if index_foreign == -1:
                    entity_list_ordered.insert(index_self, foreign_values[0])

                elif index_foreign > index_self:
                    entity_list_ordered.pop(index_foreign)
                    entity_list_ordered.insert(index_self, foreign_values[0])

            pass
    for key in entity_list_ordered:
        new_ordered_entity_list[key] = entities[key]
    return new_ordered_entity_list
