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
king_slime_spawn_phase_1_happened = False
king_slime_spawn_phase_2_happened = False
king_slime_spawn_phase_3_happened = False
king_slime_spawn_phase_4_happened = False

callback_triggers = {
    "callback_entity_is_hit": [],
    "callback_pc_is_hit": [],
    "callback_enemy_is_hit": [],
    "callback_entity_is_dead": [],
    "callback_pc_is_dead": [],
    "callback_enemy_is_dead": [],
}
player_party = []


def add_callback(trigger, callback):
    # Takes a given "stringified" callback and adds it to the value of a given trigger in callback_triggers
    # To add a callback that should happen every time some*thing* dies:
    # add_callback("callback_entity_is_dead", "something_died")
    trigger.append(callback)

def run_callbacks(trigger, callback_args = None):
    # Takes a given trigger and excecutes all of the callbacks in the trigger's value in callback_triggers
    #
    # callback_args is callback-dependent; some callbacks need some extra info to function
    # ex: take a function that hits the attacking enemy for 1 HP every time a character gets hit called spiked_armor()
    # "spiked_armor" would be in callback_pc_is_hit and would be called by run_callbacks("callback_pc_is_hit", attacker)
    # spiked_armor() would deal damage to the passed attacker
    #
    # issues that needs resolving: 
    # what if another callback was in callback_pc_is_hit that doesn't take anything?
    # what if another callback is expecting something different as an argument?
    # what if another callback expects more than two args?
    # 
    for callback in trigger:
        run_callback = globals()[callback]
        run_callback()

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


# 1 -> 4-5 start
# 2 -> 8-10 start
# 3 -> 12-15 start
# 4 -> 16-20 start



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
    run_callbacks("callback_entity_is_hit")
    run_callbacks("callback_enemy_is_hit")
    if entity_is_dead(target):
        input(f"{target.Name} has fallen!")
        run_callbacks("callback_entity_is_dead")
        run_callbacks("callback_enemy_is_dead")
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
    run_callbacks("callback_entity_is_hit")
    run_callbacks("callback_enemy_is_hit")
    if entity_is_dead(defender):
        input(f"{defender.Name} has fallen!")
        run_callbacks("callback_entity_is_dead")
        run_calbacks("callback_enemy_is_dead")
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
                    entity.level_up(guy, True)
            for guy in player_party:
                entity.level_up(guy, True)
                
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
                entity.level_up(guy, False)
                
        entity.present_player_party_members(player_party)
        if not battle.initiate_battle(player_party, run):
            began = False
        if run <= 4:
            run += 1




while __name__ == "__main__":
    main()
