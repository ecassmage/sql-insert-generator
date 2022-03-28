"""
What I want is something regex like though simplified
[0-9]{5} should return a number between 00000 and 99999 and
[a-z]{2} should return a string between aa and zz and
Ignore This -> [a-z]{1, 2} should return a string between a and zz. I might add this later.
simple stuff similar to regex in syntax, there won't be support for + * ? in context of length since it wouldn't be able to end as we aren't here to match patterns.
"""

import random

from SQPYErrors import GrammarError, SQPYGrammarError


class Grammar:
    def __init__(self, entity, attribute, grammar, defines=None, flag=0):
        self.specialCharacters = {'{': -1, '}': -2, '[': -3, ']': -4, '(': -5, ')': -6}

        self.entity = entity
        self.attribute = attribute

        self.type = grammar[0]
        self.grammar = self.__set_grammar(grammar[1])
        self.flag = flag

        self.first = None  # will be to store the first so it can always be found again
        self.current = None  # will store where currently located

        self.totalCombinations = 0

        self.__defineLength()
        pass

    def getChoice(self, optional=None):
        if self.attribute.unique and self.type == 2:
            self.__change_type()

        match self.type:
            case -1:
                return self.__getSpecial()
            case 0:
                raise SQPYGrammarError("File incorrectly stored")
            case 1:
                return self.__getArray(optional)
            case 2:
                return self.__get_r_gex(optional)
            case _:
                raise GrammarError("random choice could not be generated.")

    def __set_grammar(self, value):
        if self.type == -1:
            if value.lower() == 'autoincrement':
                return [0, 0]
        return value

    def __getSpecial(self):
        match self.grammar[0]:
            case 0:
                self.grammar[1] += 1
                return self.grammar[1] - 1

    def __getArray(self, optional: list):
        if len(self.grammar) == 0:
            raise SQPYGrammarError(f"Not enough unique combinations available for: {self.entity.name}: {self.attribute.name}")
        choice = random.choice(self.grammar)
        if self.attribute.unique:
            self.grammar.pop(self.grammar.index(choice))
        return choice

    def __get_r_gex(self, optional):
        self.current = self.first
        string = ''
        while self.current is not None:
            string += random.choice(self.current.possibilities)
            self.current = self.current.next
        self.current = self.first
        # if self.attribute.unique:
        #     if len(self.used) >= self.totalCombinations:
        #         raise SQPYGrammarError("Not enough unique combinations for a unique attribute")
        #     while True:
        #         if string not in self.used:
        #             break
        #         while self.current is not None:
        #             string += random.choice(self.current.possibilities)
        #             self.current = self.current.next
        #         self.current = self.first
        #     self.used.append(string)
        return string

    def __set(self):
        self.__Grammar_Encoder()

    def __defineLength(self):
        match self.type:
            case -1:
                self.totalCombinations = -1
            case 0:
                pass
            case 1:
                self.totalCombinations = len(self.grammar)
            case 2:
                self.__set()
                while self.current is not None:
                    self.totalCombinations = self.totalCombinations * len(self.current.possibilities) if self.totalCombinations > 0 else len(self.current.possibilities)
                    self.current = self.current.next
                self.current = self.first

    def __change_type(self):
        if 0 < self.totalCombinations <= 25000:
            self.type = 1
            self.grammar = self.__build_array(self.current)

        pass

    def __build_array(self, this_node):
        arr = []
        array_return = self.__build_array(this_node.next) if this_node.next is not None else ['']
        for char in this_node.possibilities:
            for ele in array_return:
                arr.append(char + ele)
        return arr

    def __Grammar_Encoder(self):
        array_encoded = []
        ptr = 0
        inside = False
        self.grammar = str(self.grammar)
        while ptr < len(self.grammar):
            if self.grammar[ptr] != '\\':
                if not inside:
                    if self.grammar[ptr] == '[':
                        inside = True
                        array_encoded.append(self.specialCharacters.get(self.grammar[ptr]))
                    elif self.grammar[ptr] == ']':
                        array_encoded.append(ord(self.grammar[ptr]))
                    else:
                        array_encoded.append(self.specialCharacters.get(self.grammar[ptr], ord(self.grammar[ptr])))
                else:
                    if self.grammar[ptr] == ']':
                        inside = False
                        array_encoded.append(self.specialCharacters.get(self.grammar[ptr], ord(self.grammar[ptr])))
                    else:
                        array_encoded.append(ord(self.grammar[ptr]))
            else:
                array_encoded.append(self.grammar[ptr+1])
                ptr += 1

            ptr += 1
        self.__Grammar_Constructor(array_encoded)

    def __dump_buffer(self, buffer, prev, booleans):

        if any(booleans):
            return prev, buffer
        self.first, prev = self.__makeNodes(self.first, buffer, prev)
        return prev, []

    def __Grammar_Constructor(self, encoded_string, ptr=0, parenthesis=False):
        def send_to_buffer(ctr_buf, bfr, prv, boolean):
            if len(ctr_buf) > 0 and not any(boolean):
                bfr.append(ctr_buf)
                ctr_buf = ''
            a, b = self.__dump_buffer(bfr, prv, boolean)
            return ctr_buf, a, b

        def add_to_container(ctr, character):
            if any([parenthesis, bracket, brace]):
                return ctr + chr(character)
            if len(ctr) > 0:
                buffer.append(ctr)
            return chr(character)

        prev = None
        bracket = False
        brace = False
        buffer = []
        container = ''

        while ptr < len(encoded_string):
            match encoded_string[ptr]:
                case -1:  # {
                    if brace:
                        raise GrammarError("Nested Braces {{}")
                    brace = True

                case -2:  # }
                    brace = False
                    buffer = buffer * self.__set_brace(container)
                    container = ''

                case -3:  # [
                    if bracket:
                        raise GrammarError("Unrecognized [ was found")

                    container, prev, buffer = send_to_buffer(container, buffer, prev, [bracket, brace, parenthesis])

                    bracket = True

                case -4:  # ]
                    bracket = False
                    buffer.append(self.__set_bracket(container))
                    container = ''

                case -5:  # (
                    container, prev, buffer = send_to_buffer(container, buffer, prev, [bracket, brace, parenthesis])

                    temp, ptr = self.__Grammar_Constructor(encoded_string, ptr+1, True)
                    for element in temp:
                        buffer.append(element)
                case -6:  # )
                    if parenthesis:
                        return buffer, ptr
                    else:
                        raise GrammarError("Unrecognized ) was found")
                case _:   # others
                    container, prev, buffer = send_to_buffer(container, buffer, prev, [bracket, brace, parenthesis])
                    container = add_to_container(container, encoded_string[ptr])
                    pass
            ptr += 1
        container, prev, buffer = send_to_buffer(container, buffer, prev, [bracket, brace, parenthesis])
        self.current = self.first

        return buffer, ptr

    @staticmethod
    def __makeNodes(first, list_of_nodes, prev):
        current = prev
        for obj_stored in list_of_nodes:
            current = Node(obj_stored)
            if first is None:
                first = current
            if prev is not None:
                prev.next = current
            prev = current
        return first, current

    def __set_bracket(self, bracket):
        bracket = self.__special_character_clean(bracket)
        ascii_arr = [False] * 256
        ptr = 0
        while ptr < len(bracket):
            if (ptr == 0 or bracket[ptr-1] != '\\') and bracket[ptr] == '\\' and bracket[ptr+1] == '-':
                ascii_arr[ord(bracket[ptr+1])] = True
                ptr += 2
            elif ptr + 1 == len(bracket) or bracket[ptr+1] != '-':
                ascii_arr[ord(bracket[ptr])] = True
                ptr += 1
            else:
                for char in range(ord(bracket[ptr]), ord(bracket[ptr+2]) + 1):
                    ascii_arr[char] = True
                ptr += 3
        arr = []
        for num, index in enumerate(ascii_arr):
            if index:
                arr.append(chr(num))
        return arr

    @staticmethod
    def __set_brace(brace):
        try:
            a = int(brace)
            return a
        except ValueError:
            raise ValueError(f"that wasn't an integer given {{{brace}}}")

    @staticmethod
    def __special_character_clean(string):
        arr = [['\\n', '\n'], ['\\r', '\r'], ['\\b', '\b'], ["\\'", "\'"], ['\\"', '\"']]
        for inp, out in arr:
            string = string.replace(inp, out)
        return string


class Node:
    def __init__(self, possibilities: list):
        self.possibilities = possibilities
        self.next = None


def main():
    # a = ['a', 'b', 'c']
    # b = a * 9
    # print(b)
    # g = Grammar('(a[0-9]){5}-0')
    # print(g.set_bracket('ab-r0-9\\-helloworldA-Z'))
    # print(g.set_bracket('ab-r0-9\\\\-helloworldA-Z'))
    # print(g.set_brace('12'))
    # while g.current is not None:
    #     print(f"{g.current.possibilities} -> ", end='')
    #     g.current = g.current.next
    g = Grammar(None, None, [2, '[0-9{}[()]{5} [0-9]{5}-0 AUTOINCREMENT [A-a]'])
    # while g.current is not None:
    #     print(g.current.possibilities)
    #     g.current = g.current.next
    # g.current = g.first
    print()
    print(g.getChoice())
    # exit()
    for _ in range(100):
        print(g.getChoice())
    pass


if __name__ == '__main__':
    main()
