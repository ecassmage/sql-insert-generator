import re

from SQPYErrors import IncorrectSQPYError, InternalProblemError
from Format_SQPY.format_defines import mk_defines


def find_entities(string: str, defines=None) -> tuple[dict[str]: list, dict]: return __find_entities(string, {} if defines is None else defines)


def check_order_of_brackets(string: str) -> str: return __check_order_of_brackets(string)
def form_and_factor(data: str) -> list: return __form_and_factor(data)
def invert_ord(char): return -1 * ord(char)
def tokenize_sql(dict_of_sql: dict): return __tokenize_sql(dict_of_sql)


def __find_entities(string: str, defines) -> tuple[dict[str]: list, dict]:
    formatted_entities = []
    for entity in string.split(";"):
        entity = check_order_of_brackets(mk_defines(defines, entity))
        tokens = form_and_factor(entity)

        formatted_entity = []
        format_string = ''
        for token in tokens:
            if token != invert_ord(','):
                format_string += chr(token)

            else:
                if format_string.replace('\n', '').replace('\r', '') != '':
                    formatted_entity.append(format_string.replace('\n', '').replace('\r', ''))

                format_string = ''

        number = 1
        if format_string.replace('\n', '').replace('\r', '') != '':  # Checks for if number of entities was specified with CREATE TABLE
            number = re.split(" *\\* *", re.sub('[\n\t\r]', '', format_string))
            formatted_entity.append(number[0])
            try:
                number = int(number[1]) if len(number) > 1 else 1
            except TypeError:
                raise IncorrectSQPYError
            except Exception:
                raise InternalProblemError("I am not sure what would trigger this")
            pass

        if len(formatted_entity) > 0:
            formatted_entities.append([formatted_entity, number])

    return_dict = {}
    for entity in formatted_entities:
        name, entity[0][0] = entity[0][0].split('(', 1)
        bee = re.findall('[^ ]+', name)[-1]
        return_dict[re.findall('[^ ]+', name)[-1]] = entity

    tokenize_sql(return_dict)

    return return_dict, defines


def __check_order_of_brackets(string: str) -> str:
    order = {')': '(', '}': '{', ']': '[', '>': '<', '\'': '\'', '"': '"'}
    open_order = list('([{<\'"')
    bracket_stack = []

    ptr = 0
    while ptr < len(string):

        if string[ptr] in open_order:
            bracket_stack.append(string[ptr])

        elif string[ptr] in order:
            popped = bracket_stack.pop()

            if order[string[ptr]] != popped:
                raise IncorrectSQPYError(f"Incorrect closing bracket match up: {popped} ... {string[ptr]}")

        ptr += 1

    if len(bracket_stack) > 0:
        raise IncorrectSQPYError(f"brackets and others left unclosed: {bracket_stack}")

    return string


def __form_and_factor(data: str) -> list:
    parenthesis_count = 0
    ptr = 0

    Tokens = []
    while ptr < len(data):
        match data[ptr]:
            case '\\':
                Tokens.append(special_characters(data[ptr+1], True))
                ptr += 1

            case '(':
                parenthesis_count += 1
                Tokens.append(ord(data[ptr]))

            case ')':
                parenthesis_count -= 1
                Tokens.append(ord(data[ptr]))

            case ',':
                Tokens.append(invert_ord(data[ptr]) if parenthesis_count < 2 else ord(' '))

            case _:
                Tokens.append(ord(data[ptr]))

        ptr += 1
    return Tokens


def __tokenize_sql(dict_of_sql):
    for entity in dict_of_sql:

        for num, line in enumerate(dict_of_sql[entity][0]):
            dict_of_sql[entity][0][num] = re.findall("PRIMARY KEY|FOREIGN KEY|NOT NULL|[^ \t()]+", line, re.IGNORECASE)

    return dict_of_sql


def list_to_str(list_of_strings: list):
    string_final = ''
    for string in list_of_strings:
        string_final += string
    return string_final


def special_characters(char, backslash=False):
    match char:
        case 'n':
            return ord('\n') if backslash else ord(char)

        case 'r':
            return ord('\r') if backslash else ord(char)

        case 't':
            return ord('\t') if backslash else ord(char)

        case _:
            return ord(char)


def main():
    lis = [line for line in open('test.sqpy')]
    string = list_to_str(lis)
    split = string.split("%%")
    a, d = find_entities(split[2])
    print(a)
    print(d)
    import clean_format_sql
    clean_format_sql.tokenize_sql(a)
    pass


if __name__ == '__main__':
    import sys
    sys.path.insert(1, 'E:\\Github\\Projects\\Python\\sql insert generator')
    main()
