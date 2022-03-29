from SQPYErrors import SQLError


class Attribute:
    def __init__(self, name, d_type=None, choice=None, null=True, unique=False, primary=False, foreign=None):
        self.name = name
        self.type = d_type

        self.choice = choice
        self.null = null
        self.value = None
        self.__length = 0

        self.unique = unique
        self.primary = primary
        self.__foreign_key = foreign

    def copy(self): return self.__copy()

    def __copy(self):
        return Attribute(self.name, self.type, self.choice, self.null, self.unique, self.primary, self.__foreign_key)

    def set_type(self, newType):
        acceptedTypes = ['INT', 'VARCHAR', 'DOUBLE', 'CHAR', 'FLOAT', 'DATE']
        if newType in acceptedTypes:
            self.type = newType
        else:
            raise SQLError(f"{newType} is not supported: supported: {acceptedTypes}")

    def set_VarLength(self, length):
        self.__length = length

    def set_foreign(self, foreign_key: list[str, str]):
        self.__foreign_key = foreign_key

    def get_foreign(self):
        return self.__foreign_key

    def is_foreign(self):
        return self.__foreign_key is not None

    def set_value(self, value):
        if value == 'null' or value is None:
            self.value = 'null'
            return
        elif isinstance(value, Attribute):
            self.value = value
            return

        match self.type:
            case "INT":
                self.value = int(value)
            case "DOUBLE":
                self.value = float(value)
            case _:
                self.value = "'" + value + "'"

    def __str__(self):
        return "null" if self.value is None else str(self.value)
