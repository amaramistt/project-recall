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
    1: { # First floor encounters; balanced around early level party members
        "encounters": [
            [entities["EnemyWizard"], entities["EnemyWarrior"]],
            [entities["Volakuma"], entities["Volakuma"], entities["Volakuma"]],
            [entities["Slime"], entities["Slime"], entities["Volakuma"]]
        ],
        
        "encounter_dialogue": [
            "You see two adventurers sitting at a campfire...\nThey rise and draw their weapons when they see you!\nAn Enraged Wizard and a Stalwart Warrior draw near!",
            "You hear the shrieking of bats behind you as three black monsters fly above your head!\nThree Volakumas draw near!",
            "As you explore the area, you gather the attention of some slimes and a bat!\nTwo slimes and a Volakuma draw near!"
        ],
        
        "bosses": [
            [entities["GelatinousKing"]]
        ],
        "boss_dialogue": [
            "An army of slimes appear from all around and merge into one before you!\nYou face down the boss of the floor; the Gelatinous King!",
        ]
    },
    
    2: { # Second encounter; balanced around early-mid level party members
        "encounters": [
            [entities["EnragedWarrior"], entities["StalwartWizard"]]
        ],
        
        "encounter_dialogue": [
            "You see two adventurers sitting at a campfire...\nThey rise and draw their weapons when they see you!\nAn Enraged Warrior and a Stalwart Wizard draw near!"
        ]
    },
    
    3: { # Third encounter; balanced around mid-late level party members
        "encounters": [
            [entities["DisgracedMonk"], entities["SorcererSupreme"], entities["CraftyThief"]]
        ],
        
        "encounter_dialogue": [
            "You stumble upon a congregation of evildoers while you explore...\nThree adventurers block your path!\nA Disgraced Monk, Sorcerer Supreme, and Crafty Thief draw near!"
        ]
    },
    
    4: { # Fourth encounter; final boss monster balanced around endgame level party members
        "encounters": [
            [entities["GelatinousKing"]],
            [entities["StoneGolem"]]
        ],
        
        "encounter_dialogue": [
            "An army of slimes appear from all around and merge into one before you!\nYou face down the boss of the floor; the Gelatinous King!",
            "A collection of boulders rise from the floor and take humanoid shape!\nYou face down the boss of the floor; the Stone Golem!"
        ]
    }
}


def initiate_battle(enemy_pool = None, spawn_boss = False):
    os.system(CLEAR)
    enemies_spawned = []

    gamestate.print_with_conf("The party encounters a group of enemies!")

    # Spawn 
    if enemy_pool is not None:
        if not spawn_boss:
            possible_encounters = enemy_pools[enemy_pool]["encounters"]
        else:
            possible_encounters = enemy_pools[enemy_pool]["boss_encounters"]            
        chosen_encounter = random.randrange(0, len(possible_encounters))            
        for enemy in possible_encounters[chosen_encounter]:
            enemy_to_spawn = Entity.copy(enemy)
            enemies_spawned.append(enemy_to_spawn)
        gamestate.print_with_conf(enemy_pools[enemy_pool]["encounter_dialogue"][chosen_encounter])
        GAME_STATE.enemy_party = enemies_spawned
        return run_encounter()

    else:
        gamestate.print_with_conf("You didn't, actually, because THE DEV FORGOT TO SET THE ENEMY POOL LIKE A DUMBASS!")
        return False


def pc_find_target():
    amount_of_enemies = len(GAME_STATE.enemy_party)
    print("ENEMIES")
    for _ in range(amount_of_enemies):
        print(f"Enemy {_ + 1}: {GAME_STATE.enemy_party[_].Name}")
    print()
    target = input("(INPUT NUM) Which numbered enemy would you like to target?    ")
    while not isinstance(target, int):
        try:
            target = int(target)
        except ValueError:
            print("Please input a number correlated to the enemy.")
            gamestate.print_with_conf("Don't input anything other than a number!", True)
            target = input("(INPUT NUM) Which numbered enemy would you like to target?    ")
    target -= 1
    if target < 0:
        target = 0
    elif target > amount_of_enemies:
        target = amount_of_enemies - 1
    target = GAME_STATE.enemy_party[target]
    return target


def find_turn_order():
    entity_list = []
    for actors in GAME_STATE.player_party:
        entity_list.append(actors)
    for actors in GAME_STATE.enemy_party:
        entity_list.append(actors)
    return sorted(entity_list, key=lambda x: x.AGI, reverse=True)


def run_encounter():
    GAME_STATE.in_battle = True
    GAME_STATE.turn_order = find_turn_order()
    party_wiped = False
    enemies_are_dead = False
    enemies_spawned = []
    for enemy in GAME_STATE.enemy_party:
        enemies_spawned.append(enemy)
    bloodthirsty_check = None
    os.system(CLEAR)
    
    # BATTLE STEPS:
    # 1) Turn order list is made
    # 2) Entity takes turn
    # 3) Is removed from turn order list
    # 4) Repeat 2/3 until turn order list is empty
    # 5) Check for flags
    # 6) Repeat until someone's dead!!!
    
    while True:
        while len(GAME_STATE.turn_order) > 0:
            actor = GAME_STATE.turn_order[0]
            os.system(CLEAR)
            # Check to see if the battle's over BEFORE bloodthirsty/AFTER normal turn

            GAME_STATE.battle_entity_targeted = None
            GAME_STATE.battle_entity_attacking = None
            if actor.HP <= 0:
                if actor in GAME_STATE.turn_order:
                    GAME_STATE.turn_order.remove(actor)
                continue

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
                    pc_turn_handler(bloodthirsty_check, True)
                    gamestate.print_with_conf(f"{bloodthirsty_check.Name}'s primal rage dims!")
                    os.system(CLEAR)
                elif bloodthirsty_check.EntityType == "Enemy":
                    gamestate.print_with_conf(f"{bloodthirsty_check.Name} is bloodthirsty!")
                    enemy_AI(bloodthirsty_check,)
                    gamestate.print_with_conf(f"{bloodthirsty_check.Name}'s primal rage dims!")
                    os.system(CLEAR)
                elif bloodthirsty_check.EntityType == "BossEnemy":
                    gamestate.print_with_conf(f"{bloodthirsty_check.Name} is bloodthirsty!!")
                    logic_to_reference = globals()[bloodthirsty_check.BossLogic]
                    logic_to_reference(bloodthirsty_check, enemies_spawned)
                    gamestate.print_with_conf(f"{bloodthirsty_check.Name}'s primal rage dims!")
                    os.system(CLEAR)
                bloodthirsty_check = None

            
            GAME_STATE.battle_entity_targeted = None
            GAME_STATE.battle_entity_attacking = None
            if actor.HP <= 0:
                if actor in GAME_STATE.turn_order:
                    GAME_STATE.turn_order.remove(actor)
                continue
            
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
                bloodthirsty_check = pc_turn_handler(actor, False)
    
            # check if entity is an enemy
            if actor.EntityType == "Enemy":
                # do enemy shit
                bloodthirsty_check = enemy_AI(actor)
    
            if actor.EntityType == "BossEnemy":
                logic_to_reference = globals()[actor.BossLogic]
                bloodthirsty_check = logic_to_reference(actor, enemies_spawned)
    
            GAME_STATE.turn_order.remove(actor)
            
        # check for the flags & win/lose the battle
        if party_wiped:
            return battle_cleanup(enemies_spawned, False)

        elif enemies_are_dead:
            return battle_cleanup(enemies_spawned, True)

        GAME_STATE.turn_order = find_turn_order()



def pc_turn_handler(character, is_bloodthirsty: bool = False):
    bloodthirsty = None
    turn_is_over = False

    while not turn_is_over:
        cmd = input("Command?\n").strip().lower()
        
        if cmd == "attack":
            # find the target of melee

            GAME_STATE.battle_entity_attacking = character
            gamestate.run_callbacks("callback_entity_is_targeted", attacker_action="physical_attack")
            gamestate.run_callbacks("callback_enemy_is_targeted", attacker_action="physical_attack")
            if GAME_STATE.battle_entity_targeted is None:
                GAME_STATE.battle_entity_targeted = pc_find_target()

            
            # deal damage to it
            if isinstance(GAME_STATE.battle_entity_targeted, list):
                damage_falloff = 1
                gamestate.print_with_conf(f"{character.Name} attacks with their weapon and hits all of the enemies!")
                
                enemies_to_attack = []
                for victim in GAME_STATE.battle_entity_targeted:
                    enemies_to_attack.append(victim)
                
                for victim in enemies_to_attack:
                    damage = int(damage_calc(character, victim, False) * damage_falloff)
                    gamestate.print_with_conf(f"{victim.Name} takes {damage} damage!")
                    bloodthirsty = gamestate.deal_damage_to_target(character, victim, damage)
                    damage_falloff = damage_falloff - 0.1 if damage_falloff > 0.1 else 0.1
            else:
                gamestate.print_with_conf(f"{character.Name} attacks with their weapon and hits {GAME_STATE.battle_entity_targeted.Name}!")
                damage = damage_calc(character, GAME_STATE.battle_entity_targeted, False)
                gamestate.print_with_conf(f"They deal {damage} damage!")
                bloodthirsty = gamestate.deal_damage_to_target(character, GAME_STATE.battle_entity_targeted, damage)
            
            turn_is_over = True
        
        elif cmd == "ability":
            bloodthirsty = ability_handler(character)
            turn_is_over = True
            
        elif cmd == "pass":
            if is_bloodthirsty:
                gamestate.print_with_conf(f"{character.Name} is enraged! They must attack!")
            else:
                gamestate.print_with_conf(f"{character.Name} waited to act!")
                turn_is_over = True

        elif cmd == "item":
            if is_bloodthirsty:
                gamestate.print_with_conf(f"{character.Name} is enraged! They must attack!")
            else:
                if battle_item_handler(character) == "backed_out":
                    continue
                else:
                    turn_is_over = True
        else:
            gamestate.print_with_conf("Invalid command!")

    return bloodthirsty
    

def battle_item_handler(character):
    turn_is_over = False
    while not turn_is_over:    
        
        os.system(CLEAR)
        for _ in range(len(character.Items)):
            print(f"Item {_ + 1}: {character.Items[_]}")
        print()
    
        cmd = input("(INPUT NUM) Input the numbered item you would like to operate on! Input anything else to go back.    ")
        while not isinstance(cmd, int):
            try:
                cmd = int(cmd)
                chosen_item = character.Items[cmd - 1]
            except ValueError:
                return "backed_out"
                
        if chosen_item.ItemType == "equip" and character.Job != "monk":
            print("Would you like to 'equip' this item?")
        cmd2 = input("Would you like to 'use' this item?\n(INPUT) Input anything else to go back.   ").lower().strip()
        
        if cmd2 == "equip":
            if chosen_item.ItemType == "equip":
                if character.Job != "monk":
                    chosen_item.equip(character)
                else:
                    if chosen_item.ItemSubtype == "weapon":
                        input(f"{character.Name} is a Monk! They can't equip weapons!")
                    else:
                        chosen_item.equip(character)
                    
        elif cmd2 == "use":
            if chosen_item.use() == "dont_end_turn":
                return "backed_out"
            turn_is_over = True
            
        else:
            return "backed_out"
            


def ability_handler(character):
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
                    pc_turn_handler(character)
                    return None
                    break
                    
        # !!! CRITICAL REMINDER !!!
        # Since checking if anybody's died is too much work to put in here, YOU MUST DO IT IN THE ABILITY SCRIPT!!
        # Forgetting to check if anything's died when you deal damage that *COULD* be lethal is DUMB!!!
        # !!! CRITICAL REMINDER !!!
        bloodthirsty = use_ability(character)
            
    # if you don't have an ability, don't let them do anything
    else:
        gamestate.print_with_conf("you don't have an ability dummy")
        pc_turn_handler(character)
        return None
    if bloodthirsty == False:
        pc_turn_handler(character)
        return None
    return bloodthirsty


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

def enemy_AI(enemy):
    bloodthirsty = None
    
    # choose a random target 
    GAME_STATE.battle_entity_targeted = GAME_STATE.player_party[random.randrange(0, len(GAME_STATE.player_party))]
    
    # check if its mind is higher than its strength and use the higher stat in the damage calc
    if enemy.get_strength() > enemy.get_mind():
        gamestate.run_callbacks("callback_entity_is_targeted", attacker_action="physical_attack")
        gamestate.run_callbacks("callback_pc_is_targeted", attacker_action="physical_attack")
        enemy_damage = damage_calc(enemy, GAME_STATE.battle_entity_targeted, False)
        gamestate.print_with_conf(f"The enemy attacks with their weapon and deals {enemy_damage} damage to {GAME_STATE.battle_entity_targeted.Name}!")
    else:
        gamestate.run_callbacks("callback_entity_is_targeted", attacker_action="magic_attack")
        gamestate.run_callbacks("callback_pc_is_targeted", attacker_action="magic_attack")
        enemy_damage = damage_calc(enemy, GAME_STATE.battle_entity_targeted, True)
        gamestate.print_with_conf(f"The enemy casts a spell and deals {enemy_damage} damage to {GAME_STATE.battle_entity_targeted.Name}!")
        
    bloodthirsty = gamestate.deal_damage_to_target(enemy, GAME_STATE.battle_entity_targeted, enemy_damage)
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
    jexp_to_gain = 0
    if won_battle == True:
        print("B A T T L E  W O N !")
        for actors in enemies:
            print(f"You defeated {actors.Name}!")
            xp_to_gain += actors.EXP_Reward
            money_to_gain += actors.Money_Reward
            if actors.EntityType == "BossEnemy":
                jexp_to_gain += 3
            else:
                jexp_to_gain += 1
        GAME_STATE.in_battle = False
        gamestate.print_with_conf(f"You earned {xp_to_gain} EXP and found {money_to_gain} gold!")
        gamestate.print_with_conf(f"You earned {jexp_to_gain} Job EXP!")
        for pc in GAME_STATE.player_party:
            pc.StatChanges["STR"] = 0
            pc.StatChanges["RES"] = 0
            pc.StatChanges["MND"] = 0
            pc.StatChanges["AGI"] = 0
            pc.JEXP += jexp_to_gain
            pc.MasteredJobs[pc.Job]["JOB_EXP"] += jexp_to_gain
            entity.check_for_mastery_level_up(pc)
        GAME_STATE.xp_count += xp_to_gain
        GAME_STATE.money += money_to_gain
        
    if won_battle == False:
        gamestate.print_with_conf("Khorynn's party wiped! You lose!")
    return won_battle


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
            GAME_STATE.turn_order.append(GelatinousServant)
            enemies_spawned.append(GelatinousServant)
            gel_king.Phases["Spawn Phase 1"] = True

    # At 60% health, spawn another servant
    if gel_king.HP < int(gel_king.MaxHP * 0.6):
        if gel_king.Phases["Spawn Phase 2"] == False:
            GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])
            gamestate.print_with_conf("The Gelatinous King ejects another Servant from its wounded flesh!")
            GAME_STATE.enemy_party.append(GelatinousServant)
            GAME_STATE.turn_order.append(GelatinousServant)
            enemies_spawned.append(GelatinousServant)
            gel_king.Phases["Spawn Phase 2"] 

    # At 40% health, spawn 2 servants
    if gel_king.HP < int(gel_king.MaxHP * 0.4):
        if gel_king.Phases["Spawn Phase 3"] == False:
            gamestate.print_with_conf("The Gelatinous King is falling apart! Two servants are ripped from the main body!")
            for _ in range(2):
                GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])                
                GAME_STATE.enemy_party.append(GelatinousServant)
                GAME_STATE.turn_order.append(GelatinousServant)
                enemies_spawned.append(GelatinousServant)
            gel_king.Phases["Spawn Phase 3"] = True

    # At 20% helath, spawn 3 servants
    if gel_king.HP < int(gel_king.MaxHP * 0.2):
        if gel_king.Phases["Spawn Phase 4"] == False:
            gamestate.print_with_conf("The Gelatinous King is almost dead!\nThree Gelatinous Servants stream like a river from its flesh!")
            for _ in range(3):
                GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])
                GAME_STATE.enemy_party.append(GelatinousServant)
                GAME_STATE.turn_order.append(GelatinousServant)
                enemies_spawned.append(GelatinousServant)   
            gel_king.Phases["Spawn Phase 4"] = True    

def king_slime_death_logic(entity_dead, entity_attaker, cause_of_death):
    if entity_dead.Name == "Gelatinous King" and entity_dead.EntityType == "BossEnemy":
        gamestate.print_with_conf("The Gelatinous King's body ruptures, its body fracturing into five Servants!")
        for _ in range(5):
            GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])
            GAME_STATE.enemy_party.append(GelatinousServant)
            GAME_STATE.turn_order.append(GelatinousServant)
            enemies_spawned.append(GelatinousServant) 
        gamestate.remove_callback("callback_enemy_is_hit", "king_slime_spawn_phase_handler")
        gamestate.remove_callback("callback_enemy_is_dead", "king_slime_death_logic")
    else:
        return


def king_slime(gel_king, enemies_spawned):
    bloodthirsty = None

    if "king_slime_spawn_phase_handler" not in gamestate.get_callback_triggers_map()["callback_enemy_is_hit"]:
        gamestate.add_callback("callback_enemy_is_hit", king_slime_spawn_phase_handler)
    if "king_slime_death_logic" not in gamestate.get_callback_triggers_map()["callback_enemy_is_dead"]:
        gamestate.add_callback("callback_enemy_is_dead", king_slime_death_logic)

    for player_character in GAME_STATE.player_party:
        if damage_calc(gel_king, player_character, False, False) > player_character.HP:
            GAME_STATE.battle_entity_targeted = player_character
            break
    GAME_STATE.battle_entity_targeted = random.choice(GAME_STATE.player_party) if GAME_STATE.battle_entity_targeted == None else GAME_STATE.battle_entity_targeted
    enemy_damage = damage_calc(gel_king, GAME_STATE.battle_entity_targeted, False)
    gamestate.print_with_conf(f"The King jumps to {GAME_STATE.battle_entity_targeted.Name} and smothers them with its ginormous body, dealing {enemy_damage} damage!")
    bloodthirsty = gamestate.deal_damage_to_target(gel_king, GAME_STATE.battle_entity_targeted, False)
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

def stone_golem(golem, enemies_spawned):
    if "stone_golem_phase_handler" not in gamestate.get_callback_triggers_map()["callback_enemy_is_hit"]:
        gamestate.add_callback("callback_enemy_is_hit", stone_golem_phase_handler)
    if "stone_golem_death_logic" not in gamestate.get_callback_triggers_map()["callback_enemy_is_dead"]:
        gamestate.add_callback("callback_enemy_is_dead", stone_golem_death_logic)


    cant_see_kill = True
    for player_character in GAME_STATE.player_party:
        if damage_calc(gel_king, player_character, False, False) > player_character.HP:
            GAME_STATE.battle_entity_targeted = player_character
            cant_see_kill = False
            break
    if cant_see_kill:
        GAME_STATE.battle_entity_targeted = random.choice(GAME_STATE.player_party)


    def golem_normal_attack(phase):
        nonlocal golem
        nonlocal enemies_spawned
        nonlocal enemy_damage

        gamestate.run_callbacks("callback_entity_is_targeted", attacker_action="attack")
        gamestate.run_callbacks("callback_pc_is_targeted", attacker_action="attack")
        
        if phase == 1:
            gamestate.print_with_conf(f"The Golem slams its boulder fists down on {GAME_STATE.battle_entity_targeted.Name} and deals {enemy_damage}!")
        else:
            gamestate.print_with_conf(f"The Golem rushes towards {GAME_STATE.battle_entity_targeted.Name} with undiluted rage!\nIt runs them over and deals {enemy_damage} damage!!")

        
        GAME_STATE.battle_entity_targeted.HP -= enemy_damage
        bloodthirsty = gamestate.deal_damage_to_target(golem, GAME_STATE.battle_entity_targeted, enemy_damage)

    
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
                GAME_STATE.battle_entity_targeted = GAME_STATE.player_party
                for pc in GAME_STATE.battle_entity_targeted:
                    gamestate.run_callbacks("callback_entity_is_targeted", attacker_action="attack")
                    gamestate.run_callbacks("callback_pc_is_targeted", attacker_action="attack")                    
                    enemy_damage = int(damage_calc(golem, pc, False) * 0.6)
                    gamestate.print_with_conf(f"{pc.Name} takes {enemy_damage} damage!")
                    bloodthirsty = gamestate.deal_damage_to_target(golem, pc, enemy_damage)

        
    return bloodthirsty



#####################################
# \/\/\/ Ability Functions \/\/\/
#####################################

def skull_crusher(user, cast_for_free: bool = False):
    bloodthirsty = None
    
    if user.MP < 3 and not cast_for_free:
        gamestate.print_with_conf(f"{user.Name} didn't have enough MP to use Skull Crusher!")
        return False
        
    target = GAME_STATE.enemy_party[find_target()]
    gamestate.run_callbacks("callback_entity_is_targeted", entity_targeted=target, entity_attacking=user, attacker_action="physical_attack")
    gamestate.run_callbacks("callback_enemy_is_targeted", entity_targeted=target, entity_attacking=user, attacker_action="physical_attack")
    
    gamestate.print_with_conf(f"{user.Name} uses Skull Crusher!")
    if not cast_for_free:
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
    gamestate.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=target, spell_casted=skull_crusher)
    return bloodthirsty


def forfireball(user):
    if user.MP < 40:
        gamestate.print_with_conf(f"{user.Name} tried to use Fireball, but its immense mana cost proved too much for them!")
        return False
    
    defender = GAME_STATE.enemy_party[find_target()]
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


def focus(user):
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
        gamestate.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=user, spell_casted=focus)
        gamestate.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=user, stat_changed="MND", change_stages=1)


def slap(user):
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
    gamestate.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=user, spell_casted=slap)
    gamestate.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=user, stat_changed="MND", change_stages=1)    
    return None

def spark(user):
    if user.MP < 4:
        gamestate.print_with_conf(f"{user.Name} didn't have enough MP to use Spark!")
        return False
    defender = GAME_STATE.enemy_party[find_target()]
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
    gamestate.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=defender, spell_casted=spark)
    return None
    
def heal(user):
    if user.MP < 6:
        gamestate.print_with_conf(f"{user.Name} didn't have enough MP to use Heal!")
        return False

    
    print("Party:")
    for _ in range(len(GAME_STATE.player_party)):
        print(f"Party Member {_ + 1}: {GAME_STATE.player_party[_].Name}\nHP: {GAME_STATE.player_party[_].HP}/{GAME_STATE.player_party[_].MaxHP}\n")
    pc_to_heal = input("\n(INPUT NUM) Which numbered party member would you like to heal?    ").lower().strip()

    
    while not isinstance(pc_to_heal, int):
        try:
            pc_to_heal = int(pc_to_heal)
        except ValueError:
            print("Please input a number correlated to the target.")
            gamestate.print_with_conf("Don't input anything other than a number!", True)
            pc_to_heal = input("(INPUT NUM) Which numbered party member would you like to heal?    ")

    
    gamestate.print_with_conf(f"{user.Name} focuses on calming things...")
    gamestate.print_with_conf("They siphon 6 MP!")
    gamestate.print_with_conf(f"{user.Name} casts Heal!")
    HP_to_heal = int(user.MaxHP * 0.2) + user.get_mind()
    HP_to_heal = pc_to_heal.MaxHP - pc_to_heal.HP if pc_to_heal.HP + HP_to_heal > pc_to_heal.MaxHP else HP_to_heal
    gamestate.print_with_conf(f"They heal {pc_to_heal.Name} for {HP_to_heal} HP!")
    pc_to_heal.HP += HP_to_heal
    gamestate.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=pc_to_heal, spell_casted=heal)
    return None



def resilience_prayer(user):
    if user.MP < 20:
        gamestate.print_with_conf(f"{user.Name} didn't have enough MP to use Resilience Prayer!")
        return False
    gamestate.print_with_conf(f"{user.Name} kneels down and prays for everyone to be safe...")
    for pc in GAME_STATE.player_party:
        pc.change_stat("RES", 1)
    gamestate.print_with_conf("Everyone feels a little tougher! Party's resilience increases one stage!")
    gamestate.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=GAME_STATE.player_party, spell_casted=resilience_prayer)
    for pc in GAME_STATE.player_party:
        gamestate.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=pc, stat_changed="RES", change_stages=1)    
    return None



def steal(user):
    # Find target
    target = pc_find_target()
    gamestate.print_with_conf(f"{user.Name} tries to steal from the enemy {target.Name}!")

    # Steal success chance procedure:
    # Get a random number between 0 and half of the user's AGI stat
    # Find the difference between the user's AGI stat and the target's AGI stat
    # If that random number is lower than the difference, you succeed and steal up to the entire money reward of the target!
    random_chance = random.randrange(0, int(user.get_agi() * 0.2)) 
    input(f"Steal threshold: {random_chance}")
    if user.get_agi() - target.get_agi() < random_chance:
        input(f"{user.get_agi()} - {target.get_agi()} ({user.get_agi() - target.get_agi()}) is lesser than threshold of {random_chance}: steal fails")
        gamestate.print_with_conf(f"The enemy sees it coming and {user.Name} fails the steal!")
    else:
        input(f"{user.get_agi()} - {target.get_agi()} ({user.get_agi() - target.get_agi()}) is greater than threshold of {random_chance}: steal succeeds")
        money_min = int(target.Money_Reward * 0.3) if int(target.Money_Reward * 0.3) > 0 else 1
        money_stolen = random.randrange(money_min, target.Money_Reward + 1)
        gamestate.print_with_conf(f"{user.Name} slips into the enemy's blindspot and steals {money_stolen} gold!")
        GAME_STATE.money += money_stolen
        target.Money_Reward -= int(target.Money_Reward * 0.3)
    return



def talk(user):
    target_found = False
    
    while not target_found:
        target = GAME_STATE.enemy_party[find_target()]
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
