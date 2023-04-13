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




entities = {
    "Billie": Entity({
        "Name": "Billie",
        "EntityType": "PlayerCharacter",
        "Job": "warrior",
        "Level": 1,
        "Max HP": 10,
        "Max MP": 2,
        "STR": 9,
        "RES": 11,
        "MND": 3,
        "AGI": 3,
        "HP": 10,
        "MP": 2,
        "Abilities": {
            "SkullCrusher": {
                "abilityFunc": "SkullCrusher",
                "abilityType": "OFFENSIVE"
            },
            "Focus": {
                "abilityFunc": "Focus",
                "abilityType": "NOT_OFFENSIVE"
            },
        }
    }),
    "EnemyWizard": Entity({
        "Name": "Enranged Wizard",
        "EntityType": "Enemy",
        "EntityID": "ENEMY_1",
        "Job": "mage",
        "Level": 1,
        "Max HP": 4,
        "Max MP": 11,
        "STR": 3,
        "RES": 3,
        "MND": 12,
        "AGI": 6,
        "HP": 4,
        "MP": 11,
        "Abilities": {
            "Fireball": "FORFIREBALL"
        }
    }),
    "EnemyWarrior": Entity({
        "Name": "Stalwart Warrior",
        "EntityType": "Enemy",
        "EntityID": "ENEMY_2",
        "Job": "warrior",
        "Level": 1,
        "Max HP": 10,
        "Max MP": 2,
        "STR": 10,
        "RES": 12,
        "MND": 3,
        "AGI": 4,
        "HP": 10,
        "MP": 2,
        "Abilities": {
            "Skull Crusher": "SkullCrusher"
        }
    })
}


def find_turn_order(pc_party: list[Entity], enemies_in_battle: list[Entity]):
    entity_list = []
    for actors in pc_party:
        entity_list.append(actors)
    for actors in enemies_in_battle:
        entity_list.append(actors)
    return sorted(entity_list, key=lambda x: x.AGI, reverse=True)


###




