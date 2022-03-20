"""
Need keywords to be all upper so remember ME.
"""
import Grammar
import re

from SQPYErrors import SQLError, SQPYGrammarError


class Entity:
    def __init__(self, entities, name, table, defines):
        self.entities = entities
        self.table = table
        self.attributes = {}
        self.name = name
        self.__parse(defines)
        pass

    def __parse(self, defines):
        for line in self.table:
            self.__full_parse(line, defines)
        pass

    def __full_parse(self, line, defines):
        grammar, line = self.__collect_grammar(line)
        exclusion = ['CREATE', 'TABLE']
        lis = re.findall("(PRIMARY KEY|FOREIGN KEY|[^ ()]+)", line)
        for exclusive in exclusion:
            for event in lis:
                if exclusive == event.upper():
                    raise SQLError(f'{exclusive} found in attribute location')
        ptr = 0
        attr = None
        if lis[0] == 'works_on_professor_id':
            pass
        if lis[0] == 'works_on_graduate_id':
            pass
        if lis[0] == 'works_on_project_id':
            pass
        while ptr < len(lis):
            match lis[ptr]:
                case "PRIMARY KEY" | "UNIQUE":
                    if ptr == 0:
                        self.attributes[lis[1]].unique = True
                        ptr += 1
                    else:
                        self.attributes[lis[0]].unique = True
                case "FOREIGN KEY":
                    if ptr == 0:
                        self.attributes[lis[ptr + 1]].foreign = lis[ptr + 3: ptr + 5]
                        ptr += 3
                    else:
                        self.attributes[lis[0]].foreign = lis[ptr + 2: ptr + 4]
                        ptr += 2
                case _:
                    match ptr:
                        case 0:
                            attr = Attribute(self, lis[ptr])
                            self.attributes[lis[ptr]] = attr
                        case 1:
                            attr.set_type(lis[ptr])
                        case 2:
                            if attr.d_type == "VARCHAR" or attr.d_type == "CHAR":
                                attr.set_VarLength(lis[ptr])
                    pass
            ptr += 1
        if attr is not None:
            attr.setChoice(defines, grammar)

    @staticmethod
    def __collect_grammar(line):
        gex = re.findall("<\\w+>", line)
        if len(gex) > 1:
            raise SQPYGrammarError("Too many choice actions were given for attribute")
        if len(gex) == 0:
            return None, line
        return gex[0].replace('<', '').replace('>', ''), line

    def build_line(self):
        for attribute in self.attributes:
            if self.attributes[attribute].foreign is None:
                self.attributes[attribute].set_value(self.attributes[attribute].getChoice())


class Attribute:
    def __init__(self, entity, name):
        self.entity = entity
        self.name = name
        self.d_type = None
        self.choices = None
        self.__length = 0
        self.unique = False
        self.foreign = None

        self.value = None

    def set_type(self, newType):
        acceptedTypes = ['INT', 'VARCHAR', 'DOUBLE', 'CHAR', 'FLOAT', 'DATE']
        if newType in acceptedTypes:
            self.d_type = newType
        else:
            raise SQLError(f"{newType} is not supported")

    def set_foreign_key(self, foreign_key):
        pass

    def set_VarLength(self, length):
        self.__length = length

    def setChoice(self, defines, grammar):
        if grammar is None:
            self.choices = 'null'
        else:
            self.choices = Grammar.Grammar(self, defines[grammar], defines)

            if self.choices.grammar == 'AUTOINCREMENT':
                self.entity.entities.autoincrement[self.name] = 0

    def getChoice(self):
        return self.choices.getChoice() if isinstance(self.choices, Grammar.Grammar) else self.choices

    def set_value(self, value):
        if value == 'null':
            self.value = value
            return
        match self.d_type:
            case "INT":
                self.value = int(value)
            case "DOUBLE":
                self.value = float(value)
            case _:
                self.value = "'" + value + "'"

    def __str__(self):
        return f"{self.name}: {{type: {self.d_type}, choices: {self.choices}, unique: {self.unique}, foreignInfo: {self.foreign}}}"


def main():
    arr = []
    for line in open('../test.sql'):
        arr.append(line)
    e = Entity(None, 'pass', arr, None)
    # e.__parse(None)


if __name__ == '__main__':
    main()
