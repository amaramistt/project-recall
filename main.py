# To-Do List
#
#    \/ THINGS TO ACTUALLY WORK ON RIGHT NOW \/
# 1) Create a system in which enemies can be spawned from a pool of encounters only available at certain points of the game
#    ^^^^^^^^^   IN DEVELOPMENT   ^^^^^^^^^
# 2) Create a system in which passive, consumable, and non-consumable items can be seamlessly acquired and used,
#    preferably complete with item pools and broken synergies
# 3) Create a callback system in which functions may be excecuted every time something happens
# 4) 
#
#    \/ DO AT SOME POINT LATER \/
#    Create a system in which the player may exist outside of battle, so that items/equipment/accessories/menuing
#    may be implemented and debugged
#    Create a system where I can create spell functions (a la SkullCracker()) in a different file and import
#    them for use without too much rewriting of code


import os
import sys
import subprocess
import random
import copy
from entity import Entity
import entity
import battle

CLEAR = 'cls' if os.name == 'nt' else 'clear'
player_party = []

callback_triggers = {
    "callback_entity_is_hit": [], # KWARGS FORMAT: entity_hit, entity_attacker, player_party, enemy_party
    "callback_pc_is_hit": [], # KWARGS FORMAT: entity_hit, entity_attacker, player_party, enemy_party
    "callback_enemy_is_hit": [], # KWARGS FORMAT: entity_hit, entity_attacker, player_party, enemy_party
    "callback_entity_is_dead": [], # KWARGS FORMAT: entity_dead, entity_attacker
    "callback_pc_is_dead": [], # KWARGS FORMAT: entity_dead, entity_attacker
    "callback_enemy_is_dead": [], # KWARGS FORMAT: entity_dead, entity_attaker
    "callback_entity_is_targeted": [], #KWARGS FORMAT: entity_targeted, entity_attacking, attacker_action
    "callback_pc_is_targeted": [], #KWARGS FORMAT: entity_targeted, entity_attacking, attacker_action
    "callback_enemy_is_targeted": [], #KWARGS FORMAT: entity_targeted, entity_attacking, attacker_action
    "callback_spell_is_casted": [], #KWARGS FORMAT: entity_casting, enitity_targeted, spell_casted
    "callback_stat_is_changed": [], #KWARGS FORMAT: entity_buffing_debuffing, stat_changed, change_stages
    "callback_bloodthirsty_triggered": [], #KWARGS FORMAT: entity_bloodthirsty
}

def get_callback_triggers_map():
    return callback_triggers
def add_callback(trigger, callback):
    # Takes a given "stringified" callback and adds it to the value of a given trigger in callback_triggers
    # To add a callback that should happen every time some*thing* dies:
    # add_callback("callback_entity_is_dead", "something_died")
    callback_triggers[trigger].append(callback)

def remove_callback(trigger, callback):
    callback_triggers[trigger].remove(callback)

def run_callbacks(trigger, **kwargs):
    # Takes a given trigger and excecutes all of the callbacks in the trigger's value in callback_triggers
    # kwargs are callback-dependent; each one has a different format that gives things that they might need
    # check the callback_triggers dict for the format
    for callback in callback_triggers[trigger]:
        run_callback = globals()[callback]
        run_callback(**kwargs)

def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])
        


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
        entity.debug_starting_stats()
        return None
    else:
        input("Invalid input.")
        return None


###


def begin_run_handler():
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
    for job in entity.get_jobs_map().keys():
        print(f"{job}, ", end = "")
        #HOW DO I MAKE THIS GRAMMATICALLY CORRECT :((((((
    while True:
        char_job = input("\nWhat job should Khorynn start with? ").strip().lower()
        if char_job in entity.get_jobs_map().keys():
            Khorynn = entity.generate_khorynn(char_job)
            player_party.append(Khorynn)
            input(f"Character sheet\n{player_party[0]}")
            return True
        else:
            input("That is not an available job!")


def load_cutscene(cutscene_ID):
    # IN CONSTRUCTION 
    # finds the cutscene ID from a large database of cutscenes
    # has some system in which this function could interpret some text as instructions
    # i.e. if i call load_cutscene(5) it would load cutscene 5 and make sure that each character moves and speaks the correct way
    # i.e. if cutscene ID 5 was one line saying "(Khorynn)(FACE_LEFT)'Are you serious?'", Khorynn would face left and say 'Are you serious?'
    # gonna have to get real used to using for x in y :3
    pass


###

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
                    entity.level_up(guy, True)
            for guy in player_party:
                entity.level_up(guy)
                
        elif run == 5:
            input("Congratulations! You beat the game!")
            input("That's all I have for now. Thanks for playing!")
            began = False
            break
            
        else:
            for _ in range(9):
                for guy in player_party:
                    entity.level_up(guy, True)
            for guy in player_party:
                entity.level_up(guy)
                
        entity.present_player_party_members(player_party)
        if not battle.initiate_battle(player_party, run):
            began = False
        if run <= 4:
            run += 1




while __name__ == "__main__":
    main()
