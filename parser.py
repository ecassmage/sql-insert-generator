import re
import sys
import os
import random

from SQPYErrors import TooManyArgumentsError, IncorrectSQPYError, IncorrectFileError
import FormatFile
from EntityPackage import Entities
states = {'special': -1, 'file': 0, 'array': 1, 'r_gex': 2}
customPtr = 10


def getArgFiles(arg1, arg2):
    if len(sys.argv) > 3:
        raise TooManyArgumentsError
    read_file = sys.argv[1] if len(sys.argv) > 1 else None
    write_file = sys.argv[2] if len(sys.argv) > 2 else None

    if read_file is None:
        if os.path.isfile(arg1):
            read_file = arg1
        else:
            exit()

    if write_file is None:
        write_file = arg2 if arg2 is not None else 'output.sql'
    return read_file, write_file


def checkFile(file):
    if not file.endswith(".sqpy"):
        raise IncorrectFileError(file)


def preDefined():
    def preDefined_SQL():
        definedLists['0'] = [states['special'], "AUTOINCREMENT"]

    definedLists = {None: None}
    if os.path.isfile('Defined_Files\\fname.txt'):
        definedLists['fname'] = [states['array'], [line.strip() for line in open('Defined_Files\\fname.txt')]]
    if os.path.isfile('Defined_Files\\lname.txt'):
        definedLists['lname'] = [states['array'], [line.strip().capitalize() for line in open('Defined_Files\\lname.txt')]]
    if os.path.isfile('Defined_Files\\hospital_names.txt'):
        definedLists['hospital_names'] = [states['array'], [line.strip() for line in open('Defined_Files\\hospital_names.txt')]]
    if os.path.isfile('Defined_Files\\street_names.txt'):
        definedLists['street_names'] = [states['array'], [line.strip() for line in open('Defined_Files\\street_names.txt')]]

    preDefined_SQL()
    return definedLists


def definedActions(string, lhsReturn=True):
    """
    file = "{.+}"
    array = "[.+]"
    r_gex = ".+"
    """

    def get_file(arg):
        file = re.findall('[^{}]+', arg)[0].strip()
        f_ptr = open(file)
        file = []
        for line in f_ptr:
            file.append(line.strip())
        f_ptr.close()
        return file

    def get_array(arg):
        array = re.findall('[^\\[\\]]+', arg)[0].replace(', ', ',').split(',')
        return array

    def get_r_gex(arg):
        r_gex = ''.join(re.findall("'.+'", arg)[0].replace("'", '', 1).rsplit("'", 1))
        return r_gex
    lhs, rhs = None, None
    if lhsReturn:
        lhs, rhs = string.split('=')
    else:
        rhs = string
    for num, char in enumerate(rhs):
        match char:
            case '{':
                state = states['array']
                rhs = get_file(rhs[num:])
                break
            case '[':
                state = states['array']
                rhs = get_array(rhs[num:])
                break
            case '\'':
                state = states['r_gex']
                rhs = get_r_gex(rhs[num:])
                break
    else:
        raise IncorrectSQPYError(f"Action not formatted correctly\n{string}")
    return (state, lhs.strip(), rhs) if lhsReturn else (state, rhs)


def mk_defines(Defines, lines):
    global customPtr
    for gex in re.findall("{.+}|\\[.+]|AUTOINCREMENT|'.+'", lines, re.IGNORECASE):
        if gex.upper() == "AUTOINCREMENT":
            lines = lines.replace(gex, f"<0>", 1)
            continue
        state, rhs = definedActions(gex, False)
        Defines[str(customPtr)] = [state, rhs]
        lines = lines.replace(gex, f"<{str(customPtr)}>", 1)
        customPtr += 1
    return lines


def sql_reader(lines, Defines):
    lines = mk_defines(Defines, lines)
    information = lines.replace('\n', '').replace('\r', '').split(',')
    number = 1
    try:
        table, information[0] = information[0].split('(', 1)
        table = re.findall('\\w+', table)[2]
        numberRe = re.findall("(\\* *[0-9]+)", information[-1])
        if len(numberRe) > 0:
            information[-1] = information[-1].rsplit('*', 1)[0]
            number = int(numberRe[0].replace("*", '').replace(" ", ''))
    except Exception:
        raise IncorrectSQPYError("Incorrect SQL Table construction")

    return table, information, number


def switched_Section(data):
    booleans = {}
    for line in data.split("\n"):
        if line == '':
            continue
        try:
            boolean_name, boolean = line.replace(' ', '').split("=")
        except Exception:
            raise IncorrectSQPYError("Incorrect First Section Format Error")
        if boolean.lower() == 'true':
            booleans[boolean_name.lower()] = True
        elif boolean.lower() == 'false':
            booleans[boolean_name.lower()] = False
        else:
            raise IncorrectSQPYError(f"First section Error >> '{line}' uses '{boolean}' instead of true or false")
    return booleans


def Defined_Section(data, Defines):
    # temp = data.split('\n')
    for line in data.split('\n'):
        line = line.strip()
        if line == '':
            continue
        state, lhs, rhs = definedActions(line)
        Defines[lhs] = [state, rhs]


def SQL_Section(data, Defines):
    # temp = data.split(';')
    entities = {}

    for line in data.split(';'):
        line = line.strip()
        if line == '':
            continue
        table_name, table_attributes, number = sql_reader(line, Defines)
        entity_package = Entities.Entities(table_name, table_attributes, number)
        entities[table_name] = entity_package
    return entities, Defines


def Iterations_Section(data, entities):
    for line in data.replace(' ', '').split("\n"):
        if line == '':
            continue
        try:
            line = line.split('=')
            a = entities[line[0]]
            entities[line[0]].iterations = int(line[1])

        except Exception:
            raise IncorrectSQPYError("Fourth section not formatted correctly")


def fill_foreign_integer(entities):
    list_keys = list(entities.keys())
    for num, entity_set in enumerate(entities):
        for entity in entities[entity_set].entities:
            for attribute in entity.attributes:
                if entity.attributes[attribute].foreign is not None:
                    index_foreign = list_keys.index(entity.attributes[attribute].foreign[0]) if entity.attributes[attribute].foreign[0] in list_keys else -1
                    index_self = list_keys.index(entity.name) if entity.name in list_keys else -1
                    if index_foreign < index_self:
                        a = entity.attributes[attribute].foreign[0]
                        foreign_entity = entities[entity.attributes[attribute].foreign[0]]
                        entity.attributes[attribute].set_value(random.choice(foreign_entity.entities).attributes[entity.attributes[attribute].foreign[1]].value)
                    else:
                        entity.attributes[attribute].set_value('null')
                    pass
                pass
    pass


def parse(file):
    # action = "{.+}"
    # array = "[.+]"
    # r_gex = "'.+'"
    Defines = preDefined()
    parts = ''
    for line in open(file):
        ln = re.findall("-- [^\n]*", line)
        if len(ln) > 0:
            line = line.replace(ln[0], '')
        parts += line
    parts = parts.split("%%")
    if len(parts) > 4:
        raise IncorrectSQPYError("Too Many Sections (%%)")

    booleans = switched_Section(parts[0])
    Defined_Section(parts[1], Defines)
    Entity_Sets, Defines = SQL_Section(parts[2], Defines)
    Iterations_Section(parts[3], Entity_Sets)
    return booleans, Entity_Sets, Defines


def deal_with_foreign_keys(entities, boolean):
    if boolean:
        entities = FormatFile.set_foreign(entities, boolean)
        fill_foreign_integer(entities)
    return entities


def main(arg1=None, arg2=None):
    read_file, write_file = getArgFiles(arg1, arg2)
    checkFile(read_file)
    booleans, entities, defines = parse(read_file)
    for entity in entities:
        entities[entity].build_line(defines)
    entities = deal_with_foreign_keys(entities, booleans.get('foreign', True))

    FormatFile.write_file(entities, write_file)
    pass


if __name__ == '__main__':
    main()
