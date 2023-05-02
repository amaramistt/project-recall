class Entity(object):
    def __init__(self, template):
        self.Name = template["Name"]
        self.EntityType = template["EntityType"]
        self.Job = template["Job"]
        self.Level = template["Level"]
        self.MaxHP = template["Max HP"]
        self.MaxMP = template["Max MP"]
        self.STR = template["STR"]
        self.RES = template["RES"]
        self.MND = template["MND"]
        self.AGI = template["AGI"]
        self.MP = template["HP"]
        self.HP = template["MP"]
        self.Abilities = template["Abilities"]
        self.__items = {}

    def __repr__(self):
        #makes it so that whenever the class object itself is printed, it prints the below instead!
        return f'Name: {self.Name}\nLevel: {self.Level}\nHP: {self.HP}/{self.MaxHP}\nMP: {self.MP}/{self.MaxMP}\nJOB: {self.Job}\nSTR: {self.STR}\nRES: {self.RES}\nMND: {self.MND}\nAGI: {self.AGI}'


def find_turn_order(pc_party: list[Entity], enemies_in_battle: list[Entity]):
    entity_list = []
    for actors in pc_party:
        entity_list.append(actors)
    for actors in enemies_in_battle:
        entity_list.append(actors)
    return sorted(entity_list, key=lambda x: x.AGI, reverse=True)


###




