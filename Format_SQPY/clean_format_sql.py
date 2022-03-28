import re


def tokenize_sql(list_of_sql):
    for entity in list_of_sql:
        list_of_sql[entity] = __tokenize_sql(list_of_sql[entity])
    return list_of_sql


def __tokenize_sql(lis):

    for num, line in enumerate(lis):
        lis[num] = re.findall("PRIMARY KEY|FOREIGN KEY|NOT NULL|[^ \t()]+", line, re.IGNORECASE)
        pass
    return lis


# while ptr < len(info):
#     match info[ptr]:
#         case _:
#             pass
#     ptr += 1
# pass
