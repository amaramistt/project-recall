import os
import sys
import random
import entity as ENTY

CLEAR = 'cls' if os.name == 'nt' else 'clear'

class GameState(object):
    def __init__(self):
      self.reset()

    def reset(self):
        self.player_party = []
        self.enemy_party = []
        self.bagged_items = []
        self.passives = []
        self.money = 0
        self.floor = 0
        self.in_battle = False
        self.message_log = []
        self.debug_mode = False


GAME_STATE = GameState()

callback_triggers = {
    "callback_entity_is_hit": [], # KWARGS FORMAT: entity_hit, entity_attacker, damage_dealt
    
    "callback_pc_is_hit": [], # KWARGS FORMAT: entity_hit, entity_attacker, damage_dealt
    
    "callback_enemy_is_hit": [], # KWARGS FORMAT: entity_hit, entity_attacker, damage_dealt
    
    "callback_entity_is_dead": [], # KWARGS FORMAT: entity_dead, entity_attacker
    
    "callback_pc_is_dead": [], # KWARGS FORMAT: entity_dead, entity_attacker
    
    "callback_enemy_is_dead": [], # KWARGS FORMAT: entity_dead, entity_attaker
    
    "callback_entity_is_targeted": [], #KWARGS FORMAT: entity_targeted, entity_attacking, attacker_action
    
    "callback_pc_is_targeted": [], #KWARGS FORMAT: entity_targeted, entity_attacking, attacker_action
    
    "callback_enemy_is_targeted": [], #KWARGS FORMAT: entity_targeted, entity_attacking, attacker_action
    
    "callback_spell_is_casted": [], #KWARGS FORMAT: entity_casting, enitity_targeted, spell_casted
    
    "callback_stat_is_changed": [], #KWARGS FORMAT: entity_buffing_debuffing, stat_changed, change_stages
    
    "callback_bloodthirsty_triggered": [], #KWARGS FORMAT: entity_bloodthirsty

    "callback_turn_phase_1": [], #KWARGS FORMAT: 

    "callback_turn_phase_2": [], #KWARGS FORMAT: 

    "callback_turn_phase_3": [], #KWARGS FORMAT: 
    
    "callback_item_pickup": [], #KWARGS FORMAT: entity_picking_up, item_picking_up
}

def get_callback_triggers_map():
    return callback_triggers
    
def add_callback(trigger, callback):
    # Takes a given "stringified" callback and adds it to the value of a given trigger in callback_triggers
    # To add a callback that should happen every time some*thing* dies:
    # add_callback("callback_entity_is_dead", "something_died")
    if trigger == "" or callback == "":
        return
    callback_triggers[trigger].append(callback)

def remove_callback(trigger, callback):
    if trigger == "" or callback == "":
        return
    callback_triggers[trigger].remove(callback)

def run_callbacks(trigger, **kwargs):
    # Takes a given trigger and excecutes all of the callbacks in the trigger's value in callback_triggers
    # kwargs are callback-dependent; each one has a different format that gives things that they might need
    # check the callback_triggers dict for the format
    for callback in callback_triggers[trigger]:
        run_callback = globals()[callback]
        run_callback(**kwargs)

def print_tutorial():
    print("Basic Combat Tutorial")
    print_with_conf("In this tutorial, you will learn the basics of combat.", True)
    os.system(CLEAR)
    print("STATISTICS")
    print_with_conf("Your characters' statistics are the backbone of combat. There are several stats that directly affect the effectiveness of your units.", True)
    print_with_conf("HP or Health Points: How much damage one can take before dying.", True)
    print_with_conf("MP or Magic Points: Spells and Abilities use MP to activate.", True)
    print_with_conf("STR or Strength: How effective one is at attacking directly with a weapon.", True)
    print_with_conf("RES or Resilience: How effective one is at taking hits.", True)
    print_with_conf("MND or Mind: How effective one is at using magic and resisting urges.", True)
    print_with_conf("AGI or Agility: How fast one is.", True)
    os.system(CLEAR)
    print("JOBS")
    print_with_conf("Jobs affect a character's stats and learnable abilities.", True)
    print_with_conf("There will be more jobs with more in-depth mechanics later, but these are the jobs available to you currently.", True)
    print_with_conf("Warrior: Big, strong, tanky unit that takes hits and deals damage. However, they're a little slow, both literally and figuratively.", True)
    print_with_conf("Mage: Absolute powerhouses that die if you look at them too hard. Abuse their powerful magic and keep them safe!", True)
    print_with_conf("Just A Guy: I don't know how they got here, they are literally just normal humans. Extremely weak.", True)
    print_with_conf("Thief: Generalists with exceptional speed. Gets things done and gets things done before anyone else.", True)
    print_with_conf("Monk: Fast, decently bulky physical fighters that don't need weapons to kill. Say your prayers.", True)
    print_with_conf("Priest: Squishy backliners that support their allies with healing and buffs. Keep them safe and they'll return the favor!", True)
    os.system(CLEAR)
    print("COMMANDS")
    print_with_conf("When it is a player characters' turn in battle, you will be asked to print_with_conf a command.", True)
    print_with_conf("A list of available commands will follow.", True)
    print_with_conf("Attack: Initiate a basic attack on a selected enemy.", True)
    print_with_conf("Ability: Initiates the process of using abilities. Most of them use MP!", True)
    print_with_conf("Pass: Passes your turn. Your character will not act that turn.", True)
    print_with_conf("Item: Shows the inventory of your character and allows for the use of active items!", True)
    os.system(CLEAR)
    print("BLOODTHIRSTINESS")
    print_with_conf("Whenever a character kills an opposing character, they immediately take another turn.", True)
    print_with_conf("Both enemies and player characters are affected by bloodthirstiness.", True)
    print_with_conf("In the extra turn, you may *only* attack, with either a basic attack or with a spell.", True)
    print_with_conf("Nobody may take two bloodthirsty turns in a row.", True)
    os.system(CLEAR)
    print_with_conf("More to come in the future! Good luck!", True)
    os.system(CLEAR)

def begin_run_handler():
    os.system(CLEAR)
    if not GAME_STATE.debug_mode:
        # start with a selected job
        print(f"Jobs available for selection: ", end="")
        for job in ENTY.get_jobs_map().keys():
            print(f"{job}, ", end = "")
            #HOW DO I MAKE THIS GRAMMATICALLY CORRECT :((((((
        while True:
            char_job = input("\nWhat job should Khorynn start with? ").strip().lower()
            if char_job in ENTY.get_jobs_map().keys():
                Khorynn = ENTY.generate_khorynn(char_job)
                GAME_STATE.player_party.append(Khorynn)
                print_with_conf(f"Character sheet\n{GAME_STATE.player_party[0]}")
                return True
            else:
                print_with_conf("That is not an available job!")
    else:
        # UNLEASH THE WRATH OF ULTRA MEGA DEBUG KHORYNN
        print(GAME_STATE.debug_mode)
        print_with_conf("Through the power of debugging, you are blessed with Ultra Mega Debug Khorynn!!!!", True)
        Khorynn = ENTY.generate_khorynn("balls")
        GAME_STATE.player_party.append(Khorynn)
        print_with_conf(f"Character sheet\n{GAME_STATE.player_party[0]}", True)
        return True

def title_screen():
    GAME_STATE.reset()
    os.system(CLEAR)
    print("                P R O J E C T    R E C A L L")
    print_with_conf("                    Press Enter To Start    ", True)
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
        print_with_conf("DEBUG  MODE  ENABLED!!!!!!!!", True)
        GAME_STATE.debug_mode = True
        return begin_run_handler()
    else:
        print_with_conf("Invalid print_with_conf.", True)
        return None


###


def load_cutscene(cutscene_ID):
    # IN CONSTRUCTION 
    # finds the cutscene ID from a large database of cutscenes
    # has some system in which this function could interpret some text as instructions
    # i.e. if i call load_cutscene(5) it would load cutscene 5 and make sure that each character moves and speaks the correct way
    # i.e. if cutscene ID 5 was one line saying "(Khorynn)(FACE_LEFT)'Are you serious?'", Khorynn would face left and say 'Are you serious?'
    # gonna have to get real used to using for x in y :3
    pass

def menu():
    os.system(CLEAR)
    print("PARTY\n")
    for pc in GAME_STATE.player_party:
        print(pc.Name)
    print("\n")
    print(f"Gold: {GAME_STATE.money}")
    print(f"Items in the Stash: {GAME_STATE.bagged_items}")
    print(f"Floor: {GAME_STATE.floor}")
    print("\n")

    chosen_pc = None
    cmd = input("(INPUT) Input a party member's name to see details about them. Input anything else to go back.").strip().lower()
    for pc in GAME_STATE.player_party:
        if cmd == pc.Name.lower():
            chosen_pc = pc
    if chosen_pc is None:
        os.system(CLEAR)
        return
    else:
        pc_management_menu(chosen_pc)

def print_with_conf(message, from_menu: bool = False):
    # Should replace every instance of print_with_conf() used to control the pace of the game
    # Allows access to the menu at any time, which means you can KNOW YOUR STATS!
    confirmed = False
    while not confirmed:
        confirm = input(message).lower().strip()
        if confirm == "menu":
            menu()
        elif confirm == "log":
            os.system(CLEAR)
            for each_message in GAME_STATE.message_log:
                print(each_message)
            input()
            os.system(CLEAR)
        else:
            confirmed = True

    if not from_menu:
        GAME_STATE.message_log.insert(0, message)
        if len(GAME_STATE.message_log) > 20:
            GAME_STATE.message_log.remove(20)
    
        
def pc_management_menu(chosen_pc):
    os.system(CLEAR)
    print(chosen_pc)
    print(f"Weapon: {chosen_pc.EquippedWeapon}")
    print(f"Armor: {chosen_pc.EquippedArmor}")
    print(f"Accessory 1: {chosen_pc.EquippedAccessories[0]}")
    print(f"Accessory 2: {chosen_pc.EquippedAccessories[1]}\n")
    print("Items in their Inventory:")
    for _ in range(len(chosen_pc.Items)):
        print(f"{_ + 1}: {chosen_pc.Items[_]}")
    print("\n\n")    
    chosen_item = None
    cmd = input("(INPUT) Input an item number to see details about it and do some operations on it. Input anything else to go back.")
    try:
        cmd = int(cmd)
    except ValueError:
        menu()
        return

    cmd = 1 if cmd <= 0 else cmd
    cmd = len(chosen_pc.Items) if cmd > len(chosen_pc.Items) else cmd
    chosen_item = chosen_pc.Items[cmd - 1]
    
    os.system(CLEAR)
    print(chosen_item.ItemName)
    print(f"Item Type: {chosen_item.ItemType}")
    if chosen_item.ItemType == "equip":
        print(f"Equipment Type: {chosen_item.ItemSubtype}")
    print(chosen_item.ItemDesc)
    if chosen_item.ItemType == "equip":
        if chosen_item.ItemSubtype == "weapon":
            if chosen_item.ItemName == chosen_pc.EquippedWeapon.ItemName:
                input(f"This is {chosen_pc.Name}'s equipped weapon.")
        if chosen_item.ItemSubtype == "armor":
            if chosen_item.ItemName == chosen_pc.EquippedArmor.ItemName:
                input(f"This is {chosen_pc.Name}'s equipped armor.") 
        if chosen_item.ItemSubtype == "accessory":
            if chosen_item.ItemName == chosen_pc.EquippedAccessories[0].ItemName:
                input(f"This is {chosen_pc.Name}'s equipped weapon.")
        cmd = input("\n(INPUT Y/N) Would you like to equip this item?").lower().strip()
        if cmd == "y":
            chosen_item.equip(chosen_pc)
        pc_management_menu(chosen_pc)
        return
