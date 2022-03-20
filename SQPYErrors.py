class EntityFamilyError(Exception):
    def __init__(self, message='Error in the entity family'):
        super().__init__(message)


class SQLError(EntityFamilyError):
    def __init__(self, message='input sql was unable to be read correctly'):
        super().__init__(message)


class GrammarError(Exception):
    def __init__(self, message='GRAMMAR ERROR'):
        super().__init__(message)


class GrammarSyntaxError(GrammarError):
    def __init__(self, message="SYNTAX ERROR"):
        super().__init__(message)


class TooManyArgumentsError(Exception):
    def __init__(self, message="Too many Arguments were given"):
        super().__init__(message)


class IncorrectSQPYError(Exception):
    def __init__(self, message="IncorrectSQPYError"):
        super().__init__(message)


class SQPYGrammarError(IncorrectSQPYError):
    def __init__(self, message="Grammatical Error in .sqpy file"):
        super().__init__(message)


class IncorrectFileError(Exception):
    def __init__(self, file):
        super().__init__(f"{file} is not a .sqpy file. There fore I will not except it!!!")

