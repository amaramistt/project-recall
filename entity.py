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

    def __getitem__(self, item):
        return self.__items.get(item)


entities = {
    "Billie": {
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
    },
    "EnemyWizard": {
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
    },
    "EnemyWarrior": {
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
    }
}


def find_turn_order(entityList):
    list_item_num = 0

    # make a new list where each dict is turned to an object
    old_list = entityList
    for _ in range(len(entityList)):
        entity_name = entityList[list_item_num]["Name"]
        # "Billie"
        # Billie.Name
        print(entity_name)
        entity_name = Entity(entityList[list_item_num])
        print(entity_name.Name)
        entityList.append(entity_name)
        list_item_num += 1

    # make sure the dicts are out of the list
    for _ in range(0, list_item_num):
        entityList.remove(entityList[0])
    list_item_num = 0

    # sort the object list
    object_list = sorted(entityList, key=lambda x: x.AGI, reverse=True)

    # replace the objects with their former dict selves
    for _ in range(len(object_list)):
        other_list_item_num = 0
        print()
        for __ in range(len(old_list)):
            print(object_list[list_item_num].Name)
            print(old_list[other_list_item_num]["Name"])
            if object_list[list_item_num].Name == old_list[other_list_item_num]["Name"]:
                object_list[list_item_num] = old_list[other_list_item_num]
                print("PASSED THE DICT CHECK!")
            other_list_item_num += 1
        list_item_num += 1

    # thus sorting a list of dicts by a shared key
    print(object_list)
    return object_list


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
