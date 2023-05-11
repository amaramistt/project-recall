# To-Do List
# 1) Create a system in which enemies can be spawned from a pool of encounters only available at certain points of the game

# 2) Create a system in which the player may exist outside of battle, so that items/equipment/accessories/menuing
#    may be implemented and debugged
# 3) Create a system in which passive, consumable, and non-consumable items can be seamlessly acquired and used,
#    preferably complete with item pools and broken synergies :3
# 4) Create a system where I can create spell functions (a la SkullCracker()) in a different file and import
#    them for use without too much rewriting of code
# NOT-SO-DISTANT FUTURE) Start using pygame/libtcod and work on room generation and UI


import os
import sys
import subprocess
import random
import copy
from entity import Entity, find_turn_order, find_party_level

CLEAR = 'cls' if os.name == 'nt' else 'clear'
king_slime_spawn_phase_1_happened = False
king_slime_spawn_phase_2_happened = False
king_slime_spawn_phase_3_happened = False
king_slime_spawn_phase_4_happened = False

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
    })
}
# A Disgraced Monk, Sorcerer Supreme, and Crafty Thief draw near!
player_party = []

# JOB STATS SYNTAX
# Goes from 1 to 6
# 1 means dogshit and 6 means top of the line
# stats go HP > MP > STR > RES > MND > AGI
# !!! IN ORDER !!!
jobs = {
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

    # "sage": {"stats": [3, 4, 1, 3, 5, 4],
    #         "dependencies": ["mage", "priest"],
    #         "abilities": {}},
}

# key = ability ID
# value = ability definition

# targets = [
#     "TARGET_SELF",       # the character
#     "TARGET_MOB_ANY",    # any non-friendly target
#     "TARGET_MOB_ALL",    # all non-friendly
#     "TARGET_DIRECT",     # victim must be chosen explicitly, foe/friendly not a factor with this target style
#     "TARGET_PARTY",      # victim must be chosen, must be in player's party
#     "TARGET_PARTY_ALL",  # entire party
# ]

abilities = {
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

def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])

def debug_starting_stats():
    os.system(CLEAR)
    debug = generate_party_member(1)
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

def lvl_up_bulk(levelee, amount_to_lvl, hide_display: bool = True):
    for _ in range(amount_to_lvl):
        level_up(levelee, hide_display)
        


def print_tutorial():
    print("Basic Combat Tutorial")
    input("In this tutorial, you will learn the basics of combat.")
    os.system(CLEAR)
    print("STATISTICS")
    input("Your characters' statistics are the backbone of combat. There are several stats that directly affect the effectiveness of your units.")
    input("HP or Health Points: How much damage one can take before dying.")
    input("MP or Magic Points: Spells and Abilities use MP to activate.")
    input("STR or Strength: How effective one is at attacking directly with a weapon.")
    input("RES or Resilience: How effective one is at taking hits.")
    input("MND or Mind: How effective one is at using magic and resisting urges.")
    input("AGI or Agility: How fast one is.")
    os.system(CLEAR)
    print("JOBS")
    input("Jobs affect a character's stats and learnable abilities.")
    input("There will be more jobs with more in-depth mechanics later, but these are the jobs available to you currently.")
    input("Warrior: Big, strong, tanky unit that takes hits and deals damage. However, they're a little slow, both literally and figuratively.")
    input("Mage: Absolute powerhouses that die if you look at them too hard. Abuse their powerful magic and keep them safe!")
    input("Just A Guy: I don't know how they got here, they are literally just normal humans. Extremely weak.")
    input("Thief: Generalists with exceptional speed. Gets things done and gets things done before anyone else.")
    input("Monk: Fast, decently bulky physical fighters that don't need weapons to kill. Say your prayers.")
    input("Priest: Squishy backliners that support their allies with healing and buffs. Keep them safe and they'll return the favor!")
    os.system(CLEAR)
    print("COMMANDS")
    input("When it is a player characters' turn in battle, you will be asked to input a command.")
    input("A list of available commands will follow.")
    input("Attack: Initiate a basic attack on a selected enemy.")
    input("Abilities: Initiates the process of using abilities. Most of them use MP!")
    input("Pass: Passes your turn. Your character will not act that turn.")
    os.system(CLEAR)
    print("BLOODTHIRSTINESS")
    input("Whenever a character kills an opposing character, they immediately take another turn.")
    input("Both enemies and player characters are affected by bloodthirstiness.")
    input("In the extra turn, you may *only* attack, with either a basic attack or with a spell.")
    input("No entity may take two bloodthirsty turns in a row.")
    os.system(CLEAR)
    input("More to come in the future! Good luck!")
    os.system(CLEAR)


def title_screen():
    global player_party
    player_party = []
    os.system(CLEAR)
    print("                P R O J E C T    R E C A L L")
    input("                    Press Enter To Start    ")
    os.system(CLEAR)
    print("NEW GAME - TUTORIAL - BACK")
    cmd = input("Choose. ").strip().lower()
    if cmd == "new game":
        run_began = begin_run_handler()
        return run_began
    elif cmd == "tutorial":
        print_tutorial()
        return None
    elif cmd == "back":
        return None
    elif cmd == "debug":
        debug_starting_stats()
        return None
    else:
        input("Invalid input.")
        return None


###


def begin_run_handler():
    global jobs
    global player_party
    os.system(CLEAR)
    # before anything, get the seed
    seed = input("Please input your seed (Leave blank for a random one!)")
    if seed == "":
        seed = random.randint(10000000, 99999999)
        random.seed(seed)
    else:
        random.seed(seed)

    # start with a selected job
    print(f"Jobs available for selection: ", end="")
    for job in jobs.keys():
        print(f"{job}, ", end = "")
        #HOW DO I MAKE THIS GRAMMATICALLY CORRECT :((((((
    char_job = input("\nWhat job should Khorynn start with? ").strip().lower()
    if char_job in jobs:
        entities["Khorynn"].Job = char_job
        player_party.append(entities["Khorynn"])
        # generate its starting stats
        gen_starting_stats(player_party[0], True)
        input(f"Character sheet\n{player_party[0]}")
        return True
    else:
        input("That is not an available job!")
        begin_run_handler()
        return None


def load_cutscene(cutscene_ID):
    # IN CONSTRUCTION 
    # finds the cutscene ID from a large database of cutscenes
    # has some system in which this function could interpret some text as instructions
    # i.e. if i call load_cutscene(5) it would load cutscene 5 and make sure that each character moves and speaks the correct way
    # i.e. if cutscene ID 5 was one line saying "(Khorynn)(FACE_LEFT)'Are you serious?'", Khorynn would face left and say 'Are you serious?'
    # gonna have to get real used to using for x in y :3
    pass


###


# 1 -> 4-5 start
# 2 -> 8-10 start
# 3 -> 12-15 start
# 4 -> 16-20 start
def roll_stat(modifier: int, start: bool = False):
    # start is true if it's the first level, used in gen_starting_stats
    # start is false if it's being used anywhere else, like in level_up
    if start:
        return (modifier * 4) + random.randrange(0, modifier + 1)
    if not start:
        return modifier + random.randrange(modifier, modifier + 4)


def gen_starting_stats(character: Entity, first_generation: bool):
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
    elif not first_generation:
        old_level = character.Level
        new_level = old_level - 5 if old_level - 5 > 0 else 1
        character.Level = 1
        for _ in range(1, new_level):
            level_up(character, True)
    

def level_up(character: Entity, suppress_output: bool = False):
    global jobs, stats_order
    char_job = jobs[character.Job]
    ability_messages = ""

    character.Level += 1
    character.MaxHP += roll_stat(char_job["stats"][0])
    character.MaxMP += roll_stat(char_job["stats"][1])
    character.STR += roll_stat(char_job["stats"][2])
    character.RES += roll_stat(char_job["stats"][3])
    character.MND += roll_stat(char_job["stats"][4])
    character.AGI += roll_stat(char_job["stats"][5])
    character.HP = character.MaxHP
    character.MP = character.MaxMP
    if character.Level in char_job["abilities"]:
        ability_to_learn = char_job["abilities"][character.Level]
        character.Abilities[ability_to_learn] = abilities[ability_to_learn]
        ability_messages = f"{character.Name} learned {abilities[ability_to_learn]['name']}!"
    
    if not suppress_output:
        input(f"{character.Name} Leveled Up!\n{ability_messages}")
        input(f"New stats:\n{character}\n")


def generate_party_member(party_level):
    # Creates a new PlayerCharacter entity object returns it  
    # For now, every new entity will just be named "Billie", but i'll need to add a random name mechanic later
    # Should have appropriate starting stats for the job it rolls 
    global jobs
    # get a name from the names list
    gen_char_name = random.choice(player_character_names)
    player_character_names.remove(gen_char_name)
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
    gen_starting_stats(generated_character, first_generation=True)
    # level it up to be useful to the party
    for _ in range(1,party_level):
        level_up(generated_character, suppress_output=True)
    return generated_character


def present_player_party_members(party_level):
    os.system(CLEAR)

    if len(player_party) <= 3:
        input(f"You may choose one of two adventurers to join your party!")
        char_1 = generate_party_member(party_level)
        print(f"Option 1\n{char_1}\n")
        char_2 = generate_party_member(party_level)
        print(f"Option 2\n{char_2}\n")
        cmd = input("(INPUT) Which option do you choose to join your party?")
        done = False
        while not isinstance(cmd, int) and not done:
            try:
                cmd = int(cmd)
            except ValueError:
                input("You must input a number!")
                cmd = input("(INPUT) Which option do you choose to join your party?")
            if cmd == 1:
                if len(player_party) <= 3:
                    input(f"You chose {char_1.Name}! They join your party!")
                    player_party.append(char_1)
                    input(player_party)
            elif cmd == 2:
                input(f"You chose {char_2.Name}! They join your party!")
                player_party.append(char_2)
                input(player_party)
                done = True
            elif cmd == 3:
                input(f"You chose the secret, third option of going solo. YOLO!")
                done = True
            else:
                input("You seem to have misinputted. Please input 1 or 2 relative to the option you want to choose.")
    elif len(player_party) > 3:
        input("You are given the option to choose one of two party members, but your party is full!")
        input("You leave in an awkward silence.")

# \/\/ NEEDS REWORK \/\/
def initiate_battle(player_party, enemy_pool):
    #For now, I'm just going to have it call run_encounter similarly to how it would will in future
    global entities
    os.system(CLEAR)
    input("The party encounters a group of enemies!")
    if enemy_pool == 1:
        EnragedWizard = copy.deepcopy(entities["EnemyWizard"])
        StalwartWarrior = copy.deepcopy(entities["EnemyWarrior"])
        input("An Enraged Wizard and a Stalwart Warrior draw near!")
        return run_encounter(player_party, [EnragedWizard, StalwartWarrior])
    elif enemy_pool == 2:
        EnragedWarrior = copy.deepcopy(entities["EnragedWarrior"])
        StalwartWizard = copy.deepcopy(entities["StalwartWizard"])
        input("An Enraged Warrior and a Stalwart Wizard draw near!")
        return run_encounter(player_party, [EnragedWarrior, StalwartWizard])
    elif enemy_pool == 3:
        DisgracedMonk = copy.deepcopy(entities["DisgracedMonk"])
        SorcererSupreme = copy.deepcopy(entities["SorcererSupreme"])
        CraftyThief = copy.deepcopy(entities["CraftyThief"])
        input("A Disgraced Monk, Sorcerer Supreme, and Crafty Thief draw near!")
        return run_encounter(player_party, [DisgracedMonk, SorcererSupreme, CraftyThief])
    elif enemy_pool == 4:
        GelatinousKing = copy.deepcopy(entities["GelatinousKing"])
        input("You face down the boss of the floor; the Gelatinous King!")
        return run_encounter(player_party, [GelatinousKing])
    else:
        input("You didn't, actually, because THE DEV FORGOT TO SET THE ENEMY POOL LIKE A DUMBASS!")
        return False
        



def find_target(amount_of_enemies):
    target = input("Which numbered enemy would you like to attack?")
    while not isinstance(target, int):
        try:
            target = int(target)
        except ValueError:
            print("Please input a number correlated to the enemy.")
            input("Don't input anything other than a number!")
            target = input("Which numbered enemy would you like to attack?")
    target -= 1
    if target < 0:
        target = 0
    elif target > amount_of_enemies:
        target = amount_of_enemies - 1
    return target


def run_encounter(friendlies: list[Entity], enemies: list[Entity]):
    initiative_list = find_turn_order(friendlies, enemies)
    os.system(CLEAR)
    party_wiped = False
    enemies_are_dead = False
    enemies_spawned = []
    for enemy in enemies:
        enemies_spawned.append(enemy)
    bloodthirsty_check = None
    
    while True:
        # go through this process for every entity
        for actor in initiative_list:
            os.system(CLEAR)
            # Check to see if the battle's over BEFORE bloodthirsty/AFTER normal turn
            if check_if_battle_won(friendlies,enemies) is not None:
                if not check_if_battle_won(friendlies, enemies):
                    party_wiped = True
                    break
                elif check_if_battle_won(friendlies, enemies):
                    enemies_are_dead = True
                    break
            
            # Check if the previous turn resulted in someone going bloodthirsty
            if bloodthirsty_check is not None:
                if bloodthirsty_check.EntityType == "PlayerCharacter":
                    input(f"{bloodthirsty_check.Name} is bloodthirsty!")
                    pc_turn_handler(friendlies, bloodthirsty_check, enemies, initiative_list, True)
                    input(f"{bloodthirsty_check.Name}'s primal rage dims!")
                    os.system(CLEAR)
                elif bloodthirsty_check.EntityType == "Enemy":
                    input(f"{bloodthirsty_check.Name} is bloodthirsty!")
                    enemy_AI(friendlies, bloodthirsty_check, initiative_list)
                    input(f"{bloodthirsty_check.Name}'s primal rage dims!")
                    os.system(CLEAR)
                elif bloodthirsty_check.EntityType == "BossEnemy":
                    input(f"{bloodthirsty_check.Name} is bloodthirsty!!")
                    logic_to_reference = globals()[actor.BossLogic]
                    logic_to_reference(friendlies, actor, enemies, initiative_list, enemies_spawned)
                    input(f"{bloodthirsty_check.Name}'s primal rage dims!")
                    os.system(CLEAR)
                bloodthirsty_check = None

            # Check if the battle's over BEFORE normal turn/AFTER bloodthirsty
            if check_if_battle_won(friendlies,enemies) is not None:
                if not check_if_battle_won(friendlies, enemies):
                    party_wiped = True
                    break
                elif check_if_battle_won(friendlies, enemies):
                    enemies_are_dead = True
                    break
                
            # Start of entity's turn
            input(f"It's {actor.Name}'s turn!")
            
            # Check whether entity is a PC
            if actor.EntityType == "PlayerCharacter":
                # do PC shit
                bloodthirsty_check = pc_turn_handler(friendlies, actor, enemies, initiative_list, False)
    
            # check if entity is an enemy
            if actor.EntityType == "Enemy":
                # do enemy shit
                bloodthirsty_check = enemy_AI(friendlies, actor, initiative_list)

            if actor.EntityType == "BossEnemy":
                logic_to_reference = globals()[actor.BossLogic]
                bloodthirsty_check = logic_to_reference(friendlies, actor, enemies, initiative_list, enemies_spawned)


        # check for the flags & win/lose the battle
        if party_wiped:
            return battle_cleanup(friendlies, enemies_spawned, False)

        elif enemies_are_dead:
            return battle_cleanup(friendlies, enemies_spawned, True)



def pc_turn_handler(player_party, character, enemy: list[Entity], turn_order: list[Entity], is_bloodthirsty: bool = False):
    bloodthirsty = None
    turn_is_over = False

    while not turn_is_over:
        cmd = input("Command?\n").strip().lower()
        
        if cmd == "attack":
            # find the target of melee
            target = enemy[find_target(len(enemy))]
            # deal damage to it
            damage = damage_calc(character, target, False)
            input(f"You attack {target.Name} with your weapon, dealing {damage} damage!")
            target.HP -= damage
            if entity_is_dead(target):
                input(f"{target.Name} has fallen!")
                turn_order.remove(target)
                enemy.remove(target)
                bloodthirsty = character
            turn_is_over = True
        
        elif cmd == "ability":
            bloodthirsty = ability_handler(player_party, character, enemy, turn_order)
            turn_is_over = True
            
        elif cmd == "pass":
            if is_bloodthirsty:
                input(f"{character.Name} is enraged! They must attack!")
                turn_is_over = False
            else:
                input(f"{character.Name} waited to act!")
                turn_is_over = True
            
        else:
            input("Invalid command!")

    return bloodthirsty
    


def ability_handler(player_party, character, enemy: list[Entity], turn_order: list[Entity]):
    bloodthirsty = None
    # check if you have an ability
    if len(character.Abilities) >= 1:
        
        # print the abilities and let you choose one
        print("Your available abilities:", character.Abilities.keys())
        chosen_ability = input("Which ability do you choose?")
        use_ability = None
        while use_ability is None:
            try:
                use_ability = globals()[character.Abilities[chosen_ability]["callback"]]
            except KeyError:
                chosen_ability = input("That ability isn't in your learned abilities! Did you change your mind? Input 'back' to go back.")
                if chosen_ability.strip().lower() == "back":
                    pc_turn_handler(player_party, character, enemy, turn_order)
                    return None
                    break
                    
        # !!! CRITICAL REMINDER !!!
        # Since checking if anybody's died is too much work to put in here, YOU MUST DO IT IN THE ABILITY SCRIPT!!
        # Forgetting to check if anything's died when you deal damage that *COULD* be lethal is DUMB!!!
        # !!! CRITICAL REMINDER !!!
        bloodthirsty = use_ability(player_party, character, enemy, turn_order)
            
    # if you don't have an ability, don't let them do anything
    else:
        input("you don't have an ability dummy")
        pc_turn_handler(player_party, character, enemy, turn_order)
        return None
    if bloodthirsty == False:
        pc_turn_handler(player_party, character, enemy, turn_order)
        return None
    return bloodthirsty


###

def check_if_battle_won(friendlies, enemies):
    if len(friendlies) == 0:
        return False
    elif len(enemies) == 0:
        return True
    else:
        return None

def enemy_AI(character: list[Entity], enemy, turn_order):
    bloodthirsty = None
    # choose a random target (advanced targeting comes later)
    enemy_target = random.randrange(0, len(character))
    # check if its mind is higher than its strength and use the higher stat in the damage calc
    if enemy.get_strength() > enemy.get_mind():
        enemy_damage = damage_calc(enemy, character[enemy_target], False)
        input(f"The enemy attacks with their weapon and deals {enemy_damage} damage to {character[enemy_target].Name}!")
    else:
        enemy_damage = damage_calc(enemy, character[enemy_target], True)
        input(f"The enemy casts a spell and deals {enemy_damage} damage to {character[enemy_target].Name}!")
    # deal damage
    character[enemy_target].HP -= enemy_damage
    # make sure the character doesn't have negative health
    if character[enemy_target].HP < 0:
        character[enemy_target].HP = 0
    # let the player know what health they're at
    input(f"{character[enemy_target].Name} is at {character[enemy_target].HP}/{character[enemy_target].MaxHP} HP!")
    # check if the character died
    if character[enemy_target].HP <= 0:
        # kill them
        input(f"{character[enemy_target].Name} Has Fallen!")
        bloodthirsty = enemy
        turn_order.remove(character[enemy_target])
        character.remove(character[enemy_target])
    return bloodthirsty


def damage_calc(attacker, defender, magic: bool = False, crit_enabled: bool = True):
    if crit_enabled:
        critical = 2 if random.uniform(0, 1) >= 0.95 else 1
    else:
        critical = 1
    level_differential = 1 + (attacker.Level / 10) - (defender.Level / 10)

    if critical > 1:
        print("It's a critical hit!")

    if not magic:
        damage = ((attacker.get_strength() * level_differential) - ((defender.get_res() * 0.9) / level_differential)) * critical
        damage = int(damage * random.uniform(0.9, 1.1))
        if damage >= 0:
            return damage
        else:
            return 0

    elif magic:
        damage = (attacker.get_mind() * level_differential) - ((defender.get_res() * 0.7) / level_differential) * critical
        damage = int(damage * random.uniform(0.9, 1.1))
        if damage >= 0:
            return damage
        else:
            return 0
    else:
        print("You forgot to set magic, dumbass.")
        return 0

def entity_is_dead(entity):
    if entity.HP <= 0:
        entity.HP = 0
    if entity.HP == 0:
        return True
    else:
        return False
    

def battle_cleanup(friendlies, enemies, won_battle = True):
    os.system(CLEAR)
    if won_battle == True:
        print("B A T T L E  W O N !")
        if len(enemies) > 1:
            for actors in enemies:
                print(f"You defeated {actors.Name}!")
            input("")
        else:
            input(f"You defeated {enemies[0].Name}!")
        for pc in friendlies:
            pc.StatChanges["STR"] = 0
            pc.StatChanges["RES"] = 0
            pc.StatChanges["MND"] = 0
            pc.StatChanges["AGI"] = 0
    if won_battle == False:
        input("Khorynn's party wiped! You lose!")
        open_file("assets/sprites/peter_griffin_fortnite.jpeg")
    return won_battle



def skull_crusher(player_party, user, enemy, inititive_list):
    bloodthirsty = None
    if user.MP < 3:
        input(f"{user.Name} didn't have enough MP to use Skull Crusher!")
        return False
    target = enemy[find_target(len(enemy))]
    input(f"{user.Name} uses Skull Crusher!")
    user.MP -= 3
    input("They siphon 3 points of MP!")
    input(f"{user.Name} slams their weapon onto {target.Name}'s head with a horrifying CRACK!")
    damage = int(damage_calc(user, target, False))
    input(f"They deal {damage} damage!")
    target.HP -= damage
    if entity_is_dead(target):
        input(f"{target.Name} has fallen!")
        enemy.remove(target)
        inititive_list.remove(target)
        bloodthirsty = user
    else:
        input(f"{target.Name}'s resilience was lowered one stage!")
        target.change_stat("RES", -1)
    return bloodthirsty


def forfireball(player_party, user, enemy, inititive_list):
    if user.MP < 40:
        input(f"{user.Name} tried to use Fireball, but its immense mana cost proved too much for them!")
        return False
    else:
        defender = enemy[find_target(len(enemy))]
        user.MP -= 40
        input(f"{user.Name} casts Fireball!")
        defense_ignored = defender.get_res()
        defender.RES -= defense_ignored
        input("Even the most powerful defenses shatter when the shockwave hits it!")
        damage = damage_calc(user, defender, True) * 2
        defender.RES += defense_ignored
        input(f"{defender.Name} takes {damage} damage!")
        defender.HP -= damage
        if entity_is_dead(defender):
            input(f"{defender.Name} has fallen!")
            enemy.remove(defender)
            inititive_list.remove(defender)
            return user
        return None


def focus(player_party, user, enemy, turn_order):
    mind_multiple = (user.get_mind() * 0.05) + 1
    if mind_multiple > 5:
        mind_multiple = 5
    if user.MP < 5:
        input(f"{user.Name} tried to use Focus, but they didn't have enough MP!")
        return False
    else:
        user.MP -= 5
        input(f"{user.Name} used Focus!")
        input("They take a deep breath and center their thoughts...")
        input("They feel better already!")
        health_to_heal = int(user.MaxHP * 0.1 + (random.randrange(10, 15) * mind_multiple))
        if (health_to_heal + user.HP) > user.MaxHP:
            health_to_heal = user.MaxHP - user.HP
        input(f"{user.Name} heals {health_to_heal} HP!")
        user.HP += health_to_heal
        input("They gain a temporary boost to Mind!")
        user.change_stat("MND", 1)


def slap(player_party, user, enemy, turn_order):
    input(f"{user.Name} is panicking!")
    panic_thoughts = [
        f"{user.Name} thinks they left their refridgerator running!",
        f"{user.Name} suddenly forgets everything they were doing!",
        f"{user.Name} suddenly finds images of malformed monkeys very valuable!",
        f"{user.Name} realizes that their parents were right about their worthlessness!",
        f"{user.Name} remembers that one cringy thing they did when they were a kid!",
        f"{user.Name} shits the bed!"
    ]
    chosen_thought = random.choice(panic_thoughts)
    input(f"{chosen_thought}")
    input("They slap themselves to regain composure!")
    damage = damage_calc(user, user, False)
    input(f"They suffer {damage} damage!")
    user.HP -= damage
    if entity_is_dead(user):
        input(f"{user.Name} killed themself!")
        turn_order.remove(user)
        player_party.remove(user)
    else:
        input(f"{user.Name}'s mind settles!")
        user.change_stat("MND", 1)
    return None
    
def heal(player_party, user, enemy, turn_order):
    if user.MP < 6:
        input(f"{user.Name} didn't have enough MP to use Heal!")
        return False
    else:
        print("Party:")
        for pc in player_party:
            print(f"{pc.Name}")
        pc_to_heal = input("(INPUT PLAYER CHARACTER NAME) Which party member would you like to heal?")
        for character in player_party:
            if character.Name.lower() == pc_to_heal.lower().strip():
                pc_to_heal = character
                break
        input(f"{user.Name} focuses on calming things...")
        input("They siphon 6 MP!")
        input(f"{user.Name} casts Heal!")
        HP_to_heal = int(user.MaxHP * 0.2) + int(user.get_mind() * 1.5)
        HP_to_heal = pc_to_heal.MaxHP - pc_to_heal.HP if pc_to_heal.HP + HP_to_heal > pc_to_heal.MaxHP else HP_to_heal
        input(f"They heal {pc_to_heal.Name} for {HP_to_heal} HP!")
        pc_to_heal.HP += HP_to_heal
        return None

def resilience_prayer(player_party, user, enemy, turn_order):
    if user.MP < 20:
        input(f"{user.Name} didn't have enough MP to use Resilience Prayer!")
        return False
    else:
        input(f"{user.Name} kneels down and prays for everyone to be safe...")
        for pc in player_party:
            pc.change_stat("RES", 1)
        input("Everyone feels a little tougher! Party's resilience increases one stage!")
        return None

def king_slime(player_party, gel_king, enemies, initiative_list, enemies_spawned):
    bloodthirsty = None
    # Boss Behavior
    # At 20% HP intervals, have it spawn a servant
    # i.e. at 80% health, it spawns 1 slime, again at 60%
    # If it's below half health, it spawns 2 at a time instead
    # at 40% and 20%, it spawns 2 slimes each time
    # Otherwise just attacks normally
    #
    # Wanted to do this via callbacks/flag checking, but I don't know how to do that!
    # At this moment, I'm just going to use highly specific globals that won't be used anywhere else.
    # THIS SHOULD NOT BE THE MAIN SOLUTION! GLOBALS ARE CRINGE! CALLBACKS ARE BASED!
    global king_slime_spawn_phase_1_happened
    global king_slime_spawn_phase_2_happened
    global king_slime_spawn_phase_3_happened
    global king_slime_spawn_phase_4_happened

    if gel_king.HP < int(gel_king.MaxHP * 0.8):
        if king_slime_spawn_phase_1_happened == False:
            GelatinousServant = copy.deepcopy(entities["GelatinousServant"])
            input("The Gelatinous King's gel wobbles...\nA Gelatinous Servent erupts from the King and joins the fight!")
            enemies.append(GelatinousServant)
            initiative_list.append(GelatinousServant)
            enemies_spawned.append(GelatinousServant)
            king_slime_spawn_phase_1_happened = True
            
    if gel_king.HP < int(gel_king.MaxHP * 0.6):
        if king_slime_spawn_phase_2_happened == False:
            GelatinousServant = copy.deepcopy(entities["GelatinousServant"])
            input("The Gelatinous King ejects another Servant from its wounded flesh!")
            enemies.append(GelatinousServant)
            initiative_list.append(GelatinousServant)
            enemies_spawned.append(GelatinousServant)
            king_slime_spawn_phase_2_happened = True  
            
    if gel_king.HP < int(gel_king.MaxHP * 0.4):
        if king_slime_spawn_phase_3_happened == False:
            input("The Gelatinous King is falling apart! Two servants are ripped from the main body!")
            for _ in range(2):
                GelatinousServant = copy.deepcopy(entities["GelatinousServant"])                
                enemies.append(GelatinousServant)
                initiative_list.append(GelatinousServant)
                enemies_spawned.append(GelatinousServant)
            king_slime_spawn_phase_3_happened = True
                
    if gel_king.HP < int(gel_king.MaxHP * 0.2):
        if king_slime_spawn_phase_4_happened == False:
            input("The Gelatinous King is almost dead!\nThree Gelatinous Servants stream like a river from its flesh!")
            for _ in range(3):
                GelatinousServant = copy.deepcopy(entities["GelatinousServant"])
                enemies.append(GelatinousServant)
                initiative_list.append(GelatinousServant)
                enemies_spawned.append(GelatinousServant)   
            king_slime_spawn_phase_4_happened = True

    enemy_target = None
    for player_character in player_party:
        if damage_calc(gel_king, player_character, False, False) > player_character.HP:
            enemy_target = player_character
            break
    enemy_target = random.choice(player_party) if enemy_target == None else enemy_target
    enemy_damage = damage_calc(gel_king, enemy_target, False)
    input(f"The King slams down on {enemy_target.Name} with its ginormous body and deals {enemy_damage}!")
    enemy_target.HP -= enemy_damage
    # make sure the character doesn't have negative health
    if enemy_target.HP < 0:
        enemy_target.HP = 0
    # let the player know what health they're at
    input(f"{enemy_target.Name} is at {enemy_target.HP}/{enemy_target.MaxHP} HP!")
    # check if the character died
    if enemy_target.HP <= 0:
        input(f"{enemy_target.Name} Has Fallen!")
        bloodthirsty = gel_king
        initiative_list.remove(enemy_target)
        player_party.remove(enemy_target)
    return bloodthirsty    

def main():
    began = False
    run = 1
    
    while not began:
        began = title_screen()
    while began:

        
        if run == 1:
            os.system(CLEAR)
            input("Welcome to Project Recall!\nAt this moment, this game is mostly just a battle simulator.")
            input("You will be presented with mutliple encounters, getting new party members and levelling up between fights.")
            input("The party members you find are entirely randomized!\nMake sure to see what each class does in the tutorial if you haven't already.")
            input("Have fun! <3")
            os.system(CLEAR)
            
        elif run == 2:
            for _ in range(8):
                for guy in player_party:
                    level_up(guy, True)
            for guy in player_party:
                level_up(guy, True)
                
        elif run == 5:
            input("Congratulations! You beat the game!")
            input("That's all I have for now. Thanks for playing!")
            began = False
            break
            
        else:
            for _ in range(9):
                for guy in player_party:
                    level_up(guy, True)
            for guy in player_party:
                level_up(guy, False)
                
        present_player_party_members(find_party_level(player_party))
        if not initiate_battle(player_party, run):
            began = False
        if run <= 4:
            run += 1




while __name__ == "__main__":
    main()
