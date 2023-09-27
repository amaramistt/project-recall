import os
import uuid
import random
import copy
import item

from gamestate import GAME_STATE, print_with_conf, clear_terminal

CLEAR = 'cls' if os.name == 'nt' else 'clear'
item_data = item.get_item_data_map()

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
    #
    # mastery_difficulty indicates how much JEXP you need to master it
    # MD 1 means 4 (total) JEXP to ML1, 7 JEXP to ML2, 10 JEXP to ML3
    # MD 2 means 10 JEXP to ML1, 15 JEXP to ML2, 20 JEXP to ML3
    # MD 3 means 20 JEXP to ML1, 35 JEXP to ML2, 50 JEXP to ML3

    # Commented Job = iffy ideas, might not make it into the game
    
    #Tier 1 Jobs: No dependencies, must be mastered to unlock T2 Jobs
    
    "warrior": {
        "name": "Warrior",
        "stats": [4, 1, 3, 3, 1, 1],
        "dependencies": [],
        "mastery_difficulty": 1,
        "tier": 1,
        "abilities": {
            1: "skullcrusher"
        }
    },
    "just a guy": {
        "name": "Just A Guy",
        "stats": [3, 1, 1, 2, 1, 3],
        "dependencies": [],
        "mastery_difficulty": 1,
        "tier": 1,
        "abilities": {
            0: "talk",
            1: "slap"
        }
    },
    "mage": {
        "name": "Mage",
        "stats": [2, 3, 1, 2, 4, 3],
        "dependencies": [],
        "mastery_difficulty": 1,
        "tier": 1,
        "abilities": {
            0: "spark",
            3: "fireball"
        }
    },
    "priest": {
        "name": "Priest",
        "stats": [3, 2, 2, 2, 2, 2],
        "dependencies": [],
        "mastery_difficulty": 1,
        "tier": 1,
        "abilities": {
            1: "heal",
        }
    },
    "thief": {
        "name": "Thief",
        "stats": [3, 1, 3, 2, 1, 4],
        "dependencies": [],
        "mastery_difficulty": 1,
        "tier": 1,
        "abilities": {
            1: "steal"
        }
    },
    "monk": {
        "name": "Monk",
        "stats": [3, 1, 4, 3, 2, 3],
        "dependencies": [],
        "mastery_difficulty": 1,
        "tier": 1,
        "abilities": {
            1: "focus",
        }
    },
    
    # Tier Two Jobs: Have dependencies, are combined and stictly better versions of their dependencies 
    
    "spellblade": {
        "name": "Spellblade",
        "stats": [4,3,4,3,4,2],
        "dependencies": ["warrior", "mage"],
        "mastery_difficulty": 2,
        "tier": 2,
        "abilities": {}
    },
    "assassin": {
        "name": "Assassin",
        "stats": [3,3,5,2,3,4],
        "dependencies": ["warrior", "thief"],
        "mastery_difficulty": 2,
        "tier": 2,
        "abilities": {
            2: "assassinstab"
        }
    },
    "tactician": {
        "name": "Tactician",
        "stats": [4,2,3,3,5,3],
        "dependencies": ["warrior", "monk"],
        "mastery_difficulty": 2,
        "tier": 2,
        "abilities": {
            1: "analyze",
            2: "raisemorale",
        }
    },
    "sage": {
        "name": "Sage",
        "stats": [3,4,2,2,6,3],
        "dependencies": ["mage", "priest"],
        "mastery_difficulty": 2,
        "tier": 2,
        "abilities": {
            1: "rejuvenationprayer",
            2: "resilienceprayer",
            3: "meteor"
        }        
    },
    "trickster": {
        "name": "Trickster",
        "stats": [3,2,3,3,4,5],
        "dependencies": ["mage", "thief"],
        "mastery_difficulty": 2,
        "tier": 2,
        "abilities": {}        
    },
    # "warlock": {
    #     "stats": [],
    #     "dependencies": ["mage", "monk"],
    #     "abilities": {}        
    # },
    "reverend": {
        "name": "Reverend",
        "stats": [3,4,3,3,4,3],
        "dependencies": ["priest", "monk"],
        "mastery_difficulty": 2,
        "tier": 2,
        "abilities": {}        
    },
    "merchant": {
        "name": "Merchant",
        "stats": [4,2,3,3,4,2],
        "dependencies": ["just a guy"],
        "mastery_difficulty": 2,
        "tier": 2,
        "abilities": {} 
    },

    # Tier 3 Jobs

    "sorcerer supreme": {
        "name": "Sorcerer Supreme",
        "stats": [3,6,3,4,7,5],
        "dependencies": ["sage", "reverend"],
        "mastery_difficulty": 3,
        "tier": 3,
        "abilities": {} 
    },
    "champion": {
        "name": "Champion",
        "stats": [6,4,5,7,3,3],
        "dependencies": ["spellblade", "tactician", "assassin"],
        "mastery_difficulty": 3,
        "tier": 3,
        "abilities": {} 
    },
    "broker": {
        "name": "Broker",
        "stats": [4,2,3,3,4,2],
        "dependencies": ["merchant", "trickster"],
        "mastery_difficulty": 3,
        "tier": 3,
        "abilities": {} 
    },

# Tier 4 Job: Hero
    
    "hero": {
        "name": "Hero",
        "stats": [8,7,8,7,8,8],
        "dependencies": ["broker", "champion", "sorcerer supreme"],
        "mastery_difficulty": 3,
        "tier": 4,
        "abilities": {} 
    },
}

class Ability(object):
    def __init__(self, template):
        self.name = template.name
        self.callback = template.callback
        target = self.target
        type = self.type


abilities = {
    
    "focus": Ability({
        "name": "Focus",
        "callback": "focus",
        "target": "TARGET_SELF",
        "type": "BATTLE_ACTIVE",
    }),
    "fireball": Ability({
        "name": "Fireball",
        "callback": "forfireball",
        "type": "BATTLE_ACTIVE",
        "target": "TARGET_DIRECT"
    }),
    "spark": Ability({
        "name": "Spark",
        "callback": "spark",
        "type": "BATTLE_ACTIVE",
    }),
    "skullcrusher": Ability({
        "name": "Skull Crusher",
        "type": "BATTLE_ACTIVE",
        "callback": "skull_crusher",
        "target": "TARGET_VICTIM"
    }),
    "talk": Ability({
        "name": "Talk",
        "type": "BATTLE_ACTIVE",
        "callback": "talk_ability"
    }),
    "slap": Ability({
        "name": "Slap",
        "type": "BATTLE_ACTIVE",
        "callback": "slap",
        "target": "TARGET_SELF"
    }),
    "heal": Ability({
        "name": "Heal",
        "type": "OMNI_ACTIVE",
        "callback": "heal",
        "target": "TARGET_PARTY"
    }),
    "resilienceprayer": Ability({
        "name": "Resilience Prayer",
        "type": "BATTLE_ACTIVE",
        "callback": "resilience_prayer",
        "target": "TARGET_PARTY_ALL"
    }),
    "steal": Ability({
        "name": "Steal",
        "type": "BATTLE_ACTIVE",
        "callback": "steal",
        "target": None
    }),
    "rejuvenationprayer": Ability({
        "name": "Rejuvenation Prayer",
        "type": "OMNI_ACTIVE",
        "callback": "rejuvenation_prayer"
    }),
    "meteor": Ability({
        "name": "Meteor",
        "type": "BATTLE_ACTIVE",
        "callback": "meteor"
    }),
    "wisdomize": Ability({
        "name": "Wisdomize",
        "type": "BATTLE_ACTIVE",
        "callback": "wisdomize"
    }),
    "assassinstab": Ability({
        "name": "Assassin's Stab",
        "type": "BATTLE_ACTIVE",
        "callback": "assassinstab"
    }),
    "analyze": Ability({
        "name": "Analyze",
        "type": "BATTLE_ACTIVE",
        "callback": "analyze"
    }),
    "raisemorale": Ability({
        "name": "Raise Morale",
        "type": "BATTLE_ACTIVE",
        "callback": "raisemorale"
    }),
    
}


stats_order = {
    # required to let levelUp() or any function like it work at all
    1: "MaxHP",
    2: "MaxMP",
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
        self.id = None
        self.Name = template["Name"]
        self.EntityType = template["EntityType"]
        self.Level = template["Level"]
        self.MaxHP = template["MaxHP"]
        self.MaxMP = template["MaxMP"]
        self.STR = template["STR"]
        self.RES = template["RES"]
        self.MND = template["MND"]
        self.AGI = template["AGI"]
        self.MP = self.MaxHP
        self.HP = self.MaxHP
        self.Status = "HEALTHY"
        self.DoomCounter = 0
        self.Abilities = template["Abilities"]
        if self.EntityType == "Enemy" or self.EntityType == "BossEnemy":
            self.EXP_Reward = template["EXP_Reward"]
            self.Money_Reward = template["Money_Reward"]
            self.Item_Reward = template["Item_Reward"]
            self.AI = template["AI"]
            self.Phases = template["Phases"]
        elif self.EntityType == "PlayerCharacter" or self.EntityType == "Khorynn":
            self.ExperienceCount = 0
            self.Job = template["Job"]
            self.JobEXP = 0
            self.MasteryLevel = 0
            self.MasteredJobs = {}
            self.Items = []
            self.EquippedWeapon = item_data["no_equip"]
            self.EquippedArmor = item_data["no_equip"]
            self.EquippedAccessories = [item_data["no_equip"], item_data["no_equip"]]
            self.JobMasteryBonus = {
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            }
        self.StatChanges = {
            "STR": 0,
            "RES": 0,
            "MND": 0,
            "AGI": 0
        }
        self.EquipmentStats = {
            "MaxHP": 0,
            "MaxMP": 0,
            "STR": 0,
            "RES": 0,
            "MND": 0,
            "AGI": 0
        }

    @staticmethod
    def copy(other):
        clone = copy.deepcopy(other)
        clone.id = uuid.uuid4()
        return clone

    
    def __repr__(self):
        # makes it so that whenever the class object itself is printed, it prints the below instead!
        if self.EntityType == "Enemy" or self.EntityType == "BossEnemy":
            
            return f'Name: {self.Name}\nLevel: {self.Level}\n\nHP: {self.HP}/{self.get_max_hp()}\nMP: {self.MP}/{self.get_max_mp()}\nSTR: {self.get_strength()}\nRES: {self.get_res()}\nMND: {self.get_mind()}\nAGI: {self.get_agi()}\n\n'

        
        return f'Name: {self.Name}\nLevel: {self.Level}\nJob: {jobs[self.Job]["name"]}\n\nHP: {self.HP}/{self.get_max_hp()}\nMP: {self.MP}/{self.get_max_mp()}\nSTR: {self.get_strength()}\nRES: {self.get_res()}\nMND: {self.get_mind()}\nAGI: {self.get_agi()}\n\n'

        
    def get_max_hp(self):
        return int(self.MaxHP + self.EquipmentStats["MaxHP"])

                   
    def get_max_mp(self):
        return int(self.MaxMP + self.EquipmentStats["MaxMP"])

                   
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

    
    def calc_equipment_stats(self):
        for stat in self.EquipmentStats.keys():
            self.EquipmentStats[stat] = 0
        for stat in ["MaxHP", "MaxMP", "STR", "RES", "MND", "AGI"]:
            
            percent = sum([item.ItemStats[stat] for item in [self.EquippedWeapon, self.EquippedArmor] + self.EquippedAccessories]) / 100
            self.EquipmentStats[stat] = int(getattr(self, stat) * percent)


    def change_job(self, job_to_take):
        if self.EntityType != "PlayerCharacter" and self.EntityType != "Khorynn":
            input(f"change_job method called for non-friendly entity; returning")
            return
        self.Job = job_to_take
        if job_to_take not in self.MasteredJobs.keys():
            self.MasteredJobs[f"{job_to_take}"] = {
                "MASTERY_LEVEL": 0,
                "JOB_EXP": 0
            }
            self.MasteryLevel = 0
            self.JEXP = 0
        else:
            self.MasteryLevel = self.MasteredJobs[job_to_take]["MASTERY_LEVEL"]
            self.JEXP = self.MasteredJobs[job_to_take]["JOB_EXP"]

        if 0 in jobs[self.Job]["abilities"].keys() and jobs[self.Job]["abilities"][0] not in self.Abilities.keys():
                ability_to_learn = jobs[self.Job]["abilities"][0]
                self.Abilities[ability_to_learn] = abilities[ability_to_learn]

        gen_starting_stats(self, False)



entities = {
    "Khorynn": Entity({
        "Name": "Khorynn",
        "EntityType": "PlayerCharacter",
        "Job": "undecided",
        "Level": 1,
        "MaxHP": 1,
        "MaxMP": 1,
        "STR": 1,
        "RES": 1,
        "MND": 1,
        "AGI": 1,
        "Abilities": {}
    }),
    "MEGAKHORYNN": Entity({
        "Name": "Ultra Mega Debug Khorynn",
        "EntityType": "Khorynn",
        "Job": "warrior",
        "Level": 500,
        "MaxHP": 10000,
        "MaxMP": 10000,
        "STR": 10000,
        "RES": 10000,
        "MND": 10000,
        "AGI": 10000,
        "Abilities": {}
    }),
    "EnemyWizard": Entity({
        "Name": "Enraged Wizard",
        "EntityType": "Enemy",
        "Level": 1,
        "MaxHP": 12,
        "MaxMP": 12,
        "STR": 3,
        "RES": 7,
        "MND": 15,
        "AGI": 10,
        "EXP_Reward": 1,
        "Money_Reward": 5,
        "Item_Reward": {"MedicinalHerb": 30},
        "Abilities": {},
        "Phases": {},
        "AI": "ai_random"
    }),
    "EnemyWarrior": Entity({
        "Name": "Stalwart Warrior",
        "EntityType": "Enemy",
        "Level": 1,
        "MaxHP": 32,
        "MaxMP": 2,
        "STR": 14,
        "RES": 12,
        "MND": 3,
        "AGI": 4,
        "EXP_Reward": 1,
        "Money_Reward": 5,
        "Item_Reward": {"StrengthComplimentary": 20},
        "Abilities": {},
        "Phases": {},
        "AI": "ai_random"

    }),
    "Volakuma": Entity({
        "Name": "Volukuma",
        "EntityType": "Enemy",
        "Level": 1,
        "MaxHP": 20,
        "MaxMP": 2,
        "STR": 15,
        "RES": 8,
        "MND": 1,
        "AGI": 12,
        "EXP_Reward": 1,
        "Money_Reward": 3,
        "Item_Reward": {"AgilityComplimentary": 20},
        "Abilities": {},
        "Phases": {},
        "AI": "ai_random"
    }),
    "Slime": Entity({
        "Name": "Slime",
        "EntityType": "Enemy",
        "Level": 1,
        "MaxHP": 40,
        "MaxMP": 0,
        "STR": 11,
        "RES": 10,
        "MND": 1,
        "AGI": 6,
        "EXP_Reward": 1,
        "Money_Reward": 2,
        "Item_Reward": {"MedicinalHerb": 20},
        "Abilities": {},
        "Phases": {},
        "AI": "ai_random"
    }),
    
    "EnragedWarrior": Entity({
        "Name": "Enraged Warrior",
        "EntityType": "Enemy",
        "Level": 10,
        "MaxHP": 360,
        "MaxMP": 20,
        "STR": 105,
        "RES": 100,
        "MND": 30,
        "AGI": 30,
        "EXP_Reward": 1,
        "Money_Reward": 7,        
        "Item_Reward": {"StrengthComplimentary": 60},
        "Abilities": {},
        "Phases": {},
        "AI": "ai_random"
    }),
    "StalwartWizard": Entity({
        "Name": "Stalwart Wizard",
        "EntityType": "Enemy",
        "Level": 10,
        "MaxHP": 200,
        "MaxMP": 79,
        "STR": 30,
        "RES": 30,
        "MND": 80,
        "AGI": 70,
        "EXP_Reward": 1,
        "Money_Reward": 7,     
        "Item_Reward": {"MedicinalHerbBag": 30},
        "Abilities": {},
        "Phases": {},
        "AI": "ai_random"
    }),
    "DisgracedMonk": Entity({
        "Name": "Disgraced Monk",
        "EntityType": "Enemy",
        "Level": 20,
        "MaxHP": 500,
        "MaxMP": 100,
        "STR": 150,
        "RES": 110,
        "MND": 110,
        "AGI": 150,
        "EXP_Reward": 1,
        "Money_Reward": 5,    
        "Item_Reward": None,
        "Abilities": {},
        "Phases": {},
        "AI": "ai_random"
    }),
    "SorcererSupreme": Entity({
        "Name": "Sorcerer Supreme",
        "EntityType": "Enemy",
        "Level": 20,
        "MaxHP": 300,
        "MaxMP": 200,
        "STR": 30,
        "RES": 110,
        "MND": 200,
        "AGI": 140,
        "EXP_Reward": 1,
        "Money_Reward": 5,        
        "Item_Reward": {"MindComplimentary": 100},
        "Abilities": {},
        "Phases": {},
        "AI": "ai_random"
    }),
    "CraftyThief": Entity({
        "Name": "Crafty Thief",
        "EntityType": "Enemy",
        "Level": 20,
        "MaxHP": 460,
        "MaxMP": 80,
        "STR": 165,
        "RES": 80,
        "MND": 100,
        "AGI": 200,
        "EXP_Reward": 1,
        "Money_Reward": 10,     
        "Item_Reward": {"MerchantsCrest": 10},
        "Abilities": {},      
        "Phases": {},
        "AI": "ai_random"
    }),
    "GelatinousKing": Entity({
        "Name": "Gelatinous King",
        "EntityType": "BossEnemy",
        "Level": 30,
        "MaxHP": 6000,
        "MaxMP": 50,
        "STR": 270,
        "RES": 160,
        "MND": 100,
        "AGI": 210,
        "EXP_Reward": 1,
        "Money_Reward": 25,      
        "Item_Reward": {"GelatinousCrown": 100},
        "AI": "king_slime",
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
        "MaxHP": 800,
        "MaxMP": 30,
        "STR": 190,
        "RES": 90,
        "MND": 100,
        "AGI": 230,
        "EXP_Reward": 1,
        "Money_Reward": 0,   
        "Item_Reward": None,
        "Abilities": {},
        "Phases": {},
        "AI": "ai_random"
    }),
    "StoneGolem": Entity({
        "Name": "Stone Golem",
        "EntityType": "BossEnemy",
        "Level": 30,
        "MaxHP": 2500,
        "MaxMP": 0,
        "STR": 320,
        "RES": 210,
        "MND": 2,
        "AGI": 80,
        "EXP_Reward": 1,
        "Money_Reward": 25,      
        "Item_Reward": {"GolemHeart": 100},
        "AI": "stone_golem",
        "Phases": {
            "Phase 2": False
        },
        "Abilities": {}
    }),
    "InsurgentMessiah": Entity({
        "Name": "Insurgent Messiah",
        "EntityType": "BossEnemy",
        "Level": 30,
        "MaxHP": 4000,
        "MaxMP": 300,
        "STR": 150,
        "RES": 180,
        "MND": 290,
        "AGI": 300,
        "EXP_Reward": 1,
        "Money_Reward": 25,      
        "Item_Reward": {"MessiahsCloak": 100},
        "AI": "insurgent_messiah",
        "Phases": {
            "Summon Phase": False
        },
        "Abilities": {}
    }),
    "InsurgentGrunt": Entity({
        "Name": "Insurgent Grunt",
        "EntityType": "Enemy",
        "Level": 30,
        "MaxHP": 500,
        "MaxMP": 30,
        "STR": 100,
        "RES": 120,
        "MND": 240,
        "AGI": 200,
        "EXP_Reward": 1,
        "Money_Reward": 0,   
        "Item_Reward": None,
        "Abilities": {},
        "Phases": {},
        "AI": "ai_random"
    }),
    "TrainingDummy": Entity({
        "Name": "Training Dummy",
        "EntityType": "Enemy",
        "Level": 1,
        "MaxHP": 5000000000000000000000000000,
        "MaxMP": 0,
        "STR": 0,
        "RES": 0,
        "MND": 0,
        "AGI": 0,
        "EXP_Reward": 1,
        "Money_Reward": 0,   
        "Item_Reward": None,
        "Abilities": {},
        "Phases": {},
        "AI": "ai_random"
    }),
    "RhysBoss": Entity({
        "Name": "Rhys",
        "EntityType": "BossEnemy",
        "Level": 30,
        "MaxHP": 5000,
        "MaxMP": 500,
        "STR": 310,
        "RES": 200,
        "MND": 200,
        "AGI": 310,
        "EXP_Reward": 1,
        "Money_Reward": 25,      
        "Item_Reward": {"RhysBossDagger": 100},
        "AI": "rhys_boss_logic",
        "Phases": {
            "Blade Enchanted": False,
            "Phase 2": False,
            "Phase 3": False,
            "Wounded": False
        },
        "Abilities": {}
    }),
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
    character.MaxHP = roll_stat(char_job["stats"][0], True) * 2
    character.MaxMP = roll_stat(char_job["stats"][1], True)
    character.STR = roll_stat(char_job["stats"][2], True)
    character.RES = roll_stat(char_job["stats"][3], True)
    character.MND = roll_stat(char_job["stats"][4], True)
    character.AGI = roll_stat(char_job["stats"][5], True)
    character.HP = character.get_max_hp()
    character.MP = character.get_max_mp()

    if first_generation:
        character.Level = 1
        character.Abilities = {}
        if 1 in char_job["abilities"]:
            ability_to_learn = char_job["abilities"][1]
            character.Abilities[ability_to_learn] = abilities[ability_to_learn]
    elif not first_generation:
        old_level = character.Level
        character.Level = 1
        level_up(character, (old_level - 1), True)
    

def level_up(character: Entity, times_to_level: int = 1, invisible: bool = False):
    global jobs, stats_order
    char_job = jobs[character.Job]
    learned_abilities = []
    char_learned_ability = False

    for _ in range(times_to_level):
        character.Level += 1
        character.MaxHP += roll_stat(char_job["stats"][0], False) * 2
        character.MaxMP += roll_stat(char_job["stats"][1], False)
        character.STR += roll_stat(char_job["stats"][2], False)
        character.RES += roll_stat(char_job["stats"][3], False)
        character.MND += roll_stat(char_job["stats"][4], False)
        character.AGI += roll_stat(char_job["stats"][5], False)
        character.HP = character.get_max_hp()
        character.MP = character.get_max_mp()

    if not invisible:
        if times_to_level > 1:
            print_with_conf(f"{character.Name} Leveled Up {times_to_level} times!")
        else:
            print_with_conf(f"{character.Name} Leveled Up!")
        if char_learned_ability:
            print(f"{character.Name} learned ", end="")
            if len(learned_abilities) > 1:
                for ability in learned_abilities:
                    print(f"{ability['name']} and ", end="")
                print_with_conf("\b\b \b\b b\b \b\b \b\b \b\b!")
            else:
                print_with_conf(f"{learned_abilities[0]['name']}!")
        print_with_conf(f"New stats:\n{character}\n")


def check_for_level_up(character):
    level = character.Level
    


def check_for_mastery_level_up(character):
    mastery_level = character.MasteryLevel
    mastery_difficulty = jobs[character.Job]["mastery_difficulty"]
    
    if mastery_difficulty > 3:
        mastery_difficulty = 3
    if mastery_difficulty < 1:
        mastery_difficulty = 1
    if mastery_level == 3:
        return
        
    if mastery_difficulty == 1:
        if mastery_level <= 2 and character.JEXP >= 10:
            give_mastery_level_up(character, 3)        
        elif mastery_level <= 1 and character.JEXP >= 7:
            give_mastery_level_up(character, 2)
        elif mastery_level == 0 and character.JEXP >= 4:
            give_mastery_level_up(character, 1)
    if mastery_difficulty == 2:
        if mastery_level <= 2 and character.JEXP >= 20:
            give_mastery_level_up(character, 3)        
        elif mastery_level <= 1 and character.JEXP >= 15:
            give_mastery_level_up(character, 2)
        elif mastery_level == 0 and character.JEXP >= 10:
            give_mastery_level_up(character, 1)   
    if mastery_difficulty == 3:
        if mastery_level <= 2 and character.JEXP >= 50:
            give_mastery_level_up(character, 3)        
        elif mastery_level <= 1 and character.JEXP >= 35:
            give_mastery_level_up(character, 2)
        elif mastery_level == 0 and character.JEXP >= 20:
            give_mastery_level_up(character, 1)

            
def give_mastery_level_up(character, ML_to_be = None):
    if ML_to_be is None:
        ML_to_be = character.MasteryLevel + 1
    print_with_conf(f"{character.Name} increased their Mastery Level!")
    character.MasteryLevel = ML_to_be
    character.MasteredJobs[character.Job]["MASTERY_LEVEL"] = ML_to_be
    for learnable_ability in jobs[character.Job]["abilities"]:
        ability_to_learn = jobs[character.Job]["abilities"][learnable_ability]
        if learnable_ability in range(0, (character.MasteryLevel + 1)) and ability_to_learn not in character.Abilities:
            character.Abilities[ability_to_learn] = abilities[ability_to_learn]
            print_with_conf(f"{character.Name} learned {ability_to_learn}!")
    character.MasteredJobs[character.Job]["JOB_EXP"] = character.JEXP
    print_with_conf(f"They are now Mastery Level {character.MasteryLevel}!")
    if character.MasteryLevel == 3:
        print_with_conf(f"{character.Name} has mastered the way of the {jobs[character.Job]['name']}!!!")
    

def generate_party_member(party_level, name=""):
    # Creates a new PlayerCharacter entity object returns it  
    if name == "":    
        gen_char_name = random.choice(player_character_names)
        player_character_names.remove(gen_char_name)
    else:
        gen_char_name = name
    # make a new entity
    entities[f"{gen_char_name}"] = Entity({
        "Name": f"{gen_char_name}",
        "EntityType": "PlayerCharacter",
        "Job": "undecided",
        "Level": 1,
        "MaxHP": 1,
        "MaxMP": 1,
        "STR": 1,
        "RES": 1,
        "MND": 1,
        "AGI": 1,
        "Abilities": {}
    })
    # make it a variable so it is more readable
    generated_character = entities[f"{gen_char_name}"]
    # give it a job
    generated_character.change_job(random.choice(list(jobs.keys())))
    # give it starting stats
    gen_starting_stats(generated_character, True)
    # level it up to be useful to the party
    level_up(generated_character, (party_level - 1), True)
    return generated_character


def present_player_party_members():
    clear_terminal()
    if len(GAME_STATE.player_party) <= 3:
        party_level = find_party_level(GAME_STATE.player_party)
        print_with_conf("OLIVIA) OK, love, I've got two adventurers here for you. You can only take one.")
        char_1 = generate_party_member(party_level)
        print(f"Option 1\n{char_1}\n")
        char_2 = generate_party_member(party_level)
        print(f"Option 2\n{char_2}\n")
        cmd = input("OLIVIA) Which one are you taking, Khorynn?\n(INPUT) Which number option do you choose to join your party?")
        while not isinstance(cmd, int):
            try:
                cmd = int(cmd)
            except ValueError:
                print_with_conf("You must input a number!")
                cmd = input("(INPUT) Which number option do you choose to join your party?")
        if cmd == 1:
            print_with_conf(f"You chose {char_1.Name}! They join your party!")
            GAME_STATE.player_party.append(char_1)
            print_with_conf(GAME_STATE.player_party)
        elif cmd == 2:
            print_with_conf(f"You chose {char_2.Name}! They join your party!")
            GAME_STATE.player_party.append(char_2)
            print_with_conf(GAME_STATE.player_party)
    elif len(GAME_STATE.player_party) > 3:
        print_with_conf("OLIVIA) Sorry, love, but you're already running with a party of four. Can't give you any more in good concience.")
        print_with_conf("OLIVIA) If one of them kicks it, come back and I'll have two wonderful options for you.")


def generate_khorynn(chosen_job):
    if GAME_STATE.debug_mode:
        MEGAKHORYNN = copy.deepcopy(entities["MEGAKHORYNN"])
        MEGAKHORYNN.change_job("hero")
        return MEGAKHORYNN
    Khorynn = generate_party_member(1, "Khorynn")
    Khorynn.change_job(chosen_job)
    Khorynn.EntityType = "Khorynn"
    gen_starting_stats(Khorynn, True)
    return Khorynn

def job_change_handler():
    clear_terminal()
    selected_pc = None
    finished = False
    
    print("Party:\n")
    for _ in range(len(GAME_STATE.player_party)):
        print(f"Party Member {_ + 1}: {GAME_STATE.player_party[_].Name}\nJob: {jobs[GAME_STATE.player_party[_].Job]['name']}\n")

    print("\n\n")
    cmd = input("\nOLIVIA) Which one of you is looking to change your job?\nInput the numbered party member you would like to change the job of.\n(INPUT NUM) Input anything else to go back.    ")
    
    try:
        cmd = int(cmd) - 1 if int(cmd) - 1 > -1 else 0
        cmd = len(GAME_STATE.player_party) - 1 if cmd >= len(GAME_STATE.player_party) else cmd
        selected_pc = GAME_STATE.player_party[cmd]
    except ValueError:
        return "backed_out"

    clear_terminal()
    print_with_conf(f"OLIVIA) {selected_pc.Name}... Mmm, that one.")
    
    while not finished:
        print("OLIVIA) Here's a list of the jobs that one can take:")
        available_jobs = find_available_jobs(selected_pc)
        for job in available_jobs:
            print(jobs[job]['name'])
        cmd = input(f"\nOLIVIA) Which job is {selected_pc.Name} here gonna take, Khorynn?\n(INPUT JOB) Input anything else to go back.    ").lower().strip()

        
        if cmd in [x.lower() for x in list(jobs.keys())]:
            job_chosen = cmd
            if job_chosen in selected_pc.MasteredJobs:
                cmd2 = input(f"OLIVIA) Hold on, love. They've already mastered that job. They can't get anything more out of it. You still want to switch?\n(INPUT Y/N)    ").strip().lower()
                if cmd2 != "y":
                    return "backed_out"
                     

            clear_terminal()
            print_with_conf(f"OLIVIA) Alright, come here, {selected_pc.Name}. Look deep into my eyes.")
            print_with_conf(f"{selected_pc.Name} steps up towards Olivia. They stare into each other's eyes for a few seconds.")
            print_with_conf("Suddenly, Olivia grabs hold of them and starts shaking them around violently while shouting in their face!")
            print_with_conf(f"OLIVIA) YOU'RE A FUCKING {job_chosen.upper()}!!! BE A {job_chosen.upper()}!!! BE A {job_chosen.upper()} OR I'LL FUCKING KILL YOU RIGHT NOW!!!")
            for _ in range(3):
                print_with_conf(".")
            print_with_conf(f"{selected_pc.Name} successfully became a {job_chosen}!")
            selected_pc.change_job(job_chosen)        
            finished = True
        else:
            return "backed_out"
    

def party_place_handler():
    GAME_STATE.player_got_new_party_member = False
    GAME_STATE.player_changed_jobs = False
    player_is_finished = False

    while not player_is_finished:
        clear_terminal()
        print("OLIVIA) Welcome to my party planning place.\n* What are you looking to be done today, love?")
        cmd = input("(INPUT) You think of whether you want to find a new 'party member' or 'change jobs'... or just 'leave'.  ").strip().lower()
        
        if cmd == "party member":
            if not GAME_STATE.player_got_new_party_member:
                if present_player_party_members() != "backed_out":
                    GAME_STATE.player_got_new_party_member = True
            else:
                print_with_conf("OLIVIA) You already chose one of the two I gave you, Khorynn. There isn't anyone else to take.")
                
        elif cmd == "change jobs":
            if not GAME_STATE.player_changed_jobs:
                if job_change_handler() == "backed_out":
                    GAME_STATE.player_changed_jobs = False
                else:
                    GAME_STATE.player_changed_jobs = True
            else:
                print_with_conf("OLIVIA) Khorynn, honey, you already changed jobs. You know I don't have the energy to do that again.")
                
        elif cmd == "leave":
            if GAME_STATE.player_changed_jobs and GAME_STATE.player_got_new_party_member:
                print_with_conf("OLIVIA) Godspeed, Khorynn. May nothing stand in your way.")
                player_is_finished = True
            else:
                conf = input("OLIVIA) Hey, Khorynn! Leaving so soon? You didn't do everything you could, did you mean to leave?\n(INPUT Y/N)   ").lower().strip()
                if conf == "y":
                    print_with_conf("OLIVIA) ...Alright. Godspeed, Khorynn. May nothing stand in your way.")
                    player_is_finished = True
                else:
                    print_with_conf("OLIVIA) Ah! Alright, where was I...?")


def find_available_jobs(character = None):
    available_jobs = []
    if character == None:
        for each_job in jobs:
            if jobs[each_job]["dependencies"] == []:
                available_jobs.append(each_job)
                continue
        return available_jobs
    mastery_data = character.MasteredJobs
    guy_job_mastered = False
    
    if "just a guy" in mastery_data.keys():
        if mastery_data["just a guy"]["MASTERY_LEVEL"] == 3:
            guy_job_mastered = True
    
    for each_job in jobs:
        job_dependencies = jobs[each_job]["dependencies"]
        dependencies_met = None

        if job_dependencies == []:
            available_jobs.append(each_job)
            continue

        if jobs[each_job]["tier"] == 2:
            if guy_job_mastered:
                available_jobs.append(each_job)
                continue

        
        for dependency in job_dependencies:
            if dependencies_met == False:
                continue
                
            if dependency in list(mastery_data.keys()):
                if mastery_data[dependency]["MASTERY_LEVEL"] == 3:
                    dependencies_met = True
                else:
                    dependencies_met = False
            else:
                dependencies_met = False
        
        if dependencies_met:
            available_jobs.append(each_job)
            
    return available_jobs