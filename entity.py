import os
import random
import copy
import item

from gamestate import GAME_STATE, print_with_conf

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
    # !!! IN ORDER !!!
    
    "warrior": {
        "stats": [4, 1, 3, 3, 1, 1],
        "dependencies": [],
        "abilities": {
            10: "skullcrusher"
        }
    },
    "just a guy": {
        "stats": [3, 1, 1, 2, 1, 3],
        "abilities": {
            1: "talk",
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
        "stats": [3, 1, 4, 3, 2, 3],
        "abilities": {
            10: "focus",
        }
    }
}

abilities = {

    # Ability Template

    # LevelLearned: Level that the class should learn the ability
    # NAME: Used to name the ability in the abilities dict inside an entity's stat sheet
    # ABILITYFUNC: Name of the function's ability. Case sensitive. Must be exact same as the function.
    # ABILITYTYPE: If it's NOT_OFFENSIVE, it can target things other than just enemies and must handle *everything*
    # in its function
    #             Meaning it has to deal damage if it deals damage and also check for death
    
    # LevelLearned:{"NAME": "AbilityName",
    # "AbilityName": {
    # "ABILITYFUNC": "name",
    # "ABILITYTYPE": "OFFENSIVE/NOT_OFFENSIVE"
    # }}
    
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
    "talk": {
        "name": "Talk",
        "callback": "talk_ability"
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
        self.Name = template["Name"]
        self.EntityType = template["EntityType"]
        self.Level = template["Level"]
        self.MaxHP = template["MaxHP"]
        self.MaxMP = template["MaxMP"]
        self.STR = template["STR"]
        self.RES = template["RES"]
        self.MND = template["MND"]
        self.AGI = template["AGI"]
        self.MP = self.MaxMP
        self.HP = self.MaxHP
        self.Abilities = template["Abilities"]
        if self.EntityType == "Enemy" or self.EntityType == "BossEnemy":
            self.EXP_Reward = template["EXP_Reward"]
            self.Money_Reward = template["Money_Reward"]
        if self.EntityType == "BossEnemy":
            self.BossLogic = template["BossLogic"]
            self.Phases = template["Phases"]
        elif self.EntityType == "PlayerCharacter" or self.EntityType == "Khorynn":
            self.ExperienceCount = 0
            self.Job = template["Job"]  
            self.JobEXP = 0
            self.MasteredJobs = []
            self.Items = []
            self.EquippedWeapon = item_data["no_equip"]
            self.EquippedArmor = item_data["no_equip"]
            self.EquippedAccessories = [item_data["no_equip"], item_data["no_equip"]]
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

    def __repr__(self):
        # makes it so that whenever the class object itself is printed, it prints the below instead!
        return f'Name: {self.Name}\nLevel: {self.Level}\nJob: {self.Job}\n\nHP: {self.HP}/{self.MaxHP}\nMP: {self.MP}/{self.MaxMP}\nSTR: {self.get_strength()}\nRES: {self.get_res()}\nMND: {self.get_mind()}\nAGI: {self.get_agi()}\n\n'

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
        "Money_Reward": 15,
        "Abilities": {}
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
        "Money_Reward": 15,
        "Abilities": {}

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
        "Money_Reward": 10,
        "Abilities": {}
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
        "Money_Reward": 5,
        "Abilities": {}
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
        "Money_Reward": 20,        
        "Abilities": {}
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
        "Money_Reward": 20,        
        "Abilities": {}
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
        "Money_Reward": 15,        
        "Abilities": {}
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
        "Money_Reward": 20,        
        "Abilities": {}        
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
        "Money_Reward": 50,        
        "Abilities": {}        
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
        "Money_Reward": 100,        
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
        "MaxHP": 800,
        "MaxMP": 30,
        "STR": 190,
        "RES": 90,
        "MND": 100,
        "AGI": 230,
        "EXP_Reward": 1,
        "Money_Reward": 0,        
        "Abilities": {}
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
        "Money_Reward": 100,        
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
    character.HP = character.MaxHP
    character.MP = character.MaxMP

    if first_generation:
        character.Level = 1
        character.Abilities = {}
        if 1 in char_job["abilities"]:
            ability_to_learn = char_job["abilities"][1]
            character.Abilities[ability_to_learn] = abilities[ability_to_learn]
    elif not first_generation:
        old_level = character.Level
        new_level = old_level - 3 if old_level - 3 > 0 else 1
        character.Level = 1
        level_up(character, (new_level - 1))
    

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
        character.HP = character.MaxHP
        character.MP = character.MaxMP

    for learnable_ability in char_job["abilities"]:
        ability_to_learn = char_job["abilities"][learnable_ability]
        if learnable_ability in range(0, (character.Level + 1)) and ability_to_learn not in character.Abilities:
            character.Abilities[ability_to_learn] = abilities[ability_to_learn]
            learned_abilities.append(abilities[ability_to_learn]) 
            char_learned_ability = True
            # there is a better way to do this and I do not know it
        
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


def generate_party_member(party_level, name=""):
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
    generated_character.Job = random.choice(list(jobs.keys()))
    # give it starting stats
    gen_starting_stats(generated_character, True)
    # level it up to be useful to the party
    level_up(generated_character, (party_level - 1), True)
    return generated_character


def present_player_party_members():
    os.system(CLEAR)
    if len(GAME_STATE.player_party) <= 3:
        party_level = find_party_level(GAME_STATE.player_party)
        print_with_conf("OLIVIA) OK, love, I've got two adventurers here for you. You can only take one.")
        char_1 = generate_party_member(party_level)
        print(f"Option 1\n{char_1}\n")
        char_2 = generate_party_member(party_level)
        print(f"Option 2\n{char_2}\n")
        cmd = input("OLIVIA) Which one are you taking, Khorynn?\n(print_with_conf) Which number option do you choose to join your party?")
        while not isinstance(cmd, int):
            try:
                cmd = int(cmd)
            except ValueError:
                print_with_conf("You must print_with_conf a number!")
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
        return MEGAKHORYNN
    Khorynn = generate_party_member(1, "Khorynn")
    Khorynn.Job = chosen_job
    Khorynn.EntityType = "Khorynn"
    gen_starting_stats(Khorynn, True)
    return Khorynn

def job_change_handler():
    os.system(CLEAR)
    selected_pc = None
    finished = False
    while selected_pc is None:
        print("Party:")
        for pc in GAME_STATE.player_party:
            print(pc.Name)
        cmd = input("\nOLIVIA) Which one of you is looking to change your job?\n(print_with_conf) print_with_conf the party member you would like to change the job of.")
        
        for pc in GAME_STATE.player_party:
            if cmd.lower().strip() == pc.Name.lower():
                selected_pc = pc
        if selected_pc is None:
            print_with_conf(f"OLIVIA) {cmd}... Mmmm, nope, I don't see a {cmd} with you. Let's try that again.")

    print_with_conf(f"OLIVIA) {selected_pc.Name}... Mmm, that one.")
    while not finished:
        print("OLIVIA) Here's a list of the jobs that one can take:")
        for job in jobs.keys():
            print(f"{job}, ", end = "")
        cmd = input(f"\nOLIVIA) Which job is {selected_pc.Name} here gonna take, Khorynn?").lower().strip()
        if cmd in jobs.keys():
            selected_pc.Job = cmd
            print_with_conf(f"OLIVIA) Alright, come here, {selected_pc.Name}. Look deep into my eyes.")
            print_with_conf(f"{selected_pc.Name} steps up towards Olivia. They stare into each other's eyes for a few seconds.")
            print_with_conf("Suddenly, Olivia grabs hold of them and starts shaking them around violently while shouting in their face!")
            print_with_conf(f"OLIVIA) YOU'RE A FUCKING {cmd.upper()}!!! BE A {cmd.upper()}!!! BE A {cmd.upper()} OR I'LL FUCKING KILL YOU RIGHT NOW!!!")
            for _ in range(3):
                print_with_conf(".")
            print_with_conf(f"{selected_pc.Name} successfully became a {cmd}!")
            gen_starting_stats(selected_pc, False)            
            finished = True
        else:
            print_with_conf(f"OLIVIA) Love, that's not on the list. You've gotta pick a job on the list.")
    

def party_place_handler():
    GAME_STATE.player_got_new_party_member = False
    GAME_STATE.player_changed_jobs = False
    player_is_finished = False

    while not player_is_finished:
        os.system(CLEAR)
        print("OLIVIA) Welcome to my party planning place.\n* What are you looking to be done today, love?")
        cmd = input("(INPUT) You think of whether you want to find a new 'party member' or 'change jobs'... or just 'leave'.  ").strip().lower()
        
        if cmd == "party member":
            if not GAME_STATE.player_got_new_party_member:
                present_player_party_members()
                GAME_STATE.player_got_new_party_member = True
            else:
                print_with_conf("OLIVIA) You already chose one of the two I gave you, Khorynn. There isn't anyone else to take.")
                
        elif cmd == "change jobs":
            if not GAME_STATE.player_changed_jobs:
                job_change_handler()
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
###             




