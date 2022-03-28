import re

from SQPYErrors import IncorrectSQPYError


def format_rules(data, entities, booleans):
    return __format_rules(data, entities, booleans)


def __format_rules(data, entities, booleans):

    for rule in re.sub('[\n\r\t ]', '', data).split(";"):

        if rule != '':

            lhs, rhs = re.split('->|=', rule, maxsplit=1)  # if this is longer then left and right, something isn't right.
            lhs, rhs = lhs.split('.'), rhs.replace(')', '').split('(')

            __set_iterations_limit(entities, lhs[0], rhs[0]) if not booleans['relation_limits'] or len(rhs) == 1 else __set_limit(entities, lhs, __get_range_limit(rhs))


def __get_range_limit(rhs: list):
    match len(rhs):
        case 0:
            raise IncorrectSQPYError("no rhs to a rule was given")
        case 1:
            num1, num2 = __get_nums(rhs[0])
            return None, num1, num2
        case 2:
            num1, num2 = __get_nums(rhs[1])
            return rhs[0], num1, num2
        case _:
            raise IncorrectSQPYError("Section 4 has longer then expected rule")


def __get_nums(nums: str):
    if ',' in nums:
        nums = nums.split(",")
        return int(nums[0]), int(nums[1])
    else:
        return -1, int(nums)


def __set_iterations_limit(entities: dict, lhs: str, rhs: str):
    try:
        rhs = int(rhs)
        entities[lhs].set_copies(rhs)
    except TypeError:
        raise IncorrectSQPYError(f"rhs couldn't be read with rule set: {lhs} -> {rhs}")
    except KeyError:
        raise IncorrectSQPYError(f"entity({lhs}) could not be found.")
    pass


def __set_limit(entities: dict, lhs: list, limit: tuple[str, int, int]):
    try:
        entities[lhs[0]].add_limit(lhs, limit)
    except TypeError:
        raise IncorrectSQPYError(f"rhs couldn't be read with rule set: {lhs} -> {limit}")
    except KeyError:
        raise IncorrectSQPYError(f"entity({lhs}) could not be found.")
