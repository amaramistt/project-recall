import os
import sys
import random
import entity as ENTY
import item as ITM
import json

CLEAR = 'cls' if os.name == 'nt' else 'clear'

class GameState(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.player_party = []
        self.enemy_party = []
        self.bagged_items = []
        self.passives = []
        self.khorynn = None
        self.floor = 0
        self.money = 0
        self.xp_count = 0
        self.in_battle = False
        self.turn_order = []
        self.battle_entity_targeted = None
        self.battle_entity_attacking = None
        self.battle_bloodthirsty_triggered = False
        self.message_log = []
        self.debug_mode = False
        self.player_changed_jobs = False
        self.player_got_new_party_member = False
        self.player_bought_something = False
        self.shop_stock = []


GAME_STATE = GameState()

callback_trigger_args = {
    "callback_entity_is_hit": ["entity_hit", "entity_attacker", "damage_dealt"],
    "callback_pc_is_hit": ["entity_hit", "entity_attacker", "damage_dealt"],
    "callback_enemy_is_hit": ["entity_hit", "entity_attacker", "damage_dealt"],
    "callback_entity_is_dead": ["entity_dead", "entity_attacker"],
    "callback_pc_is_dead": ["entity_dead", "entity_attacker"],
    "callback_enemy_is_dead": ["entity_dead", "entity_attacker"],
    "callback_entity_is_targeted": ["attacker_action"],
    "callback_pc_is_targeted": ["attacker_action"],
    "callback_enemy_is_targeted": ["attacker_action"],
    "callback_spell_is_casted": ["entity_casting", "entity_targeted", "spell_casted"],
    "callback_stat_is_changed": ["entity_buffing_debuffing", "stat_changed", "change_stages"],
    "callback_bloodthirsty_triggered": ["entity_bloodthirsty"],
    "callback_turn_phase_1": [],
    "callback_turn_phase_2": [],
    "callback_turn_phase_3": [],
    "callback_item_pickup": ["entity_picking_up", "item_picking_up"],
    "callback_item_being_used": ["item_being_used", "entity_using_item"],
    "callback_shop_items_generated": [],
    "callback_battle_is_finished": [],
}

callback_triggers = {
    "callback_entity_is_hit": [],
    "callback_pc_is_hit": [],
    "callback_enemy_is_hit": [],
    "callback_entity_is_dead": [],
    "callback_pc_is_dead": [],
    "callback_enemy_is_dead": [],
    "callback_entity_is_targeted": [],
    "callback_pc_is_targeted": [],
    "callback_enemy_is_targeted": [],
    "callback_spell_is_casted": [],
    "callback_stat_is_changed": [],
    "callback_bloodthirsty_triggered": [],
    "callback_turn_phase_post_normal_turn": [],
    "callback_turn_phase_post_bloodthirsty": [],
    "callback_item_pickup": [],
    "callback_item_being_used": [],
    "callback_turn_timer": [],
    "callback_shop_items_generated": [],
    "callback_battle_is_finished": [],
}

def get_callback_triggers_map():
    return callback_triggers

def move_to_line(x = 0, y = 0):
    print("\033[%d;%dH" % (y, x))

def clear_terminal():
    os.system(CLEAR)
    print()

def add_callback(trigger, callback):
    if callback is None:
        return
    if trigger not in callback_triggers:
        raise ValueError(f"{trigger} is FAKE!!! not a real callback")
    callback_triggers[trigger].append(callback)

def remove_callback(trigger, callback):
    if trigger is None:
        return
    if trigger not in callback_triggers:
        raise ValueError(f"{trigger} is FAKE!!! not a real callback")
    if callback not in callback_triggers[trigger]:
        return
    callback_triggers[trigger].remove(callback)

def run_callbacks(trigger, **kwargs):
    # Takes a given trigger and excecutes all of the callbacks in the trigger's value in callback_triggers
    # kwargs are callback-dependent; each one has a different format that gives things that they might need
    # check the callback_triggers dict for the format
    for callback in callback_triggers[trigger]:
        callback_args = {k: kwargs[k] for k in callback_trigger_args[trigger]}
        callback(**callback_args)


def print_tutorial():
    print("Basic Combat Tutorial")
    print_with_conf("In this tutorial, you will learn the basics of combat.", True)
    clear_terminal()
    print("STATISTICS")
    print_with_conf("Your characters' statistics are the backbone of combat. There are several stats that directly affect the effectiveness of your units.", True)
    print_with_conf("HP or Health Points: How much damage one can take before dying.", True)
    print_with_conf("MP or Magic Points: Spells and Abilities use MP to activate.", True)
    print_with_conf("STR or Strength: How effective one is at attacking directly with a weapon.", True)
    print_with_conf("RES or Resilience: How effective one is at taking hits.", True)
    print_with_conf("MND or Mind: How effective one is at using magic and resisting urges.", True)
    print_with_conf("AGI or Agility: How fast one is.", True)
    clear_terminal()
    print("JOBS")
    print_with_conf("Jobs affect a character's stats and learnable abilities.", True)
    print_with_conf("There will be more jobs with more in-depth mechanics later, but these are the jobs available to you currently.", True)
    print_with_conf("Warrior: Big, strong, tanky unit that takes hits and deals damage. However, they're a little slow, both literally and figuratively.", True)
    print_with_conf("Mage: Absolute powerhouses that die if you look at them too hard. Abuse their powerful magic and keep them safe!", True)
    print_with_conf("Just A Guy: I don't know how they got here, they are literally just normal humans. Extremely weak.", True)
    print_with_conf("Thief: Generalists with exceptional speed. Gets things done and gets things done before anyone else.", True)
    print_with_conf("Monk: Fast, decently bulky physical fighters that don't need weapons to kill. Say your prayers.", True)
    print_with_conf("Priest: Squishy backliners that support their allies with healing and buffs. Keep them safe and they'll return the favor!", True)
    clear_terminal()
    print("COMMANDS")
    print_with_conf("When it is a player characters' turn in battle, you will be asked to input a command.", True)
    print_with_conf("A list of available commands will follow.", True)
    print_with_conf("Attack: Initiate a basic attack on a selected enemy.", True)
    print_with_conf("Ability: Initiates the process of using abilities. Most of them use MP!", True)
    print_with_conf("Pass: Passes your turn. Your character will not act that turn.", True)
    print_with_conf("Item: Shows the inventory of your character and allows for the use of active items!", True)
    clear_terminal()
    print("BLOODTHIRSTINESS")
    print_with_conf("Whenever a character kills an opposing character, they immediately take another turn.", True)
    print_with_conf("In the extra turn, you may *only* attack, with either a basic attack or with a spell.", True)
    print_with_conf("Nobody may take two bloodthirsty turns in a row.", True)
    clear_terminal()
    print_with_conf("More to come in the future! Good luck!", True)
    clear_terminal()

def begin_run_handler():
    clear_terminal()
    if not GAME_STATE.debug_mode:
        # start with a selected job
        print(f"Jobs available for selection:")
        for job in ENTY.find_available_jobs():
            print(f"{ENTY.get_jobs_map()[job]['name']}")
        while True:
            char_job = input("\n\nWhat job should Khorynn start with? ").strip().lower()
            if char_job in ENTY.get_jobs_map().keys():
                Khorynn = ENTY.generate_khorynn(char_job)
                GAME_STATE.player_party.append(Khorynn)
                GAME_STATE.khorynn = Khorynn
                print_with_conf(f"Character sheet\n{GAME_STATE.khorynn}")
                return True
            else:
                print_with_conf("That is not an available job!")
    else:
        # UNLEASH THE WRATH OF ULTRA MEGA DEBUG KHORYNN
        print(GAME_STATE.debug_mode)
        print_with_conf("Through the power of debugging, you are blessed with Ultra Mega Debug Khorynn!!!!", True)
        Khorynn = ENTY.generate_khorynn("balls")
        GAME_STATE.player_party.append(Khorynn)
        GAME_STATE.khorynn = Khorynn
        print_with_conf(f"Character sheet\n{GAME_STATE.khorynn}", True)
        return True

def title_screen():
    GAME_STATE.reset()
    clear_terminal()
    print("                P R O J E C T    R E C A L L")
    print_with_conf("                    Press Enter To Start    ", True)
    clear_terminal()
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

def rest_time():
    GAME_STATE.player_changed_jobs = False
    GAME_STATE.player_got_new_party_member = False
    GAME_STATE.player_bought_something = False
    clear_terminal()
    player_has_party = True
    if len(GAME_STATE.player_party) > 1:
        player_has_party = True
    # establish safe zone and max out party HP and MP
    print_with_conf("After finishing the battle, you feel exhausted and seek shelter.")
    print_with_conf("As soon as you find a suitable area to rest, you start a campfire and sit down once your work is done.")
    if player_has_party:
        print_with_conf("Your party quickly follow your lead.")
    print_with_conf("Rejuvenated by the comforting warmth, your health and mental capacity are restored.")
    for pc in GAME_STATE.player_party:
        pc.HP = pc.get_max_hp()
        pc.MP = pc.get_max_mp()
    print_with_conf("Party's HP and MP maxed out!")
    
    while True:
        clear_terminal()
        
        print("The dying fire inspires thought... There are many things you could do to prepare for the dangers ahead.")
        cmd = input("Will you visit Olivia's 'party' planning service?\nWould you rather take a look at your stats and manage your items in the 'menu'?\nDo you want to check out what Ornaldo has in his 'shop'?\n(INPUT) Or, are you 'done' resting up?    ").lower().strip()
        
        if cmd == "party":
            ENTY.party_place_handler()

        if cmd == "shop":
            ITM.shop()

        if cmd == "menu":
            menu()
            
        if cmd == "done":
            if player_has_party:
                print_with_conf("You stand up, and your party follows your lead. Putting out the flame, you venture forth.")
                return
                
            else:
                print_with_conf("You stand up, putting out the flame. You begin to venture forth on your own.")
                return

def load_cutscene(cutscene_ID):
    clear_terminal()
    with open(f"data/scenes/{cutscene_ID}.sdt") as file:
        for line in file:
            if "CMD_CLEAR" in line:
                input(f"'CMD_CLEAR' found in line: {line}")
                clear_terminal()
            else:
                input("not clearing")
                print_with_conf(f"{line}\033[A")

def menu():
    clear_terminal()
    print("PARTY\n")
    for _ in range(len(GAME_STATE.player_party)):
        print(f"Party member {_ + 1}: {GAME_STATE.player_party[_].Name}")
    print("\n")
    print(f"Gold: {GAME_STATE.money}")
    print(f"Items in the Stash: {GAME_STATE.bagged_items}")
    print(f"Floor: {GAME_STATE.floor}")
    print("\n")

    chosen_pc = None
    
    cmd = input("(INPUT) Input a party member's number to see details about them.\nInput 'Stash' to operate on items in the Stash.\nInput anything else to go back.  ").strip().lower()
    

    if cmd == "stash":
        stash_management_menu()

    elif cmd == "debug":
        if GAME_STATE.debug_mode:
            debug_menu()
    
    try:
        cmd = int(cmd) - 1 if int(cmd) - 1 > -1 else 0
        cmd = len(GAME_STATE.player_party) - 1 if cmd >= len(GAME_STATE.player_party) else cmd
        selected_pc = GAME_STATE.player_party[cmd]
    except ValueError:
        clear_terminal()
        return
    
    pc_management_menu(selected_pc)


def stash_management_menu():
    if len(GAME_STATE.bagged_items) != 0:
        for item_number in range(len(GAME_STATE.bagged_items)):
            print(f"{item_number + 1}: {GAME_STATE.bagged_items[item_number]}")
    else:
        input("There are no items in the Stash.")
        menu()
        return
    cmd = input(f"(INPUT) Which number item would you like to work with? For example, '1' is your {GAME_STATE.bagged_items[0]}. Input anything else to go back.  ").strip()
    try:
        cmd = int(cmd)
    except ValueError:
        menu()
        return

    cmd = 1 if cmd <= 0 else cmd
    cmd = len(GAME_STATE.bagged_items) if cmd > len(GAME_STATE.bagged_items) else cmd
    chosen_item = GAME_STATE.bagged_items[cmd - 1]

    clear_terminal()
    print(f"Item Name: {chosen_item.ItemName}")
    print(f"Item Description: {chosen_item.ItemDesc}")
    print(f"Item Type: {chosen_item.ItemType}")
    if chosen_item.ItemType == "equip":
        print(f"Equipment Type: {chosen_item.ItemSubtype}")
    print("\n\n")
    
    if not GAME_STATE.in_battle:
        print("Would you like to 'use' this item?")
        cmd = input("Would you like to 'move' this item to a character's inventory?\nWould you like to 'discard' this item?\n(INPUT)   ").lower().strip()
        
        if cmd == "use":
            chosen_item.use()
            menu()
            return
                
        if cmd == "move":
            if chosen_item in GAME_STATE.bagged_items:
                input('ok so its in the stash')
            move_item_menu(chosen_item)
            menu()
        elif cmd == "discard":
            cmd2 = input(f"(INPUT Y/N) Are you SURE you want to discard the {chosen_item.ItemName}?   ").strip().lower()
            if cmd2 == "y":
                input(f"You threw the {chosen_item.ItemName} away. It shatters instantly.")
                GAME_STATE.bagged_items.remove(chosen_item)
                menu()
                return
            else:
                stash_management_menu()
                return
    else:
        input("You're in a battle! You can't manage your items right now!")
        menu()
        return

def move_item_menu(chosen_item, inventory = "bag"):
    if GAME_STATE.inbattle:
        input("You're in a battle! You can't manage your items right now!")
        return
    if inventory == "bag":
        inventory = GAME_STATE.bagged_items
    if chosen_item.ItemType == "equip":
        if chosen_item.Equipped:
            input("That item is currently equipped by someone! Unequip it first!")
            return
    
    chars_to_print = []
    for pc in GAME_STATE.player_party:
        if len(pc.Items) < 8:
            chars_to_print.append(pc)

    print(f"Party members with inventory space")
    for pc in chars_to_print:
        print(pc.Name)
    print("\n\n")
    
    cmd2 = input(f"(INPUT) Input the name of the character you would like to hold the {chosen_item.ItemName}. Input anything else to go back.   ").strip().lower()
    
    selected_pc = None
    for pc in chars_to_print:
        if cmd2 == pc.Name.lower():
            selected_pc = pc
            break 
            
    if selected_pc is not None:
        input(f"{selected_pc.Name} takes the {chosen_item.ItemName} and puts it in their inventory!")
        inventory.remove(chosen_item)
        selected_pc.Items.append(chosen_item)
        return
        
    else:
        return    

def print_with_conf(message, from_menu: bool = False):
    # Should replace every instance of print_with_conf() used to control the pace of the game
    # Allows access to the menu at any time, which means you can KNOW YOUR STATS!
    confirmed = False
    while not confirmed:
        confirm = input(message).lower().strip()
        if confirm == "menu":
            menu()
        elif confirm == "log":
            clear_terminal()
            for each_message in reversed(GAME_STATE.message_log):
                print(each_message)
            input()
            clear_terminal()
        else:
            confirmed = True

    if not from_menu:
        GAME_STATE.message_log.insert(0, message)
        if len(GAME_STATE.message_log) > 20:
            GAME_STATE.message_log.remove(GAME_STATE.message_log[20])
    
        
def pc_management_menu(chosen_pc):
    clear_terminal()
    print(chosen_pc)
    print(f"Job: {chosen_pc.Job}")
    print(f"Job Experience: {chosen_pc.JEXP}")
    print(f"Mastery Level: {chosen_pc.MasteryLevel}", end=" ")
    if chosen_pc.MasteryLevel == 3:
        print("<-- !! MASTERED !!")
    else:
        print()
    print("\n")
    print(f"Weapon: {chosen_pc.EquippedWeapon}")
    print(f"Armor: {chosen_pc.EquippedArmor}")
    print(f"Accessory 1: {chosen_pc.EquippedAccessories[0]}")
    print(f"Accessory 2: {chosen_pc.EquippedAccessories[1]}\n\n")
    print("Items in their Inventory:")
    for _ in range(len(chosen_pc.Items)):
        print(f"{_ + 1}: {chosen_pc.Items[_]}")
    print("\n\n\n")    

    if GAME_STATE.in_battle:
        input("You're in a battle! you can't manage your items right now!")
        menu()
        return
    
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
    
    clear_terminal()
    print(chosen_item.ItemName)
    print(f"Item Type: {chosen_item.ItemType}")
    if chosen_item.ItemType == "equip":
        print(f"Equipment Type: {chosen_item.ItemSubtype}")
    print(chosen_item.ItemDesc)
    if chosen_item.ItemType == "equip":
        if chosen_item.ItemSubtype == "weapon":
            if chosen_item.id == chosen_pc.EquippedWeapon.id:
                print(f"This is {chosen_pc.Name}'s equipped weapon.")
        if chosen_item.ItemSubtype == "armor":
            if chosen_item.id == chosen_pc.EquippedArmor.id:
                print(f"This is {chosen_pc.Name}'s equipped armor.") 
        if chosen_item.ItemSubtype == "accessory":
            if chosen_item.id in [x.id for x in chosen_pc.EquippedAccessories]:
                print(f"This is one of {chosen_pc.Name}'s equipped accessories.")
    print("\n\n")
    print("Would you like to 'use' this item?")
    if chosen_item.ItemType == "equip" and chosen_pc.Job != "monk":
        print("Would you like to 'equip' this item?")
        
    cmd = input("Would you like to 'move' this item to a character's inventory?\nWould you like to 'discard' this item?\n(INPUT)   ").lower().strip()
    
    if chosen_item.ItemType == "equip":
        if cmd == "equip":
            if chosen_pc.Job != "monk":
                chosen_item.equip(chosen_pc)
                pc_management_menu(chosen_pc)
                return
            else:
                if chosen_item.ItemSubtype == "weapon":
                    input(f"{chosen_pc.Name} is a Monk! They can't equip weapons!")
                    pc_management_menu(chosen_pc)
                else:
                    chosen_item.equip(chosen_pc)
                    pc_management_menu(chosen_pc)
            
    if cmd == "use":
        chosen_item.use()
        pc_management_menu(chosen_pc)
        return
        
    if cmd == "move":
        move_item_menu(chosen_item, chosen_pc.Items)
        pc_management_menu(chosen_pc)
        return
    if cmd == "discard":
        if chosen_item.Equipped:
            input("This item is equipped! If you want to discard it, unequip it first.")
            pc_management_menu(chosen_pc)
            return
        cmd2 = input(f"(INPUT Y/N) Are you SURE you want to discard the {chosen_item.ItemName}?   ").strip().lower()
        if cmd2 == "y":
            input(f"You threw the {chosen_item.ItemName} away. It shatters instantly.")
            chosen_pc.Items.remove(chosen_item)
            menu()
            return
    else:
        pc_management_menu(chosen_pc)
        return

def debug_menu():
    if not GAME_STATE.debug_mode:
        return

    cmd = input("do you want to give 'money' or 'jexp'?").strip().lower()
    if cmd == "money":
        cmd = int(input("input how much money you want to give"))
        GAME_STATE.money += cmd
        return
    if cmd == "jexp":
        for pc in GAME_STATE.player_party:
            print(f"{pc.Name}: ML{pc.MasteryLevel}")
        print("\n")
        cmd = int(input("input how much JEXP you want to give the first party member"))
        GAME_STATE.player_party[0].JEXP += cmd
        ENTY.check_for_mastery_level_up(GAME_STATE.player_party[0])
        return
    

def deal_damage_to_target(attacker, target, damage):
    bloodthirsty = None
    target.HP -= damage
    if target.HP < 0:
        target.HP = 0

    run_callbacks("callback_entity_is_hit", entity_hit=target, entity_attacker=attacker, damage_dealt=damage)
    if target.EntityType == "Khorynn" or target.EntityType == "PlayerCharacter":
        run_callbacks("callback_pc_is_hit", entity_hit=target, entity_attacker=attacker, damage_dealt=damage)
    else:
        run_callbacks("callback_enemy_is_hit", entity_hit=target, entity_attacker=attacker, damage_dealt=damage)
    
    if target.EntityType == "PlayerCharacter":
        print_with_conf(f"{target.Name} is at {target.HP}/{target.get_max_hp()} HP!")
    
    if target.HP <= 0:
        print_with_conf(f"{target.Name} Has Fallen!")
        bloodthirsty = attacker
        if target.EntityType == "PlayerCharacter" or target.EntityType == "Khorynn":
            GAME_STATE.player_party.remove(target)
        else:
            GAME_STATE.enemy_party.remove(target)
        run_callbacks("callback_entity_is_dead", entity_dead=target, entity_attacker=attacker)
        run_callbacks("callback_pc_is_dead", entity_dead=target, entity_attacker=attacker)
    return bloodthirsty