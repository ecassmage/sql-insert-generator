import re
import os

from SQPYErrors import IncorrectSQPYError


states = {'special': -1, 'file': 0, 'array': 1, 'r_gex': 2}
customPtr = 10


# This type of thing is something new I am trying out for organizational purposes.
def mk_defines(Defines: dict, lines: str) -> str: return __mk_defines(Defines, lines)
def definedActions(string, lhsReturn=True): return __definedActions(string, lhsReturn)
def preDefined(): return __preDefined()


def __preDefined():
    def preDefined_SQL():
        definedLists['0'] = [states['special'], "AUTOINCREMENT"]

    folder_name = 'Defined_Files'
    definedLists = {None: None}
    for file in os.listdir(folder_name):
        nm = re.sub("\\..+", '', file, re.DOTALL)
        definedLists[nm] = [states['array'], [line.strip() for line in open(f'{folder_name}\\{file}')]]

    # if os.path.isfile('Defined_Files/fname.txt'):
    #     definedLists['fname'] = [states['array'], [line.strip() for line in open('Defined_Files/fname.txt')]]
    # if os.path.isfile('Defined_Files/lname.txt'):
    #     definedLists['lname'] = [states['array'], [line.strip().capitalize() for line in open('Defined_Files/lname.txt')]]
    # if os.path.isfile('Defined_Files/hospital_names.txt'):
    #     definedLists['hospital_names'] = [states['array'], [line.strip() for line in open('Defined_Files/hospital_names.txt')]]
    # if os.path.isfile('Defined_Files/street_names.txt'):
    #     definedLists['street_names'] = [states['array'], [line.strip() for line in open('Defined_Files/street_names.txt')]]

    preDefined_SQL()
    return definedLists


def __mk_defines(Defines: dict, lines: str) -> str:
    global customPtr
    for gex in re.findall(r"{[^}]+}|\[[^]]+]|AUTOINCREMENT|'(?:\\'|[^'])*'", lines, re.IGNORECASE):
        if gex == '':
            continue
        if gex.upper() == "AUTOINCREMENT":
            lines = lines.replace(gex, f"<0>", 1)
            continue
        state, rhs = definedActions(gex, False)
        Defines[str(customPtr)] = [state, rhs]
        lines = lines.replace(gex, f"<{str(customPtr)}>", 1)
        customPtr += 1
    return lines


def __definedActions(string, lhsReturn=True):
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