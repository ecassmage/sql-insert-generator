def write_file(entities, file):
    file_writer = open(file, 'w')
    for entity_set in entities:
        for entity in entities[entity_set].entities:
            string = f'INSERT INTO {entity.name} VALUES('
            for num, attribute in enumerate(entity.attributes):
                if num > 0:
                    string += ', '
                string += str(entity.attributes[attribute].value) if entity.attributes[attribute].value is not None else 'null'
            string += ');'
            file_writer.write(string + '\n')
        file_writer.write('\n')
    file_writer.close()


def set_foreign(entities, boolean):
    if not boolean:
        return entities
    entity_list_ordered = []
    new_ordered_entity_list = {}
    for entity_set in entities:
        for entity in entities[entity_set].entities:
            if len(entities[entity_set].entities) == 0:
                continue
            if entity.name not in entity_list_ordered:
                entity_list_ordered.append(entity.name)
            for attribute in entity.attributes:
                if entity.attributes[attribute].foreign is not None:

                    index_foreign = entity_list_ordered.index(entity.attributes[attribute].foreign[0]) if entity.attributes[attribute].foreign[0] in entity_list_ordered else -1
                    index_self = entity_list_ordered.index(entity.name) if entity.name in entity_list_ordered else -1
                    if index_foreign == -1:
                        entity_list_ordered.insert(index_self, entity.attributes[attribute].foreign[0])
                    elif index_foreign > index_self:
                        entity_list_ordered.pop(index_foreign)
                        entity_list_ordered.insert(index_self, entity.attributes[attribute].foreign[0])
            break
    for key in entity_list_ordered:
        new_ordered_entity_list[key] = entities[key]
    return new_ordered_entity_list

