import os
import random
import copy

CLEAR = 'cls' if os.name == 'nt' else 'clear'

stat_modifier_table = {
    -2: 0.5,
    -1: 0.75,
    0: 1,
    1: 1.5,
    2: 2
}

jobs = {
    # JOB STATS SYNTAX
    # Goes from 1 to 6
    # 1 means dogshit and 6 means top of the line
    # stats go HP > MP > STR > RES > MND > AGI
    # !!! IN ORDER !!!
    
    "warrior": {
        "stats": [4, 1, 4, 3, 1, 1],
        "dependencies": [],
        "abilities": {
            10: "skullcrusher"
        }
    },
    "just a guy": {
        "stats": [3, 1, 1, 2, 1, 3],
        "abilities": {
            10: "slap"
        }
    },
    "mage": {
        "stats": [2, 3, 1, 2, 4, 3],
        "abilities": {
            1: "spark",
            10: "fireball"
        }
    },
    "priest": {
        "stats": [3, 2, 2, 2, 2, 2],
        "abilities": {
            5: "heal",
            10: "resilienceprayer"
        }
    },
    "thief": {
        "stats": [3, 1, 3, 2, 1, 4],
        "abilities": {}
    },
    "monk": {
        "stats": [3, 1, 3, 3, 2, 3],
        "abilities": {
            10: "focus",
        }
    }
}

abilities = {

    #Ability Template

    #LevelLearned: Level that the class should learn the ability
    #NAME: Used to name the ability in the abilities dict inside an entity's stat sheet
    #ABILITYFUNC: Name of the function's ability. Case sensitive. Must be exact same as the function.
    #ABILITYTYPE: If it's NOT_OFFENSIVE, it can target things other than just enemies and must handle *everything* in its function
    #             Meaning it has to deal damage if it deals damage and also check for death
    
    #LevelLearned:{"NAME": "AbilityName", 
    #"AbilityName": {
    #"ABILITYFUNC": "name",
    #"ABILITYTYPE": "OFFENSIVE/NOT_OFFENSIVE"
    #}}
    
    "focus": {
        "name": "Focus",
        "callback": "focus",
        "target": "TARGET_SELF"
    },
    "fireball": {
        "name": "Fireball",
        "callback": "forfireball",
        "target": "TARGET_DIRECT"
    },
    "spark": {
        "name": "Spark",
        "callback": "spark"
    },
    "skullcrusher": {
        "name": "Skull Crusher",
        "callback": "skull_crusher",
        "target": "TARGET_VICTIM"
    },
    "slap": {
        "name": "Slap",
        "callback": "slap",
        "target": "TARGET_SELF"
    },
    "heal": {
        "name": "Heal",
        "callback": "heal",
        "target": "TARGET_PARTY"
    },
    "resilienceprayer": {
        "name": "Resilience Prayer",
        "callback": "resilience_prayer",
        "target": "TARGET_PARTY_ALL"
    }
}

stats_order = {
    # required to let levelUp() or any function like it work at all
    1: "Max HP",
    2: "Max MP",
    3: "STR",
    4: "RES",
    5: "MND",
    6: "AGI"
}

player_character_names = [
    "Cullep",
    "Nessira",
    "Rikia",
    "Jaen",
    "Loura",
    "Slyff",
    "Jabal",
    "Dumas",
    "Isira",
    "Runo",
    "Banut",
    "Banut",
    "Carpef",
    "Linnetia",
    "Orthur",
    "Merisa",
    "Vyn",
    "Odo",
    "Nria",
    "Raelle",
    "Draya"
]

class Entity(object):
    def __init__(self, template):
        self.Name = template["Name"]
        self.EntityType = template["EntityType"]
        self.Level = template["Level"]
        self.MaxHP = template["Max HP"]
        self.MaxMP = template["Max MP"]
        self.STR = template["STR"]
        self.RES = template["RES"]
        self.MND = template["MND"]
        self.AGI = template["AGI"]
        self.MP = template["MP"]
        self.HP = template["HP"]
        self.Abilities = template["Abilities"]
        if self.EntityType == "Enemy" or self.EntityType == "BossEnemy":
            self.ExperienceReward = 0
            self.MoneyReward = 0
        if self.EntityType == "BossEnemy":
            self.BossLogic = template["BossLogic"]
            self.Phases = template["Phases"]
        elif self.EntityType == "PlayerCharacter" or self.EntityType == "Khorynn":
            self.ExperienceCount = 0
            self.Job = template["Job"]  
            self.MasteredJobs = []
            self.Items = {}
        self.StatChanges = {
            "STR": 0,
            "RES": 0,
            "MND": 0,
            "AGI": 0
        }
        self.EquipmentStats = {
            "Max HP": 0,
            "Max MP": 0,
            "STR": 0,
            "RES": 0,
            "MND": 0,
            "AGI": 0
        }

    def __repr__(self):
        #makes it so that whenever the class object itself is printed, it prints the below instead!
        return f'\nName: {self.Name}\nLevel: {self.Level}\nHP: {self.HP}/{self.MaxHP}\nMP: {self.MP}/{self.MaxMP}\nJOB: {self.Job}\nSTR: {self.STR}\nRES: {self.RES}\nMND: {self.MND}\nAGI: {self.AGI}'

    def get_strength(self):
        return int(self.STR * stat_modifier_table[self.StatChanges["STR"]]) + self.EquipmentStats["STR"]

    def get_res(self):
        return int(self.RES * stat_modifier_table[self.StatChanges["RES"]]) + self.EquipmentStats["RES"]

    def get_mind(self):
        return int(self.MND * stat_modifier_table[self.StatChanges["MND"]]) + self.EquipmentStats["MND"]

    def get_agi(self):
        return int(self.AGI * stat_modifier_table[self.StatChanges["AGI"]]) + self.EquipmentStats["AGI"]

    def change_stat(self, stat_to_change, stages_to_increment):
        new_value = self.StatChanges[stat_to_change] + stages_to_increment
        new_value = new_value if new_value <= 2 else 2
        new_value = new_value if new_value >= -2 else -2

        self.StatChanges[stat_to_change] = new_value    

entities = {
    "Khorynn": Entity({
        "Name": "Khorynn",
        "EntityType": "PlayerCharacter",
        "Job": "undecided",
        "Level": 1,
        "Max HP": 1,
        "Max MP": 1,
        "STR": 1,
        "RES": 1,
        "MND": 1,
        "AGI": 1,
        "HP": 1,
        "MP": 1,
        "Abilities": {}
    }),
    "EnemyWizard": Entity({
        "Name": "Enraged Wizard",
        "EntityType": "Enemy",
        "Level": 1,
        "Max HP": 6,
        "Max MP": 12,
        "STR": 3,
        "RES": 7,
        "MND": 15,
        "AGI": 10,
        "HP": 6,
        "MP": 12,
        "Abilities": {}
    }),
    "EnemyWarrior": Entity({
        "Name": "Stalwart Warrior",
        "EntityType": "Enemy",
        "Level": 1,
        "Max HP": 16,
        "Max MP": 2,
        "STR": 14,
        "RES": 12,
        "MND": 3,
        "AGI": 4,
        "HP": 16,
        "MP": 2,
        "Abilities": {}

    }),
    "Volakuma": Entity({
       "Name": "Volukuma",
        "EntityType": "Enemy",
        "Level": 1,
        "Max HP": 10,
        "Max MP": 2,
        "STR": 15,
        "RES": 8,
        "MND": 1,
        "AGI": 12,
        "HP": 10,
        "MP": 2,
        "Abilities": {}
    }),
    "Slime": Entity({
        "Name": "Slime",
        "EntityType": "Enemy",
        "Level": 1,
        "Max HP": 20,
        "Max MP": 0,
        "STR": 11,
        "RES": 10,
        "MND": 1,
        "AGI": 6,
        "HP": 20,
        "MP": 0,
        "Abilities": {}
    }),
    
    "EnragedWarrior": Entity({
        "Name": "Enraged Warrior",
        "EntityType": "Enemy",
        "Level": 10,
        "Max HP": 180,
        "Max MP": 20,
        "STR": 105,
        "RES": 80,
        "MND": 30,
        "AGI": 50,
        "HP": 110,
        "MP": 20,
        "Abilities": {}
    }),
    "StalwartWizard": Entity({
        "Name": "Stalwart Wizard",
        "EntityType": "Enemy",
        "Level": 10,
        "Max HP": 100,
        "Max MP": 79,
        "STR": 30,
        "RES": 60,
        "MND": 105,
        "AGI": 70,
        "HP": 70,
        "MP": 79,
        "Abilities": {}
    }),
    "DisgracedMonk": Entity({
        "Name": "Disgraced Monk",
        "EntityType": "Enemy",
        "Level": 20,
        "Max HP": 250,
        "Max MP": 100,
        "STR": 150,
        "RES": 110,
        "MND": 110,
        "AGI": 150,
        "HP": 180,
        "MP": 100,
        "Abilities": {}
    }),
    "SorcererSupreme": Entity({
        "Name": "Sorcerer Supreme",
        "EntityType": "Enemy",
        "Level": 20,
        "Max HP": 150,
        "Max MP": 200,
        "STR": 30,
        "RES": 110,
        "MND": 200,
        "AGI": 140,
        "HP": 130,
        "MP": 200,
        "Abilities": {}        
    }),
    "CraftyThief": Entity({
        "Name": "Crafty Thief",
        "EntityType": "Enemy",
        "Level": 20,
        "Max HP": 230,
        "Max MP": 80,
        "STR": 165,
        "RES": 80,
        "MND": 100,
        "AGI": 200,
        "HP": 170,
        "MP": 80,
        "Abilities": {}        
    }),
    "GelatinousKing": Entity({
        "Name": "Gelatinous King",
        "EntityType": "BossEnemy",
        "Level": 30,
        "Max HP": 4000,
        "Max MP": 50,
        "STR": 270,
        "RES": 160,
        "MND": 100,
        "AGI": 210,
        "HP": 4000,
        "MP": 50,
        "BossLogic": "king_slime",
        "Phases": {
            "Spawn Phase 1": False,
            "Spawn Phase 2": False,
            "Spawn Phase 3": False,
            "Spawn Phase 4": False
        },
        "Abilities": {}
    }),
    "GelatinousServant": Entity({
        "Name": "Gelatinous Servant",
        "EntityType": "Enemy",
        "Level": 30,
        "Max HP": 400,
        "Max MP": 30,
        "STR": 190,
        "RES": 90,
        "MND": 100,
        "AGI": 230,
        "HP": 400,
        "MP": 30,
        "Abilities": {}
    }),
    "StoneGolem": Entity({
        "Name": "Stone Golem",
        "EntityType": "BossEnemy",
        "Level": 30,
        "Max HP": 1500,
        "Max MP": 0,
        "STR": 320,
        "RES": 210,
        "MND": 2,
        "AGI": 80,
        "HP": 1500,
        "MP": 0,
        "BossLogic": "stone_golem",
        "Phases": {
            "Phase 2": False
        },
        "Abilities": {}
    })
}

def get_jobs_map():
    return jobs

def get_abilities_map():
    return abilities

def get_entity_map():
    return entities


def find_party_level(party):
    party_levels = []
    for member in party:
        party_levels.append(member.Level)
    party_levels = sorted(party_levels, reverse=True)
    return party_levels[0]

def debug_starting_stats():
    os.system(CLEAR)
    debug = entity.generate_party_member(1)
    debug.Job = "just a guy"
    gen_starting_stats(debug, True)
    print(f"Base Stat 1\nLevel 1:{debug.get_strength()}")
    lvl_up_bulk(debug, 9, True)
    print(f"Level 10: {debug.get_strength()}")
    lvl_up_bulk(debug, 10, True)
    print(f"Level 20: {debug.get_strength()}")
    lvl_up_bulk(debug, 10, True)
    input(f"Level 30: {debug.get_strength()}\n")
    os.system(CLEAR)
    gen_starting_stats(debug, True)
    print(f"Base Stat 2\nLevel 1:{debug.get_res()}")
    lvl_up_bulk(debug, 9, True)
    print(f"Level 10: {debug.get_res()}")
    lvl_up_bulk(debug, 10, True)
    print(f"Level 20: {debug.get_res()}")
    lvl_up_bulk(debug, 10, True)
    input(f"Level 30: {debug.get_res()}")
    os.system(CLEAR)
    gen_starting_stats(debug, True)
    print(f"Base Stat 3\nLevel 1: {debug.get_agi()}")
    lvl_up_bulk(debug, 9, True)
    print(f"Level 10: {debug.get_agi()}")
    lvl_up_bulk(debug, 10, True)
    print(f"Level 20: {debug.get_agi()}")
    lvl_up_bulk(debug, 10, True)
    input(f"Level 30: {debug.get_agi()}")
    os.system(CLEAR)
    debug.Job = "warrior"
    gen_starting_stats(debug, True)
    print(f"Base Stat 4\nLevel 1: {debug.HP}")
    lvl_up_bulk(debug, 9, True)
    print(f"Level 10: {debug.HP}")
    lvl_up_bulk(debug, 10, True)
    print(f"Level 20: {debug.HP}")
    lvl_up_bulk(debug, 10, True)
    input(f"Level 30: {debug.HP}")

def roll_stat(modifier: int, start: bool):
    # start is true if it's the first level, used in gen_starting_stats
    # start is false if it's being used anywhere else, like in level_up
    if start:
        return (modifier * 4) + random.randrange(0, modifier + 1)
    if not start:
        return modifier + random.randrange(modifier, modifier + 4)


def gen_starting_stats(character: Entity, first_generation: bool = True):
    # Generates and distributes the starting stats of a character with any given job.
    # first_generation is True if it is the first time this character is being generated.
    # first_generation is False if it is not; i.e. changing to a new job.
    # If first_generation is False, the character retains their old abilities from other jobs and their level
    # However, their level is subtracted by 5
    global jobs, stats_order
    char_job = jobs[character.Job]
    character.MaxHP = roll_stat(char_job["stats"][0], True)
    character.MaxMP = roll_stat(char_job["stats"][1], True)
    character.STR = roll_stat(char_job["stats"][2], True)
    character.RES = roll_stat(char_job["stats"][3], True)
    character.MND = roll_stat(char_job["stats"][4], True)
    character.AGI = roll_stat(char_job["stats"][5], True)
    character.HP = character.MaxHP
    character.MP = character.MaxMP

    if first_generation:
        character.Level = 1
        character.Abilities = {}
        if 1 in char_job["abilities"]:
            character.Abilities[]
    elif not first_generation:
        old_level = character.Level
        new_level = old_level - 5 if old_level - 5 > 0 else 1
        character.Level = 1
        for _ in range(1, new_level):
            level_up(character, True)
    

def level_up(character: Entity, invisible: bool = False):
    global jobs, stats_order
    char_job = jobs[character.Job]
    char_learned_ability = False

    character.Level += 1
    character.MaxHP += roll_stat(char_job["stats"][0], False)
    character.MaxMP += roll_stat(char_job["stats"][1], False)
    character.STR += roll_stat(char_job["stats"][2], False)
    character.RES += roll_stat(char_job["stats"][3], False)
    character.MND += roll_stat(char_job["stats"][4], False)
    character.AGI += roll_stat(char_job["stats"][5], False)
    character.HP = character.MaxHP
    character.MP = character.MaxMP
    if character.Level in char_job["abilities"]:
        ability_to_learn = char_job["abilities"][character.Level]
        character.Abilities[ability_to_learn] = abilities[ability_to_learn]
        char_learned_ability = True
        #there is a better way to do this and I do not know it
    
    if not invisible:
        input(f"{character.Name} Leveled Up!")
        if char_learned_ability:
            input(f"{character.Name} learned {abilities[ability_to_learn]['name']}!")
        input(f"New stats:\n{character}\n")


def lvl_up_bulk(levelee, amount_to_lvl, hide_display: bool = True):
    for _ in range(amount_to_lvl):
        level_up(levelee, hide_display)

def generate_party_member(party_level, name = ""):
    # Creates a new PlayerCharacter entity object returns it  
    # For now, every new entity will just be named "Billie", but i'll need to add a random name mechanic later
    # Should have appropriate starting stats for the job it rolls 
    global jobs
    # get a name from the names list
    if name == "":    
        gen_char_name = random.choice(player_character_names)
        player_character_names.remove(gen_char_name)
    else:
        gen_char_name = name
    #make a new entity
    entities[f"{gen_char_name}"] = Entity({
        "Name": f"{gen_char_name}",
        "EntityType": "PlayerCharacter",
        "Job": "undecided",
        "Level": 1,
        "Max HP": 1,
        "Max MP": 1,
        "STR": 1,
        "RES": 1,
        "MND": 1,
        "AGI": 1,
        "HP": 1,
        "MP": 1,
        "Abilities": {}
    })
    # make it a variable so it is more readable
    generated_character = entities[f"{gen_char_name}"]
    # give it a job
    generated_character.Job = random.choice(list(jobs.keys()))
    # give it starting stats
    gen_starting_stats(generated_character, True)
    # level it up to be useful to the party
    for _ in range(1,party_level):
        level_up(generated_character, True)
    return generated_character

def present_player_party_members(player_party):
    os.system(CLEAR)
    if len(player_party) <= 3:
        party_level = find_party_level(player_party)
        print("You may choose one of two adventurers to join your party!")
        char_1 = generate_party_member(party_level)
        print(f"Option 1\n{char_1}\n")
        char_2 = generate_party_member(party_level)
        print(f"Option 2\n{char_2}\n")
        cmd = input("(INPUT) Which option do you choose to join your party?")
        while not isinstance(cmd, int):
            try:
                cmd = int(cmd)
            except ValueError:
                input("You must input a number!")
                cmd = input("(INPUT) Which option do you choose to join your party?")
        if cmd == 1:
            input(f"You chose {char_1.Name}! They join your party!")
            player_party.append(char_1)
            input(player_party)
        elif cmd == 2:
            input(f"You chose {char_2.Name}! They join your party!")
            player_party.append(char_2)
            input(player_party)
    elif len(player_party) > 3:
        input("You would be given the option to choose one of two party members, but your party is full!")

def generate_khorynn(chosen_job):
    Khorynn = generate_party_member(1, "Khorynn")
    Khorynn.Job = chosen_job
    Khorynn.EntityType = "Khorynn"
    gen_starting_stats(Khorynn, True)
    return Khorynn
    
    

###




