import os
import entity
import random
import copy
import sys
import subprocess
from entity import Entity
import gamestate
from gamestate import GAME_STATE



#TODO: Replace every instance of the player party or enemy party with the GAME_STATE version
#      DO IT IN PYCHARM BC ITS EASIER



CLEAR = 'cls' if os.name == 'nt' else 'clear'
entities = entity.get_entity_map()

enemy_pools = {
    1: { # First encounter; balanced around level 1 party members
        "encounters": [
            [entities["EnemyWizard"], entities["EnemyWarrior"]],
            [entities["Volakuma"], entities["Volakuma"], entities["Volakuma"]],
            [entities["Slime"], entities["Slime"], entities["Volakuma"]]
        ],
        
        "encounter_dialogue": [
            "You see two adventurers sitting at a campfire...\nThey rise and draw their weapons when they see you!\nAn Enraged Wizard and a Stalwart Warrior draw near!",
            "You hear the shrieking of bats behind you as three black monsters fly above your head!\nThree Volakumas draw near!",
            "As you explore the area, you gather the attention of some slimes and a bat!\nTwo slimes and a Volakuma draw near!"
        ]
    },
    
    2: { # Second encounter; balanced around level 10 party members
        "encounters": [
            [entities["EnragedWarrior"], entities["StalwartWizard"]]
        ],
        
        "encounter_dialogue": [
            "You see two adventurers sitting at a campfire...\nThey rise and draw their weapons when they see you!\nAn Enraged Warrior and a Stalwart Wizard draw near!"
        ]
    },
    
    3: { # Third encounter; balanced around level 20 party members
        "encounters": [
            [entities["DisgracedMonk"], entities["SorcererSupreme"], entities["CraftyThief"]]
        ],
        
        "encounter_dialogue": [
            "You stumble upon a congregation of evildoers while you explore...\nThree adventurers block your path!\nA Disgraced Monk, Sorcerer Supreme, and Crafty Thief draw near!"
        ]
    },
    
    4: { # Fourth encounter; boss monster balanced around level 30 party members
        "encounters": [
            [entities["GelatinousKing"]],
            [entities["StoneGolem"]]
        ],
        
        "encounter_dialogue": [
            "An army of slimes appear from all around and coagulate before you!\nYou face down the boss of the floor; the Gelatinous King!",
            "A collection of boulders rise from the floor and take humanoid shape!\nYou face down the boss of the floor; the Stone Golem!"
        ]
    }
}


# \/\/ NEEDS REWORK \/\/
def initiate_battle(enemy_pool = -9999):
    #For now, I'm just going to have it call run_encounter similarly to how it would will in future
    global entities
    os.system(CLEAR)
    enemies_spawned = []

    # find appropriate encouters and choose one
    possible_encounters = enemy_pools[enemy_pool]["encounters"]
    chosen_encounter = random.randrange(0, len(possible_encounters))
    
    gamestate.print_with_conf("The party encounters a group of enemies!")

    # Spawn 
    if enemy_pool != -9999:
        for enemy in possible_encounters[chosen_encounter]:
            enemy_to_spawn = copy.deepcopy(enemy)
            enemies_spawned.append(enemy_to_spawn)
        gamestate.print_with_conf(enemy_pools[enemy_pool]["encounter_dialogue"][chosen_encounter])
        GAME_STATE.enemy_party = enemies_spawned
        return run_encounter()
    else:
        gamestate.print_with_conf("You didn't, actually, because THE DEV FORGOT TO SET THE ENEMY POOL LIKE A DUMBASS!")
        return False


def find_target(amount_of_enemies):
    target = input("Which numbered enemy would you like to target?")
    while not isinstance(target, int):
        try:
            target = int(target)
        except ValueError:
            print("Please print_with_conf a number correlated to the enemy.")
            gamestate.print_with_conf("Don't print_with_conf anything other than a number!")
            target = input("Which numbered enemy would you like to target?")
    target -= 1
    if target < 0:
        target = 0
    elif target > amount_of_enemies:
        target = amount_of_enemies - 1
    return target

def find_turn_order():
    entity_list = []
    for actors in GAME_STATE.player_party:
        entity_list.append(actors)
    for actors in GAME_STATE.enemy_party:
        entity_list.append(actors)
    return sorted(entity_list, key=lambda x: x.AGI, reverse=True)

def run_encounter():
    
    initiative_list = find_turn_order()
    os.system(CLEAR)
    party_wiped = False
    enemies_are_dead = False
    enemies_spawned = []
    for enemy in GAME_STATE.enemy_party:
        enemies_spawned.append(enemy)
    bloodthirsty_check = None

    # BATTLE STEPS:
    # 1) Turn order list is made
    # 2) Entity takes turn
    # 3) Is removed from turn order list
    # 4) Repeat 2/3 until turn order list is empty
    # 5) Check for flags
    # 6) Repeat until someone's dead!!!
    
    while True:
        while len(initiative_list) > 0:
            actor = initiative_list[0]
            os.system(CLEAR)
            # Check to see if the battle's over BEFORE bloodthirsty/AFTER normal turn
            if check_if_battle_won() is not None:
                if not check_if_battle_won():
                    party_wiped = True
                    break
                elif check_if_battle_won():
                    enemies_are_dead = True
                    break
            
            # Check if the previous turn resulted in someone going bloodthirsty
            if bloodthirsty_check is not None:
                if bloodthirsty_check.EntityType == "PlayerCharacter" or bloodthirsty_check.EntityType == "Khorynn":
                    gamestate.print_with_conf(f"{bloodthirsty_check.Name} is bloodthirsty!")
                    pc_turn_handler(bloodthirsty_check, initiative_list, True)
                    gamestate.print_with_conf(f"{bloodthirsty_check.Name}'s primal rage dims!")
                    os.system(CLEAR)
                elif bloodthirsty_check.EntityType == "Enemy":
                    gamestate.print_with_conf(f"{bloodthirsty_check.Name} is bloodthirsty!")
                    enemy_AI(bloodthirsty_check, initiative_list)
                    gamestate.print_with_conf(f"{bloodthirsty_check.Name}'s primal rage dims!")
                    os.system(CLEAR)
                elif bloodthirsty_check.EntityType == "BossEnemy":
                    gamestate.print_with_conf(f"{bloodthirsty_check.Name} is bloodthirsty!!")
                    logic_to_reference = globals()[bloodthirsty_check.BossLogic]
                    logic_to_reference(bloodthirsty_check, initiative_list, enemies_spawned)
                    gamestate.print_with_conf(f"{bloodthirsty_check.Name}'s primal rage dims!")
                    os.system(CLEAR)
                bloodthirsty_check = None

            if actor.HP <= 0:
                if actor in initiative_list:
                    initiative_list.remove(actor)
                continue
                
            # Check if the battle's over BEFORE normal turn/AFTER bloodthirsty
            if check_if_battle_won() is not None:
                if not check_if_battle_won():
                    party_wiped = True
                    break
                elif check_if_battle_won():
                    enemies_are_dead = True
                    break
                
            # Start of entity's turn
            gamestate.print_with_conf(f"It's {actor.Name}'s turn!")
            
            # Check whether entity is a PC
            if actor.EntityType == "PlayerCharacter" or actor.EntityType == "Khorynn":
                # do PC shit
                bloodthirsty_check = pc_turn_handler(actor, initiative_list, False)
    
            # check if entity is an enemy
            if actor.EntityType == "Enemy":
                # do enemy shit
                bloodthirsty_check = enemy_AI(actor, initiative_list)
    
            if actor.EntityType == "BossEnemy":
                logic_to_reference = globals()[actor.BossLogic]
                bloodthirsty_check = logic_to_reference(actor, initiative_list, enemies_spawned)
    
            initiative_list.remove(actor)
        # check for the flags & win/lose the battle
        if party_wiped:
            return battle_cleanup(enemies_spawned, False)

        elif enemies_are_dead:
            return battle_cleanup(enemies_spawned, True)

        initiative_list = find_turn_order()



def pc_turn_handler(character, turn_order: list[Entity], is_bloodthirsty: bool = False):
    bloodthirsty = None
    turn_is_over = False

    while not turn_is_over:
        cmd = input("Command?\n").strip().lower()
        
        if cmd == "attack":
            # find the target of melee
            target = None
            while target is None:
                try:
                    target = GAME_STATE.enemy_party[find_target(len(GAME_STATE.enemy_party))]
                except IndexError:
                    gamestate.print_with_conf(f"That target doesn't exist! There are only {len(GAME_STATE.enemy_party)} enemies on the field!")
                    target = None
            gamestate.run_callbacks("callback_entity_is_targeted", entity_targeted=target, entity_attacking=character, attacker_action="physical_attack")
            gamestate.run_callbacks("callback_enemy_is_targeted", entity_targeted=target, entity_attacking=character, attacker_action="physical_attack")
            
            # deal damage to it
            damage = damage_calc(character, target, False)
            gamestate.print_with_conf(f"You attack {target.Name} with your weapon, dealing {damage} damage!")
            target.HP -= damage
            gamestate.run_callbacks("callback_entity_is_hit", entity_hit=target, entity_attacker=character)
            gamestate.run_callbacks("callback_enemy_is_hit", entity_hit=target, entity_attacker=character)
            
            if target.HP <= 0:
                gamestate.print_with_conf(f"{target.Name} has fallen!")
                gamestate.run_callbacks("callback_entity_is_dead", entity_dead=target, entity_attacker=character)
                gamestate.run_callbacks("callback_enemy_is_dead", entity_dead=target, entity_attacker=character)
                GAME_STATE.enemy_party.remove(target)
                bloodthirsty = character
                
            turn_is_over = True
        
        elif cmd == "ability":
            bloodthirsty = ability_handler(character, turn_order)
            turn_is_over = True
            
        elif cmd == "pass":
            if is_bloodthirsty:
                gamestate.print_with_conf(f"{character.Name} is enraged! They must attack!")
                turn_is_over = False
            else:
                gamestate.print_with_conf(f"{character.Name} waited to act!")
                turn_is_over = True
            
        else:
            gamestate.print_with_conf("Invalid command!")

    return bloodthirsty
    


def ability_handler(character, turn_order: list[Entity]):
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
                chosen_ability = input("That ability isn't in your learned abilities! Did you change your mind? print_with_conf 'back' to go back.")
                if chosen_ability.strip().lower() == "back":
                    pc_turn_handler(character, turn_order)
                    return None
                    break
                    
        # !!! CRITICAL REMINDER !!!
        # Since checking if anybody's died is too much work to put in here, YOU MUST DO IT IN THE ABILITY SCRIPT!!
        # Forgetting to check if anything's died when you deal damage that *COULD* be lethal is DUMB!!!
        # !!! CRITICAL REMINDER !!!
        bloodthirsty = use_ability(character, turn_order)
            
    # if you don't have an ability, don't let them do anything
    else:
        gamestate.print_with_conf("you don't have an ability dummy")
        pc_turn_handler(character, turn_order)
        return None
    if bloodthirsty == False:
        pc_turn_handler(character, turn_order)
        return None
    return bloodthirsty


###

def check_if_battle_won():
    KhorynnCount = 0
    
    if len(GAME_STATE.player_party) == 0:
        return False
        
    for player_character in GAME_STATE.player_party:
        if player_character.EntityType == "Khorynn":
            KhorynnCount += 1
    if KhorynnCount == 0:
        return False
        
    elif len(GAME_STATE.enemy_party) == 0:
        return True
        
    else:
        return None

def enemy_AI(enemy, turn_order):
    bloodthirsty = None
    
    # choose a random target 
    enemy_target = GAME_STATE.player_party[random.randrange(0, len(GAME_STATE.player_party))]
    
    # check if its mind is higher than its strength and use the higher stat in the damage calc
    if enemy.get_strength() > enemy.get_mind():
        gamestate.run_callbacks("callback_entity_is_targeted", entity_targeted=enemy_target, entity_attacking=enemy, attacker_action="physical_attack")
        gamestate.run_callbacks("callback_pc_is_targeted", entity_targeted=enemy_target, entity_attacking=enemy, attacker_action="physical_attack")
        enemy_damage = damage_calc(enemy, enemy_target, False)
        gamestate.print_with_conf(f"The enemy attacks with their weapon and deals {enemy_damage} damage to {enemy_target.Name}!")
    else:
        gamestate.run_callbacks("callback_entity_is_targeted", entity_targeted=enemy_target, entity_attacking=enemy, attacker_action="magic_attack")
        gamestate.run_callbacks("callback_pc_is_targeted", entity_targeted=enemy_target, entity_attacking=enemy, attacker_action="magic_attack")
        enemy_damage = damage_calc(enemy, enemy_target, True)
        gamestate.print_with_conf(f"The enemy casts a spell and deals {enemy_damage} damage to {enemy_target.Name}!")
        
    # deal damage
    enemy_target.HP -= enemy_damage
    if enemy_target.HP < 0:
        enemy_target.HP = 0
    gamestate.run_callbacks("callback_entity_is_hit", entity_hit=enemy_target, entity_attacker=enemy)
    gamestate.run_callbacks("callback_pc_is_hit", entity_hit=enemy_target, entity_attacker=enemy)
    gamestate.print_with_conf(f"{enemy_target.Name} is at {enemy_target.HP}/{enemy_target.MaxHP} HP!")
    
    # check if the character died
    if enemy_target.HP <= 0:
        gamestate.print_with_conf(f"{enemy_target.Name} Has Fallen!")
        gamestate.run_callbacks("callback_entity_is_dead", entity_dead=enemy_target, entity_attacker=enemy)
        gamestate.run_callbacks("callback_pc_is_dead", entity_dead=enemy_target, entity_attacker=enemy)
        bloodthirsty = enemy
        GAME_STATE.player_party.remove(enemy_target)
    return bloodthirsty


def damage_calc(attacker, defender, magic: bool = False, crit_enabled: bool = True):
    
    if crit_enabled:
        critical = 2 if random.uniform(0, 1) >= 0.95 else 1
    else:
        critical = 1
    level_differential = 1 + (attacker.Level / 40) - (defender.Level / 40)
    if level_differential <= 0:
        level_differential = 0.001
    
    if critical > 1:
        print("It's a critical hit!")

    defense = defender.get_res()
    attack = attacker.get_strength() if not magic else attacker.get_mind()
    
    if not magic:
        if attack >= defense:
            damage = attack * 2 - defense
        else:
            damage = attack * attack / defense

        damage = int(damage * random.uniform(0.9, 1.1)) * critical

        if damage >= 0:
            return damage
        else:
            return 0

    elif magic:
        defense -= int(defense * 0.2)
        if attack >= defense:
            damage = attack * 2 - defense
        else:
            damage = attack * attack / defense

        damage = int(damage * random.uniform(0.9, 1.1)) * critical

        if damage >= 0:
            return damage
        else:
            return 0
    else:
        print("You forgot to set magic, dumbass.")
        return 0
    

def battle_cleanup(enemies, won_battle = True):
    os.system(CLEAR)
    xp_to_gain = 0
    money_to_gain = 0
    if won_battle == True:
        print("B A T T L E  W O N !")
        for actors in enemies:
            print(f"You defeated {actors.Name}!")
            xp_to_gain += actors.EXP_Reward
            money_to_gain += actors.Money_Reward
        gamestate.print_with_conf(f"You earned {xp_to_gain} EXP and found {money_to_gain} gold!")
        for pc in GAME_STATE.player_party:
            pc.StatChanges["STR"] = 0
            pc.StatChanges["RES"] = 0
            pc.StatChanges["MND"] = 0
            pc.StatChanges["AGI"] = 0
        GAME_STATE.xp_count += xp_to_gain
        GAME_STATE.money += money_to_gain
    if won_battle == False:
        gamestate.print_with_conf("Khorynn's party wiped! You lose!")
    return won_battle

def king_slime(gel_king, initiative_list, enemies_spawned):
    bloodthirsty = None

    if "king_slime_spawn_phase_handler" not in gamestate.get_callback_triggers_map()["callback_enemy_is_hit"]:
        gamestate.add_callback("callback_enemy_is_hit", king_slime_spawn_phase_handler)
    if "king_slime_death_logic" not in gamestate.get_callback_triggers_map()["callback_enemy_is_dead"]:
        gamestate.add_callback("callback_enemy_is_dead", "king_slime_death_logic")

    enemy_target = None
    for player_character in GAME_STATE.player_party:
        if damage_calc(gel_king, player_character, False, False) > player_character.HP:
            enemy_target = player_character
            break
    enemy_target = random.choice(GAME_STATE.player_party) if enemy_target == None else enemy_target
    enemy_damage = damage_calc(gel_king, enemy_target, False)
    gamestate.print_with_conf(f"The King jumps to {enemy_target.Name} and smothers them with its ginormous body, dealing {enemy_damage} damage!")
    enemy_target.HP -= enemy_damage
    # make sure the character doesn't have negative health
    if enemy_target.HP < 0:
        enemy_target.HP = 0
    # let the player know what health they're at
    gamestate.print_with_conf(f"{enemy_target.Name} is at {enemy_target.HP}/{enemy_target.MaxHP} HP!")
    # check if the character died
    if enemy_target.HP <= 0:
        gamestate.print_with_conf(f"{enemy_target.Name} Has Fallen!")
        bloodthirsty = gel_king
        GAME_STATE.player_party.remove(enemy_target)
    return bloodthirsty 


def king_slime_spawn_phase_handler(entity_hit, entity_attacker):
    # Make sure we're working with the boss
    if entity_hit.Name == "Gelatinous King" and entity_hit.EntityType == "BossEnemy":
        gel_king = entity_hit
    else:
        return

    # At 80% health, spawn 1 servant
    if gel_king.HP < int(gel_king.MaxHP * 0.8):
        if gel_king.Phases["Spawn Phase 1"] == False:
            GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])
            gamestate.print_with_conf("The Gelatinous King's gel wobbles...\nA Gelatinous Servent erupts from the King and joins the fight!")
            GAME_STATE.enemy_party.append(GelatinousServant)
            initiative_list.append(GelatinousServant)
            enemies_spawned.append(GelatinousServant)
            gel_king.Phases["Spawn Phase 1"] = True

    # At 60% health, spawn another servant
    if gel_king.HP < int(gel_king.MaxHP * 0.6):
        if gel_king.Phases["Spawn Phase 2"] == False:
            GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])
            gamestate.print_with_conf("The Gelatinous King ejects another Servant from its wounded flesh!")
            GAME_STATE.enemy_party.append(GelatinousServant)
            initiative_list.append(GelatinousServant)
            enemies_spawned.append(GelatinousServant)
            gel_king.Phases["Spawn Phase 2"] 

    # At 40% health, spawn 2 servants
    if gel_king.HP < int(gel_king.MaxHP * 0.4):
        if gel_king.Phases["Spawn Phase 3"] == False:
            gamestate.print_with_conf("The Gelatinous King is falling apart! Two servants are ripped from the main body!")
            for _ in range(2):
                GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])                
                GAME_STATE.enemy_party.append(GelatinousServant)
                initiative_list.append(GelatinousServant)
                enemies_spawned.append(GelatinousServant)
            gel_king.Phases["Spawn Phase 3"] = True

    # At 20% helath, spawn 3 servants
    if gel_king.HP < int(gel_king.MaxHP * 0.2):
        if gel_king.Phases["Spawn Phase 4"] == False:
            gamestate.print_with_conf("The Gelatinous King is almost dead!\nThree Gelatinous Servants stream like a river from its flesh!")
            for _ in range(3):
                GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])
                GAME_STATE.enemy_party.append(GelatinousServant)
                initiative_list.append(GelatinousServant)
                enemies_spawned.append(GelatinousServant)   
            gel_king.Phases["Spawn Phase 4"] = True    

def king_slime_death_logic(entity_dead, entity_attaker, cause_of_death):
    if entity_dead.Name == "Gelatinous King" and entity_dead.EntityType == "BossEnemy":
        gamestate.print_with_conf("The Gelatinous King's body ruptures, its body fracturing into five Servants!")
        for _ in range(5):
            GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])
            GAME_STATE.enemy_party.append(GelatinousServant)
            initiative_list.append(GelatinousServant)
            enemies_spawned.append(GelatinousServant) 
        gamestate.remove_callback("callback_enemy_is_hit", "king_slime_spawn_phase_handler")
        gamestate.remove_callback("callback_enemy_is_dead", "king_slime_death_logic")
    else:
        return


def stone_golem(golem, initiative_list, enemies_spawned):
    if "stone_golem_phase_handler" not in gamestate.get_callback_triggers_map()["callback_enemy_is_hit"]:
        gamestate.add_callback("callback_enemy_is_hit", "stone_golem_phase_handler")
    if "stone_golem_death_logic" not in gamestate.get_callback_triggers_map()["callback_enemy_is_dead"]:
        gamestate.add_callback("callback_enemy_is_dead", "stone_golem_death_logic")


    cant_see_kill = True
    for player_character in GAME_STATE.player_party:
        if damage_calc(gel_king, player_character, False, False) > player_character.HP:
            enemy_target = player_character
            cant_see_kill = False
            break
    if cant_see_kill:
        enemy_target = random.choice(GAME_STATE.player_party)
        
    enemy_damage = damage_calc(golem, enemy_target, False)

    def golem_normal_attack(phase):
        nonlocal golem
        nonlocal initiative_list
        nonlocal enemies_spawned
        nonlocal enemy_target
        nonlocal enemy_damage

        gamestate.run_callbacks("callback_entity_is_targeted")
        gamestate.run_callbacks("callback_pc_is_targeted")
        
        if phase == 1:
            gamestate.print_with_conf(f"The Golem slams its boulder fists down on {enemy_target.Name} and deals {enemy_damage}!")
        else:
            gamestate.print_with_conf(f"The Golem rushes towards {enemy_target.Name} with undiluted rage!\nIt runs them over and deals {enemy_damage} damage!!")
            
        enemy_target.HP -= enemy_damage
        if enemy_target.HP < 0:
            enemy_target.HP = 0
            
        gamestate.run_callbacks("callback_entity_is_hit", entity_hit=enemy_target, 
                           entity_attacker=golem)
        gamestate.run_callbacks("callback_pc_is_hit", entity_hit=enemy_target, 
                           entity_attacker=golem)
        
        gamestate.print_with_conf(f"{enemy_target.Name} is at {enemy_target.HP}/{enemy_target.MaxHP} HP!")
        # check if the character died
        if enemy_target.HP <= 0:
            gamestate.print_with_conf(f"{enemy_target.Name} Has Fallen!")
            gamestate.run_callbacks("callback_entity_is_dead", entity_dead=enemy_target, entity_attacker=golem)
            gamestate.run_callbacks("callback_pc_is_dead", entity_dead=enemy_target, entity_attacker=golem)
            bloodthirsty = golem
            GAME_STATE.player_party.remove(enemy_target)

    
    if not golem.Phases["Phase 2"]:
        golem_normal_attack(1)

    
    elif golem.Phases["Phase 2"]:
        if not cant_see_kill:
            golem_normal_attack(2)

        elif cant_see_kill:
            move_selection = random.choice["normal_attack", "area_attack"]
            if move_selection == "normal_attack":
                golem_normal_attack(2)
            elif move_selection == "area_attack":
                gamestate.print_with_conf("The Golem swings in a wide arc that hits the enitre party!!!")
                enemy_target = GAME_STATE.player_party
                for pc in enemy_target:
                    enemy_damage = int(damage_calc(golem, pc, False) * 0.6)
                    gamestate.print_with_conf(f"{pc.Name} takes {enemy_damage} damage!")
                    gamestate.run_callbacks("callback_entity_is_hit", entity_hit=pc, 
                                   entity_attacker=golem)
                    gamestate.run_callbacks("callback_pc_is_hit", entity_hit=pc, 
                                       entity_attacker=golem)
                    
                    gamestate.print_with_conf(f"{pc.Name} is at {pc.HP}/{pc.MaxHP} HP!")
                    # check if the character died
                    if pc.HP <= 0:
                        gamestate.print_with_conf(f"{pc.Name} Has Fallen!")
                        gamestate.run_callbacks("callback_entity_is_dead", entity_dead=pc, entity_attacker=golem)
                        gamestate.run_callbacks("callback_pc_is_dead", entity_dead=pc, entity_attacker=golem)
                        bloodthirsty = golem
                        GAME_STATE.player_party.remove(pc)

        
    return bloodthirsty

def stone_golem_phase_handler(entity_hit, entity_attacker):
    if entity_hit.Name == "Stone Golem" and entity_hit.EntityType == "BossEnemy":
        golem = entity_hit
    else:
        return

    if golem.HP <= int(golem.MaxHP / 2):
        if not golem.Phases["Phase 2"]:
            print("The Stone Golem is starting to crack! A high-pitch shriek reverberates around you as it arches back in rage!")
            gamestate.print_with_conf("The Stone Golem's attack increases drastically! It becomes considerably more aggressive!")
            golem.change_stat("STR", 4)
            gamestate.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=golem, stat_changed="STR", change_stages=4)
            golem.Phases["Phase 2"] = True


def stone_golem_death_logic(entity_dead, entity_attaker, cause_of_death):
    if entity_dead.Name == "Stone Golem" and entity_dead.EntityType == "Boss Enemy":
        gamestate.print_with_conf("The Stone Golem's body crumbles into rubble!")
        gamestate.remove_callback("callback_enemy_is_hit", "stone_golem_phase_handler")
        gamestate.remove_callback("callback_enemy_is_dead", "stone_golem_death_logic")
    else:
        return

#####################################
# \/\/\/ Ability Functions \/\/\/
#####################################

def skull_crusher(user, inititive_list):
    bloodthirsty = None
    
    if user.MP < 3:
        gamestate.print_with_conf(f"{user.Name} didn't have enough MP to use Skull Crusher!")
        return False
        
    target = GAME_STATE.enemy_party[find_target(len(GAME_STATE.enemy_party))]
    gamestate.run_callbacks("callback_entity_is_targeted", entity_targeted=target, entity_attacking=user, attacker_action="physical_attack")
    gamestate.run_callbacks("callback_enemy_is_targeted", entity_targeted=target, entity_attacking=user, attacker_action="physical_attack")
    
    gamestate.print_with_conf(f"{user.Name} uses Skull Crusher!")
    user.MP -= 3
    gamestate.print_with_conf("They siphon 3 points of MP!")
    gamestate.print_with_conf(f"{user.Name} slams their weapon onto {target.Name}'s head with a horrifying CRACK!")
    damage = int(damage_calc(user, target, False))
    gamestate.print_with_conf(f"They deal {damage} damage!")
    target.HP -= damage
    gamestate.run_callbacks("callback_entity_is_hit", entity_hit=target, entity_attacker=user)
    gamestate.run_callbacks("callback_enemy_is_hit", entity_hit=target, entity_attacker=user)
    if target.HP <= 0:
        gamestate.print_with_conf(f"{target.Name} has fallen!")
        gamestate.run_callbacks("callback_entity_is_dead", entity_dead=target, entity_attacker=user)
        gamestate.run_callbacks("callback_enemy_is_dead", entity_dead=target, entity_attacker=user)
        GAME_STATE.enemy_party.remove(target)
        inititive_list.remove(target)
        bloodthirsty = user
    else:
        gamestate.print_with_conf(f"{target.Name}'s resilience was lowered one stage!")
        target.change_stat("RES", -1)
        gamestate.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=target, stat_changed="RES", change_stages=-1)
    gamestate.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=target, spell_casted="skull_crusher")
    return bloodthirsty


def forfireball(user, inititive_list):
    if user.MP < 40:
        gamestate.print_with_conf(f"{user.Name} tried to use Fireball, but its immense mana cost proved too much for them!")
        return False
    
    defender = GAME_STATE.enemy_party[find_target(len(GAME_STATE.enemy_party))]
    gamestate.run_callbacks("callback_entity_is_targeted", entity_targeted=defender, entity_attacking=user, attacker_action="magic_attack")
    gamestate.run_callbacks("callback_enemy_is_targeted", entity_targeted=defender, entity_attacking=user, attacker_action="magic_attack")
    user.MP -= 40
    
    gamestate.print_with_conf(f"{user.Name} casts Fireball!")
    defense_ignored = defender.get_res()
    defender.RES -= defense_ignored
    gamestate.print_with_conf("Even the most powerful defenses shatter when the shockwave hits it!")
    damage = damage_calc(user, defender, True) * 2
    defender.RES += defense_ignored
    
    gamestate.print_with_conf(f"{defender.Name} takes {damage} damage!")
    defender.HP -= damage
    gamestate.run_callbacks("callback_entity_is_hit", entity_hit=defender, entity_attacker=user)
    gamestate.run_callbacks("callback_enemy_is_hit", entity_hit=defender, entity_attacker=user)
    if defender.HP <= 0:
        gamestate.print_with_conf(f"{defender.Name} has fallen!")
        gamestate.run_callbacks("callback_entity_is_dead", entity_dead=defender, entity_attacker=user)
        gamestate.run_callbacks("callback_enemy_is_dead", entity_dead=defender, entity_attacker=user)
        GAME_STATE.enemy_party.remove(defender)
        inititive_list.remove(defender)
        return user
    return None


def focus(user, turn_order):
    mind_multiple = (user.get_mind() * 0.05) + 1
    if mind_multiple > 5:
        mind_multiple = 5
        
    if user.MP < 5:
        gamestate.print_with_conf(f"{user.Name} tried to use Focus, but they didn't have enough MP!")
        return False
    else:
        user.MP -= 5
        gamestate.print_with_conf(f"{user.Name} used Focus!")
        gamestate.print_with_conf("They take a deep breath and center their thoughts...")
        gamestate.print_with_conf("They feel better already!")
        health_to_heal = int(user.MaxHP * 0.1 + user.get_mind())
        if (health_to_heal + user.HP) > user.MaxHP:
            health_to_heal = user.MaxHP - user.HP
        gamestate.print_with_conf(f"{user.Name} heals {health_to_heal} HP!")
        user.HP += health_to_heal
        gamestate.print_with_conf("They gain a temporary boost to Mind!")
        user.change_stat("MND", 1)
        gamestate.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=user, spell_casted="focus")
        gamestate.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=user, stat_changed="MND", change_stages=1)


def slap(user, turn_order):
    gamestate.print_with_conf(f"{user.Name} is panicking!")
    panic_thoughts = [
        f"{user.Name} thinks they left their refridgerator running!",
        f"{user.Name} suddenly forgets everything they were doing!",
        f"{user.Name} suddenly finds images of malformed monkeys very valuable!",
        f"{user.Name} realizes that their parents were right about their worthlessness!",
        f"{user.Name} remembers that one cringy thing they did when they were a kid!",
        f"{user.Name} shits the bed!"
    ]
    chosen_thought = random.choice(panic_thoughts)
    gamestate.print_with_conf(f"{chosen_thought}")
    gamestate.print_with_conf("They slap themselves to regain composure!")
    damage = damage_calc(user, user, False)
    gamestate.print_with_conf(f"They suffer {damage} damage!")
    user.HP -= damage
    gamestate.run_callbacks("callback_entity_is_hit", entity_hit=user, entity_attacker=user)
    gamestate.run_callbacks("callback_pc_is_hit", entity_hit=user, entity_attacker=user)
    if user.HP <= 0:
        gamestate.print_with_conf(f"{user.Name} killed themself!")
        gamestate.run_callbacks("callback_entity_is_dead", entity_dead=user, entity_attacker=user)
        gamestate.run_callbacks("callback_pc_is_dead", entity_dead=user, entity_attacker=user)
        GAME_STATE.player_party.remove(user)
        return None
    gamestate.print_with_conf(f"{user.Name}'s mind settles!")
    user.change_stat("MND", 1)
    gamestate.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=user, spell_casted="slap")
    gamestate.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=user, stat_changed="MND", change_stages=1)    
    return None

def spark(user, turn_order):
    if user.MP < 4:
        gamestate.print_with_conf(f"{user.Name} didn't have enough MP to use Spark!")
        return False
    defender = GAME_STATE.enemy_party[find_target(len(GAME_STATE.enemy_party))]
    gamestate.run_callbacks("callback_entity_is_targeted", entity_targeted=defender, entity_attacking=user, attacker_action="magic_attack")
    gamestate.run_callbacks("callback_enemy_is_targeted", entity_targeted=defender, entity_attacking=user, attacker_action="magic_attack")
    user.MP -= 4

    gamestate.print_with_conf(f"{user.Name} casts Spark!")
    gamestate.print_with_conf(f"A small flare shoots out from {user.Name}'s hand!")
    damage = damage_calc(user, defender, True)
    
    gamestate.print_with_conf(f"{defender.Name} takes {damage} damage!")
    defender.HP -= damage
    gamestate.run_callbacks("callback_entity_is_hit", entity_hit=defender, entity_attacker=user)
    gamestate.run_callbacks("callback_enemy_is_hit", entity_hit=defender, entity_attacker=user)
    if defender.HP <= 0:
        gamestate.print_with_conf(f"{defender.Name} has fallen!")
        gamestate.run_callbacks("callback_entity_is_dead", entity_dead=defender, entity_attacker=user)
        gamestate.run_callbacks("callback_enemy_is_dead", entity_dead=defender, entity_attacker=user)
        GAME_STATE.enemy_party.remove(defender)
        return user
    gamestate.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=defender, spell_casted="spark")
    return None
    
def heal(user, turn_order):
    if user.MP < 6:
        gamestate.print_with_conf(f"{user.Name} didn't have enough MP to use Heal!")
        return False
    print("Party:")
    for pc in GAME_STATE.player_party:
        print(f"{pc.Name}")
    pc_to_heal = input("(INPUT PLAYER CHARACTER NAME) Which party member would you like to heal?").lower().strip()
    for character in GAME_STATE.player_party:
        if character.Name.lower() == pc_to_heal:
            pc_to_heal = character
            break
    gamestate.print_with_conf(f"{user.Name} focuses on calming things...")
    gamestate.print_with_conf("They siphon 6 MP!")
    gamestate.print_with_conf(f"{user.Name} casts Heal!")
    HP_to_heal = int(user.MaxHP * 0.2) + user.get_mind()
    HP_to_heal = pc_to_heal.MaxHP - pc_to_heal.HP if pc_to_heal.HP + HP_to_heal > pc_to_heal.MaxHP else HP_to_heal
    gamestate.print_with_conf(f"They heal {pc_to_heal.Name} for {HP_to_heal} HP!")
    pc_to_heal.HP += HP_to_heal
    gamestate.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=pc_to_heal, spell_casted="heal")
    return None

def resilience_prayer(user, turn_order):
    if user.MP < 20:
        gamestate.print_with_conf(f"{user.Name} didn't have enough MP to use Resilience Prayer!")
        return False
    gamestate.print_with_conf(f"{user.Name} kneels down and prays for everyone to be safe...")
    for pc in GAME_STATE.player_party:
        pc.change_stat("RES", 1)
    gamestate.print_with_conf("Everyone feels a little tougher! Party's resilience increases one stage!")
    gamestate.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=GAME_STATE.player_party, spell_casted="resilience_prayer")
    for pc in GAME_STATE.player_party:
        gamestate.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=pc, stat_changed="RES", change_stages=1)    
    return None

def talk(user, turn_order):
    target_found = False
    
    while not target_found:
        target = GAME_STATE.enemy_party[find_target(len(GAME_STATE.enemy_party))]
        target_found = True
        if target.EntityType == "BossEnemy":
            gamestate.print_with_conf("Something tells you that you can't calm that one down!")
            target_found = False
            
    gamestate.print_with_conf(f"{user.Name} attempts to calm the {target.Name} down!")
    if target.MND == 0:
        gamestate.print_with_conf(f"But it's no use! The {target.Name} can't understand them at all!")
        return None
    elif target.Level > int(target.MND / 10):
        gamestate.print_with_conf(f"Most of your words fly over the enemy's head, but you might be convincing them...!")
