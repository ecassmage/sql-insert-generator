from EntityPackage import Entity


class Entities:
    def __init__(self, name, table, iterations=1):
        self.entities = []
        self.autoincrement = {}
        self.iterations = iterations
        self.name = name
        self.table = table

    def build_EntitiesSet(self, defines):
        for _ in range(self.iterations):
            temp = Entity.Entity(self, self.name, self.table, defines)
            self.entities.append(temp)
        self.mk_copy()

    def mk_copy(self):
        unique = {}
        for attribute in self.entities[0].attributes:
            if self.entities[0].attributes[attribute].unique:
                unique[attribute] = self.entities[0].attributes[attribute].choices
        for entity in self.entities:
            for attribute in entity.attributes:
                if entity.attributes[attribute].unique:
                    entity.attributes[attribute].choices = unique[attribute]

    def set_number_of_iterations(self, number):
        self.iterations = number

    def build_line(self, defines):
        self.build_EntitiesSet(defines)
        for entity in self.entities:
            entity.build_line()
