import sys
import os


import SQParser
from SQPYErrors import TooManyArgumentsError, IncorrectFileError, NoFileGivenError


def __getArgFiles(arg1, arg2):
    if len(sys.argv) > 3:
        raise TooManyArgumentsError
    read_file = sys.argv[1] if len(sys.argv) > 1 else None
    write_file = sys.argv[2] if len(sys.argv) > 2 else None

    if read_file is None:
        if arg1 is None:
            raise NoFileGivenError("No File was given")
        if os.path.isfile(arg1):
            read_file = arg1
        else:
            raise FileNotFoundError(f"{arg1} was not found")

    if write_file is None:
        write_file = arg2 if arg2 is not None else 'output.sql'
    return read_file, write_file


def __checkFile(file):
    if not file.endswith(".sqpy"):
        raise IncorrectFileError(file)


def write_to_file(entity_dict, file):
    file_writer = open(file, 'w')
    for entity_set in entity_dict:
        for entity in entity_dict[entity_set].entity_siblings:
            file_writer.write(str(entity) + '\n')
        file_writer.write('\n')
    file_writer.close()


def __main__(arg1=None, arg2=None):
    read_file, write_file = __getArgFiles(arg1, arg2)
    __checkFile(read_file)
    booleans, entities, defines = SQParser.read_input(read_file)
    for entity in entities:
        entities[entity].build_outputs()
    entities = SQParser.deal_with_foreign_keys(entities, booleans.get('foreign', True), booleans.get('foreign_reorder', True))
    if booleans.get('print_in_terminal', False):
        for ent in entities:
            print(f"{entities[ent]}\n")
    write_to_file(entities, write_file)
    pass


if __name__ == '__main__':
    __main__()
