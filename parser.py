import argparse
import os
import re
import random
import copy


class IncorrectFile(Exception):
    def __init__(self, file):
        super().__init__(f"{file} is not a .sqpy file. There fore I will not except it!!!")


def getFile():
    parser = argparse.ArgumentParser(description='A test program.')
    parser.add_argument("-get_file_to_read", help="Collects the supplied argument as a file to read from.")
    parser.add_argument("-get_file_to_write", help="Collects the supplied argument as a file to write to.")
    args = parser.parse_args()
    read_file = args.get_file_to_read
    write_file = args.get_file_to_write
    if read_file is None:
        if os.path.isfile('file.sqpy'):
            read_file = 'file.sqpy'
        else:
            raise argparse.ArgumentTypeError("Did not receive an sqpy file and file.sqpy (the stand-in was not located)")

    if write_file is None:
        write_file = 'output.sql'

    return read_file, write_file


def checkFile(file):
    if not file.endswith(".sqpy"):
        raise IncorrectFile(file)


def preDefined():
    definedLists = {None: None}
    if os.path.isfile('fname.txt'):
        definedLists['fname'] = [line.replace('\n', '').replace('\r', '') for line in open('fname.txt')]
    if os.path.isfile('lname.txt'):
        definedLists['lname'] = [line.replace('\n', '').replace('\r', '').capitalize() for line in open('lname.txt')]
    if os.path.isfile('hospital_names.txt'):
        definedLists['hospital_names'] = [line.replace('\n', '').replace('\r', '') for line in open('hospital_names.txt')]
    if os.path.isfile('street_names.txt'):
        definedLists['street_names'] = [line.replace('\n', '').replace('\r', '') for line in open('street_names.txt')]
    return definedLists


def parse_line(container):
    newContainer = []
    first_keys = ['INT', 'VARCHAR', 'BOOL', 'DATE', 'DOUBLE', 'FLOAT', 'NULL']
    third_keys = ['UNIQUE', "FOREIGN"]
    for element in container:
        split_element = element.split(" ")
        ele_1 = split_element[0] if len(split_element) > 0 and split_element[0] in first_keys else None
        ele_2 = split_element[1] if len(split_element) > 1 and split_element[1] not in third_keys else None
        ele_3 = split_element[1] if len(split_element) > 1 and split_element[1] in third_keys else split_element[2] if len(split_element) > 2 and split_element[2] in third_keys else None
        newContainer.append([ele_1, ele_2, ele_3])
    return tuple(newContainer)


def getDefines(define_line):
    if not define_line.endswith('.txt'):
        if define_line.startswith('range'):
            regex = re.findall('[0-9]+', define_line)
            temp = [line for line in range(int(regex[0] if len(regex) == 2 else 0), int(regex[1] if len(regex) == 2 else regex[0]))]
        else:
            temp = define_line.replace('[', '').replace(']', '').split(',')
    else:
        temp = [line.replace('\n', '').replace('\r', '') for line in open(define_line)]
    return temp


def collectInformation(defines, file):
    Entities = {}
    part = 0
    rules = {'foreign': True}
    for line in open(file):
        line = line.strip()
        if line == '':
            continue

        match part:
            case 0:
                line = line.replace(' ', '')
                if line == '%%':
                    part = 1
                    continue
                splitted = line.split('=')
                match splitted[0]:
                    case 'foreign':
                        rules[splitted[0]] = True if splitted[1].lower() == 'true' else False

            case 1:
                line = line.replace(' ', '')

                if line == '%%':
                    part = 2
                    continue

                split_line = line.split("=", 1)
                identifier = split_line[0]
                defines[identifier] = getDefines(split_line[1])

            case 2:
                split_line = (''.join(line.rsplit(')', 1))).split("(", 1)
                entity_split = split_line[1].split(" * ", 1)
                if len(entity_split) == 1:
                    entity_split.append(str(1))

                identifier = split_line[0].replace(' ', '')
                Entities[identifier] = [parse_line(entity_split[0].split(', ')), int(entity_split[1])]

    return defines, Entities, rules


def buildEntity(key, information, Defines, completedEntities):
    string = []

    def getUniqueAttribute(Att_Type, Unique, previous):
        match Att_Type:
            case 'INT':
                return (previous + 1 if previous is not None else 1) if Unique else random.randrange(1000000)
            case 'VARCHAR':
                return 'a'
            case 'DATE':
                return f'{random.randrange(1900, 2022)}-{random.randrange(1, 13)}-{random.randrange(1, 29)}'
            case 'DOUBLE' | 'FLOAT':
                return round(random.uniform(0, 1000000), 2)
            case 'NULL':
                return 'null'

    def formatChoice(Att_Type, result):
        if result is None:
            return None
        match Att_Type:
            case 'INT':
                return int(result)
            case 'VARCHAR' | 'DATE':
                return f"'{str(result)}'"
            case 'DOUBLE' | 'FLOAT':
                return float(round(random.uniform(0, 1000000), 2))
            case 'NULL':
                return result

    for pos, section in enumerate(information):
        foreign = False
        try:
            if section[2] == 'FOREIGN':
                choice = section[1]
                foreign = True
            else:
                choice = random.choice(Defines[section[1]]) if Defines[section[1]] is not None else getUniqueAttribute(section[0], True if section[2] == 'UNIQUE' else False, completedEntities[key][-1][pos] if len(completedEntities[key]) > 0 else None)
        except KeyError:
            choice = 0
        except IndexError:
            raise IndexError(f"Not enough choices have been given and we have run out.\n"
                             f"key: {key}({section[0]} {section[1].replace(f'{key}_', '').replace(f'_UNIQUE', '') if section[1].replace(f'{key}_', '').replace(f'_UNIQUE', '') is not None else ''} {section[2] if section[2] is not None else ''})")
        if section[2] == "UNIQUE" and Defines[section[1]] is not None:
            Defines[section[1]].pop(Defines[section[1]].index(choice))
        string.append(formatChoice(section[0], choice) if not foreign else choice)
    return string


def foreign_keys(completed_list, rule):
    for key in completed_list:
        for entity in completed_list[key]:
            for num, section in enumerate(entity):
                if type(section) is str:
                    regex = re.findall('\\([0-9]+\\)', section)
                    if len(regex) == 1:
                        section = section.replace(regex[0], '')
                        regex = re.findall('[0-9]+', regex[0])
                        entity[num] = random.choice(completed_list[section])[int(regex[0])] if rule else 'null'

                        pass
    pass


def writeSQL(information, output):
    file = open(output, 'w')
    for key in information:
        for entity in information[key]:
            values = ''
            for num, section in enumerate(entity):
                values += f', {section}' if num > 0 else str(section)
            file.write(f"INSERT INTO {key} VALUES({values});\n")
        file.write('\n')
    file.close()


def main():
    read_file, write_file = getFile()
    checkFile(read_file)
    Defines, Entities, rules = collectInformation(preDefined(), read_file)
    completedEntities = {}
    for key in Entities:
        completedEntities[key] = []
        for section in Entities[key][0]:
            if section[2] == 'UNIQUE':
                Defines[f"{key}_{section[1]}_UNIQUE"] = copy.copy(Defines.get(section[1], None))
                section[1] = f"{key}_{section[1]}_UNIQUE"
            pass
    for key in Entities:
        for _ in range(Entities[key][1]):
            string = buildEntity(key, Entities[key][0], Defines, completedEntities)
            completedEntities[key].append(string)
        pass

    foreign_keys(completedEntities, rules['foreign'])
    writeSQL(completedEntities, write_file)
    pass


if __name__ == '__main__':
    main()
