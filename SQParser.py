import random

from SQPYErrors import IncorrectSQPYError, SQLError
from Format_SQPY import format_defines, format_sql, format_sql_rules
from Entity import Entity
# from EntityPackage import Entities
import FormatFile


# def switched_Section(data: str): return __switched_Section(data)
# def Defined_Section(data: str, Defines: dict): return __Defined_Section(data, Defines)
# def SQL_Section(data: str, Defines: dict): return __SQL_Section(data, Defines)
# def Iterations_Section(data: str, entities: dict): return __Iterations_Section(data, entities)
def fill_foreign_key(entities: dict): return __fill_foreign_key(entities)
def deal_with_foreign_keys(entities: dict, foreign_allowed: bool, foreign_reorder: bool): return __deal_with_foreign_keys(entities, foreign_allowed, foreign_reorder)


def section1_BooleanRules(data: str) -> dict: return __section1_BooleanRules(data)
def section2_DefinedActions(data: str, defines: dict) -> None: return __section2_DefinedActions(data, defines)  # should return None
def section3_SQLSpecifications(data: str, defines: dict) -> tuple[dict, dict]: return __section3_SQLSpecifications(data, defines)
def section4_SQLRules(data: str, entities: dict, booleans: dict) -> None: return __section4_SQLRules(data, entities, booleans)  # should return None
def remove_comments(string: str) -> str: return __remove_comments(string)


def read_input(filename: str):

    file_descriptor = open(filename)
    Defines = format_defines.preDefined()
    file_input = ''

    for line in file_descriptor:
        file_input += line

    file_input = remove_comments(file_input)

    file_input = file_input.split("%%")
    if len(file_input) > 4:
        raise IncorrectSQPYError("Too Many Sections (%%)\n\tPossibly caused by r_gex having %%, try switching it to %\\%")

    booleans = section1_BooleanRules(file_input[0])
    section2_DefinedActions(file_input[1], Defines)
    Entity_Sets, Defines = section3_SQLSpecifications(file_input[2], Defines)
    section4_SQLRules(file_input[3], Entity_Sets, booleans)

    for entity in Entity_Sets:
        Entity_Sets[entity].copy()

    return booleans, Entity_Sets, Defines


def __section1_BooleanRules(data: str):
    booleans = {'foreign': True, 'unique_r_gex_upper': 25000, 'relation_limits': True}
    official_codes = {'true': True, 'false': False}
    for line in data.split("\n"):
        if line == '':
            continue
        try:
            boolean_name, boolean = line.replace(' ', '').split("=")
        except Exception:
            raise IncorrectSQPYError("Incorrect First Section Format Error")
        booleans[boolean_name.lower()] = official_codes.get(boolean.lower(), boolean)
    return booleans


def __section2_DefinedActions(data, defines):
    for line in data.split('\n'):
        line = line.strip()
        if line == '':
            continue
        state, lhs, rhs = format_defines.definedActions(line)
        defines[lhs] = [state, rhs]
    pass


def __section3_SQLSpecifications(data: str, defines):
    # Still got to build the entities
    entity_specs, defines = format_sql.find_entities(data, defines)
    entity_dict = {}
    for entity in entity_specs:
        entity_dict[entity] = Entity.EntityObject(entity, entity_specs[entity][0], entity_specs[entity][1])

        entity_dict[entity].build_entity(defines)
        pass

    return entity_dict, defines


def __section4_SQLRules(data, entities, booleans):
    return format_sql_rules.format_rules(data, entities, booleans)


def __remove_comments(string: str) -> str:
    single_line = False
    multi_line = 0
    new_string = ''

    ptr = 0
    while ptr < len(string):

        if single_line and string[ptr] == '\n':
            single_line = False
            # new_string += string[ptr]

        elif multi_line > 0 and string[ptr: ptr + 2] == '*/':
            multi_line -= 1
            ptr += 1

        elif multi_line == 0 and string[ptr:ptr + 2] == '--':
            single_line = True
            ptr += 1

        elif not single_line and string[ptr:ptr + 2] == '/*':
            multi_line += 1
            ptr += 1

        elif not single_line and multi_line == 0:
            new_string += string[ptr]

        ptr += 1

    return new_string


def __fill_foreign_key(entities):
    list_keys = list(entities.keys())

    for num, entity in enumerate(entities):
        for index, entity_sib in enumerate(entities[entity].entity_siblings):
            for attribute in entity_sib.attributes:
                __fill_foreign_keys_non_primary(entities[entity], entity_sib, attribute, entities, entity, list_keys, index)

            __fill_foreign_keys_primary(entities[entity], entity_sib, entities, entity, list_keys, index)

            pass


def find_most_suitable_entry(entity_of_foreign, attribute, entity, name):
    entities_in_range = []
    for ent in entity:
        look_up_code = (ent.limits.get(entity_of_foreign.name, [-1, -1, -1]), ent.limits.get(entity_of_foreign.name + '.' + attribute, [-1, -1, -1]), ent.limits.get('.' + attribute, [-1, -1, -1]))
        largest = (max(look_up_code, key=lambda x: x[0])[0], max(look_up_code, key=lambda x:  x[1])[1], max(look_up_code, key=lambda x:  x[2])[2])

        if max(largest) == -1:
            return random.choice(entity)

        if largest[2] < largest[0]:
            look_up_code[0][2], look_up_code[1][2], look_up_code[2][2] = look_up_code[0][2] + 1, look_up_code[1][2] + 1, look_up_code[2][2] + 1  # should increase them all by 1, however only those that are actually stored get saved
            return ent
        if largest[2] < largest[1]:
            entities_in_range.append(ent)

    if len(entities_in_range) == 0:
        raise IncorrectSQPYError(f"Ran out of entities to act as foreign keys. {name} -> {entity_of_foreign.name}")
    choice = random.choice(entities_in_range)
    look_up_code = (choice.limits.get(entity_of_foreign.name, [-1, -1, -1]), choice.limits.get(entity_of_foreign.name + '.' + attribute, [-1, -1, -1]), choice.limits.get('.' + attribute, [-1, -1, -1]))
    look_up_code[0][2], look_up_code[1][2], look_up_code[2][2] = look_up_code[0][2] + 1, look_up_code[1][2] + 1, look_up_code[2][2] + 1
    return choice


def __fill_foreign_keys_non_primary(siblings, entity_sib, attribute, entities, entity, list_keys, index):
    if entity_sib.attributes[attribute].is_foreign():
        foreign_values = entity_sib.attributes[attribute].get_foreign()
        index_foreign = list_keys.index(foreign_values[0]) if foreign_values[0] in list_keys else -1
        index_self = list_keys.index(entities[entity].name) if entities[entity].name in list_keys else -1

        if index_foreign < index_self:

            foreign_entity = entities[foreign_values[0]]
            choice = find_most_suitable_entry(entity_sib, foreign_values[1], foreign_entity.entity_siblings, foreign_entity.name)
            entity_sib.attributes[attribute].set_value(choice.attributes[foreign_values[1]] if foreign_values[1] in choice.attributes else choice.primary_attributes[foreign_values[1]])
            # if entity_sib.attributes[attribute] == 'null':
            #     pass  # Not sure why I wrote this part, so I am leaving it here in case I actually had a reason

        elif index_foreign == index_self:

            try:
                choice = find_most_suitable_entry(entity_sib, foreign_values[1], siblings.entity_siblings[:index], entity_sib.name)
                entity_sib.attributes[attribute].set_value(choice.attributes[foreign_values[1]] if foreign_values[1] in choice.attributes else choice.primary_attributes[foreign_values[1]])
            except IncorrectSQPYError:
                entity_sib.attributes[attribute].set_value('null')

        else:
            entity_sib.attributes[attribute].set_value('null')


def __check_primary_usability(choices, entity, choices_attributes):
    temp_call_string = ','.join(choices_attributes)
    used_set = entity.used_sets.get(temp_call_string, [])
    if choices not in used_set:
        used_set.append(choices)
        entity.used_sets[temp_call_string] = used_set
        return choices
    return None


def __fill_foreign_keys_primary(siblings, entity_sib, entities, entity, list_keys, index):
    iterations = 0
    while True:
        choices = []
        choices_attributes = []
        for attribute in entity_sib.primary_attributes:
            if entity_sib.primary_attributes[attribute].is_foreign():
                foreign_values = entity_sib.primary_attributes[attribute].get_foreign()
                index_foreign = list_keys.index(foreign_values[0]) if foreign_values[0] in list_keys else -1
                index_self = list_keys.index(entities[entity].name) if entities[entity].name in list_keys else -1
                if index_foreign < index_self:

                    foreign_entity = entities[foreign_values[0]]
                    choices.append(find_most_suitable_entry(entity_sib, foreign_values[1], foreign_entity.entity_siblings, foreign_entity.name))
                    choices_attributes.append(foreign_values[0])

                elif index_foreign == index_self:

                    try:
                        choices.append(find_most_suitable_entry(entity_sib, foreign_values[1], siblings.entity_siblings[:index], entity_sib.name))
                    except IncorrectSQPYError:
                        choices.append(entity_sib.attributes[attribute].set_value('null'))

                else:
                    choices.append(entity_sib.attributes[attribute].set_value('null'))
            else:
                return
        if __check_primary_usability(choices, siblings, choices_attributes) is not None:
            num = 0
            for attribute in entity_sib.primary_attributes:
                if entity_sib.primary_attributes[attribute].is_foreign():
                    foreign_values = entity_sib.primary_attributes[attribute].get_foreign()
                    entity_sib.primary_attributes[attribute].set_value(choices[num].primary_attributes[foreign_values[1]] if foreign_values[1] in choices[num].primary_attributes else choices[num].primary_attributes[foreign_values[1]])
                    num += 1
            return
        else:
            iterations += 1
            if iterations >= 25000:
                raise RecursionError(f"{siblings.name} Primary Key has exceeded the number of iterations allotted and has been deemed a near infinite loop and been terminated")


def __chosen_entity(self_entity, att_name, foreign_values, entity):
    if foreign_values[1] in entity.primary_attributes:
        return entity.primary_attributes[foreign_values[1]].value

    elif foreign_values[1] in entity.attributes:
        if entity.attributes[foreign_values[1]].unique:
            return entity.attributes[foreign_values[1]].value

        else:
            raise SQLError(f"Foreign Key({self_entity}.{att_name}) referencing a non UNIQUE Key ({entity.name}.{foreign_values[1]})")

    else:
        raise SQLError(f"Foreign Key {self_entity.name}.{att_name} references {foreign_values[1]} in {foreign_values[0]} however, {foreign_values[0]} was not found")


def __deal_with_foreign_keys(entities, foreign_allowed, foreign_reorder):
    if foreign_allowed:
        if foreign_reorder:
            entities = FormatFile.set_order_friendly_to_foreign_keys(entities)
        __fill_foreign_key(entities)
    return entities


def main(arg1=None, arg2=None):
    # read_file, write_file = getArgFiles(arg1, arg2)
    # checkFile(read_file)
    # booleans, entities, defines = parse(read_file)
    # for entity in entities:
    #     entities[entity].build_line(defines)
    # entities = deal_with_foreign_keys(entities, booleans.get('foreign', True))
    #
    # FormatFile.write_file(entities, write_file)
    # read_input()
    pass


if __name__ == '__main__':
    main()
