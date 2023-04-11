class Entity(object):
    def __init__(self, entity_template):
        self.Name = entity_template["Name"]
        self.EntityType = entity_template["EntityType"]
        self.Job = entity_template["Job"]
        self.Level = entity_template["Level"]
        self.MaxHP = entity_template["Max HP"]
        self.MaxMP = entity_template["Max MP"]
        self.STR = entity_template["STR"]
        self.RES = entity_template["RES"]
        self.MND = entity_template["MND"]
        self.AGI = entity_template["AGI"]
        self.MP = entity_template["HP"]
        self.HP = entity_template["MP"]
        self.Abilities = entity_template["Abilities"]
        self.EntityId = entity_template["EntityID"] if "EntityID" in entity_template else "pc"

    def __repr__(self):
        return f'{self.Name} [STR: {self.STR} RES: {self.RES} MND: {self.MND} AGI: {self.AGI}]'

    def my_cool_method(self, last_name, middle_name):
        return self.Name + middle_name + last_name


entities = {
    "Billie": Entity({
        "Name": "Billie",
        "EntityType": "PlayerCharacter",
        "Job": "mage",
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
        # Basic things that should be easy to call like name, id, and stats
        "Name": "Enraged Wizard",
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
            "Fireball": "forfireball"
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

entities_by_id = {entities[e].EntityId: entities[e] for e in entities}

def find_turn_order(entity_list: list[Entity]) -> list[Entity]:
    return sorted(entity_list, key=lambda x: x.AGI, reverse=True)
    # list_item_num = 0
    #
    # # make a new list where each dict is turned to an object
    # old_list = entity_list
    # for _ in range(len(entity_list)):
    #     entity_name = entity_list[list_item_num]["Name"]
    #     # "Billie"
    #     # Billie.Name
    #     print(entity_name)
    #     entity_name = Entity(entity_list[list_item_num])
    #     print(entity_name.Name)
    #     entity_list.append(entity_name)
    #     list_item_num += 1
    #
    # # make sure the dicts are out of the list
    # for _ in range(0, list_item_num):
    #     entity_list.remove(entity_list[0])
    # list_item_num = 0
    #
    # # sort the object list
    # object_list = sorted(entity_list, key=lambda x: x.AGI, reverse=True)
    #
    # # replace the objects with their former dict selves
    # for _ in range(len(object_list)):
    #     other_list_item_num = 0
    #     print()
    #     for __ in range(len(old_list)):
    #         print(object_list[list_item_num].Name)
    #         print(old_list[other_list_item_num]["Name"])
    #         if object_list[list_item_num].Name == old_list[other_list_item_num]["Name"]:
    #             object_list[list_item_num] = old_list[other_list_item_num]
    #             print("PASSED THE DICT CHECK!")
    #         other_list_item_num += 1
    #     list_item_num += 1
    #
    # # thus sorting a list of dicts by a shared key
    # print(object_list)
    # return object_list


###


# What I need!
# function that takes an entity (dict) as an argument
# take the ["Name"] key's definition
# create a class object named whatever the ["Name"] key is while using the actual dict as an argument
# so for example
#
# dick = {"Name":"Billie","OtherShit":"Existent"}
# voodooMagic(dick)
# print(Billie.Name)
# print(Billie.OtherShit)
#
# OUTPUT:
# Billie
# Existent
#
# make/teach me how to make voodooMagic() :3

turnOrder = find_turn_order([entities["Billie"], entities["EnemyWizard"], entities["EnemyWarrior"]])
print(turnOrder)
