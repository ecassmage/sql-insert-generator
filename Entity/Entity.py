import re

import Grammar
from SQPYErrors import SQPYGrammarError, IncorrectSQPYError
From Entity import Attribute


def collect_grammar(line): return __collect_grammar(line)


class Entity:
    def __init__(self, name, limits=1):
        self.primary_attributes = {}
        self.attributes = {}
        self.order_of_attributes = []
        self.name = name
        self.limits = {self.name: [-1, limits, 0]}

    def __str__(self):
        return f"INSERT INTO {self.name} VALUES(" + ', '.join([f"{(str(self.primary_attributes[att]) if att in self.primary_attributes else str(self.attributes[att]))}" for att in self.order_of_attributes]) + ");"

    def __str__dep(self):
        return ', '.join([f"{att}: {(str(self.primary_attributes[att]) if att in self.primary_attributes else str(self.attributes[att]))}" for att in self.order_of_attributes])

    def __len__(self):
        return len(self.order_of_attributes)


class EntityObject(Entity):
    def __init__(self, name: str, table: list, limit: int):
        super().__init__(name, 1)
        self.entity_siblings = []
        self.autoincrement = {}

        self.table = table  # contains a blueprint for the construction of the Entity table.
        self.set_copies(limit)
        self.used_sets = {}

    def __str__(self):
        return '\n'.join([f"{str(ent)}" for ent in self.entity_siblings])

    def set_copies(self, number_of_copies: int):            self.limits[self.name] = [-1, number_of_copies, 0]
    def build_entity(self, defines):                        self.__build_entity(defines)  # for line in self.table:
    def add_limit(self, limit_code, limit):                 self.__add_limit(limit_code, limit)
    def copy(self):                                         self.__copy()
    def build_outputs(self): self.__build_outputs()

    def __build_outputs(self):
        for entity_copy in self.entity_siblings:
            self.__build_key_output(entity_copy.attributes)
            self.__build_primary_output(entity_copy.name, entity_copy.primary_attributes)

    def __build_primary_output(self, name, entity: dict, iteration_cap=1000):
        if len(entity) == 1:
            self.__build_key_output(entity)
        else:
            used_set = self.used_sets.get(self.name, [])
            iterations = 0
            foreign_found = False
            while True:
                tuple_of_storage = []  # yes the tuple_of_storage is actually a list...
                for attribute in entity:
                    if entity[attribute].is_foreign():
                        foreign_found = not False
                        entity[attribute].set_value('null')
                        continue
                    tuple_of_storage.append(self.__get_choice(entity[attribute].choice, self.used_sets.get(attribute, None)))
                    if (tuple_of_storage[-1] == 'null' or tuple_of_storage[-1] is None) and not entity[attribute].is_foreign():
                        from SQPYErrors import SQLError
                        raise SQLError("program attempted to store null inside of a primary key")
                if foreign_found:
                    return
                if tuple_of_storage not in used_set:
                    used_set.append(tuple_of_storage)
                    for num, attribute in enumerate(entity):
                        entity[attribute].set_value(tuple_of_storage[num])
                    self.used_sets[self.name] = used_set
                    break
                else:
                    iterations += 1
                    if iterations > iteration_cap:
                        from SQPYErrors import RepeatingPrimaryKeyLoop
                        raise RepeatingPrimaryKeyLoop(f"{name} Primary Key has exceeded the number of iterations allotted and has been deemed a near infinite loop and been terminated")
                pass
            pass

    def __build_key_output(self, entity_dictionary: dict):
        def add_to_used(attr, add_to):
            temp_list = self.used_sets.get(attr, [])
            temp_list.append(add_to)
            self.used_sets[attr] = temp_list
            pass

        for attribute in entity_dictionary:

            if entity_dictionary[attribute].choice is None:
                entity_dictionary[attribute].value = 'null'

            elif not entity_dictionary[attribute].is_foreign():
                entity_dictionary[attribute].set_value(self.__get_choice(entity_dictionary[attribute].choice, self.used_sets.get(attribute, None)))

                if entity_dictionary[attribute].unique:
                    add_to_used(attribute, entity_dictionary[attribute].value)

    @staticmethod
    def __get_choice(choice_machine, used_set):

        return 'null' if choice_machine is None else choice_machine.getChoice(used_set)

    def __build_entity(self, defines):

        attribute_temp_list = {}
        for attribute in self.table:
            ptr = 0
            attr = None
            while ptr < len(attribute):
                match attribute[ptr].upper():
                    case "PRIMARY KEY":
                        if self.__primary_key_build_entity_case(attribute_temp_list, attribute, ptr):
                            break

                    case "UNIQUE":
                        temp_att = attribute_temp_list[attribute[1]] if ptr == 0 else attribute_temp_list[attribute[0]]
                        ptr += 1 if ptr == 0 else 0

                        temp_att.unique = True

                    case "FOREIGN KEY":
                        temp_att = attribute_temp_list[attribute[1]] if ptr == 0 else attribute_temp_list[attribute[0]]
                        ptr += 1 if ptr == 0 else 0

                        temp_att.set_foreign(attribute[ptr+2:ptr+4])
                        ptr += 2

                    case "NOT NULL":
                        attribute_temp_list[attribute[0]].null = False

                    case "CONSTRAINT":
                        # shouldn't be found cause I am lazy and Don't want to deal with constraint at the moment
                        pass
                    case _:
                        attribute_temp_list, attr = self.__default_build_entity_case(attribute_temp_list, attr, attribute, ptr, defines)
                ptr += 1
        self.__allocate_entity_hierarchy(attribute_temp_list)

    def __copy(self):
        def get_copy_of_attributes(attr):
            return {attr[att].name: attr[att].copy() for att in attr}

        from copy import deepcopy
        for _ in range(self.limits[self.name][1]):
            ent = Entity(self.name)
            ent.order_of_attributes = self.order_of_attributes
            ent.primary_attributes = get_copy_of_attributes(self.primary_attributes)
            ent.attributes = get_copy_of_attributes(self.attributes)
            ent.limits = deepcopy(self.limits)
            self.entity_siblings.append(ent)
        pass

    def __allocate_entity_hierarchy(self, attribute_set):
        for attribute in attribute_set:
            self.order_of_attributes.append(attribute)
            if attribute_set[attribute].primary:
                self.primary_attributes[attribute] = attribute_set[attribute]
            else:
                self.attributes[attribute] = attribute_set[attribute]

    @staticmethod
    def __primary_key_build_entity_case(attribute_temp_list, attribute, ptr):
        if ptr == 0:
            for index in range(1, len(attribute)):
                attribute_temp_list[attribute[index]].primary = True
                attribute_temp_list[attribute[index]].null = False
            return True

        attribute_temp_list[attribute[0]].primary = True
        attribute_temp_list[attribute[0]].null = False
        return False

    def __default_build_entity_case(self, attribute_temp_list, attr, attribute, ptr, defines):
        def check_define(define):
            return define[0] == '<' and define[-1] == '>'

        if check_define(attribute[ptr]):
            attr.choice = Grammar.Grammar(self, attr, defines[attribute[ptr].replace("<", '').replace(">", '')])

        else:
            match ptr:
                case 0:
                    attr = Attribute.Attribute(attribute[ptr])
                    attribute_temp_list[attribute[ptr]] = attr
                case 1:
                    attr.set_type(attribute[ptr])
                case 2:
                    if attr.type == "VARCHAR" or attr.type == "CHAR":
                        attr.set_VarLength(attribute[ptr])
        return attribute_temp_list, attr

    def __add_limit(self, limit_code, limit: tuple[str, int, int]):
        try:
            hash_name = (limit[0] if limit[0] is not None else '') + ('.' + limit_code[1] if len(limit_code) > 1 else '')
            self.limits[hash_name] = [limit[1], limit[2], 0]
        except Exception:
            lhs = ''.join([f'.{line}' if num > 0 else line for num, line in enumerate(limit_code)])
            rhs = f'{str(limit[0]) if limit[0] is not None else ""}({(str(limit[1]) + ", ") if limit[1] > -1 else "" }{str(limit[2])})'
            raise IncorrectSQPYError(f"Incorrect Limit in Section 4: {lhs} -> {rhs};")
        pass


def __collect_grammar(line):
    gex = re.findall("<\\w+>", line)
    if len(gex) > 1:
        raise SQPYGrammarError("Too many choice actions were given for attribute")
    if len(gex) == 0:
        return None, line
    return gex[0].replace('<', '').replace('>', ''), line
