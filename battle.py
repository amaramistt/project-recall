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
    
    print_with_conf("The party encounters a group of enemies!")

    # Spawn 
    if enemy_pool != -9999:
        for enemy in possible_encounters[chosen_encounter]:
            enemy_to_spawn = copy.deepcopy(enemy)
            enemies_spawned.append(enemy_to_spawn)
        print_with_conf(enemy_pools[enemy_pool]["encounter_dialogue"][chosen_encounter])
        GAME_STATE.enemy_party = enemies_spawned
        return run_encounter()
    else:
        print_with_conf("You didn't, actually, because THE DEV FORGOT TO SET THE ENEMY POOL LIKE A DUMBASS!")
        return False


def find_target(amount_of_enemies):
    target = input("Which numbered enemy would you like to target?")
    while not isinstance(target, int):
        try:
            target = int(target)
        except ValueError:
            print("Please print_with_conf a number correlated to the enemy.")
            print_with_conf("Don't print_with_conf anything other than a number!")
            target = input("Which numbered enemy would you like to target?")
    target -= 1
    if target < 0:
        target = 0
    elif target > amount_of_enemies:
        target = amount_of_enemies - 1
    return target

def find_turn_order(pc_party: list[Entity], enemies_in_battle: list[Entity]):
    entity_list = []
    for actors in pc_party:
        entity_list.append(actors)
    for actors in enemies_in_battle:
        entity_list.append(actors)
    return sorted(entity_list, key=lambda x: x.AGI, reverse=True)

def run_encounter():
    
    initiative_list = find_turn_order()
    os.system(CLEAR)
    party_wiped = False
    enemies_are_dead = False
    enemies_spawned = []
    for enemy in enemies:
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
                    print_with_conf(f"{bloodthirsty_check.Name} is bloodthirsty!")
                    pc_turn_handler(bloodthirsty_check, initiative_list, True)
                    print_with_conf(f"{bloodthirsty_check.Name}'s primal rage dims!")
                    os.system(CLEAR)
                elif bloodthirsty_check.EntityType == "Enemy":
                    print_with_conf(f"{bloodthirsty_check.Name} is bloodthirsty!")
                    enemy_AI(bloodthirsty_check, initiative_list)
                    print_with_conf(f"{bloodthirsty_check.Name}'s primal rage dims!")
                    os.system(CLEAR)
                elif bloodthirsty_check.EntityType == "BossEnemy":
                    print_with_conf(f"{bloodthirsty_check.Name} is bloodthirsty!!")
                    logic_to_reference = globals()[bloodthirsty_check.BossLogic]
                    logic_to_reference(bloodthirsty_check, initiative_list, enemies_spawned)
                    print_with_conf(f"{bloodthirsty_check.Name}'s primal rage dims!")
                    os.system(CLEAR)
                bloodthirsty_check = None
    
            # Check if the battle's over BEFORE normal turn/AFTER bloodthirsty
            if check_if_battle_won() is not None:
                if not check_if_battle_won():
                    party_wiped = True
                    break
                elif check_if_battle_won():
                    enemies_are_dead = True
                    break
                
            # Start of entity's turn
            print_with_conf(f"It's {actor.Name}'s turn!")
            
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
                    target = enemy[find_target(len(enemy))]
                except IndexError:
                    print_with_conf(f"That target doesn't exist! There are only {len(enemy)} enemies on the field!")
                    target = None
            main.run_callbacks("callback_entity_is_targeted", entity_targeted=target, entity_attacking=character, attacker_action="physical_attack")
            main.run_callbacks("callback_enemy_is_targeted", entity_targeted=target, entity_attacking=character, attacker_action="physical_attack")
            
            # deal damage to it
            damage = damage_calc(character, target, False)
            print_with_conf(f"You attack {target.Name} with your weapon, dealing {damage} damage!")
            target.HP -= damage
            main.run_callbacks("callback_entity_is_hit", entity_hit=target, entity_attacker=character, player_party=player_party, enemy_party=enemy)
            main.run_callbacks("callback_enemy_is_hit", entity_hit=target, entity_attacker=character, player_party=player_party, enemy_party=enemy)
            
            if target.HP <= 0:
                print_with_conf(f"{target.Name} has fallen!")
                main.run_callbacks("callback_entity_is_dead", entity_dead=target, entity_attacker=character)
                main.run_callbacks("callback_enemy_is_dead", entity_dead=target, entity_attacker=character)
                turn_order.remove(target)
                enemy.remove(target)
                bloodthirsty = character
                
            turn_is_over = True
        
        elif cmd == "ability":
            bloodthirsty = ability_handler(character, turn_order)
            turn_is_over = True
            
        elif cmd == "pass":
            if is_bloodthirsty:
                print_with_conf(f"{character.Name} is enraged! They must attack!")
                turn_is_over = False
            else:
                print_with_conf(f"{character.Name} waited to act!")
                turn_is_over = True
            
        else:
            print_with_conf("Invalid command!")

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
                print_with_conf(f"{character.Abilities[chosen_ability]}")
                use_ability = globals()[character.Abilities[chosen_ability]["callback"]]
            except KeyError:
                chosen_ability = input("That ability isn't in your learned abilities! Did you change your mind? print_with_conf 'back' to go back.")
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
        print_with_conf("you don't have an ability dummy")
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
    enemy_target = character[random.randrange(0, len(character))]
    
    # check if its mind is higher than its strength and use the higher stat in the damage calc
    if enemy.get_strength() > enemy.get_mind():
        main.run_callbacks("callback_entity_is_targeted", entity_targeted=enemy_target, entity_attacking=enemy, attacker_action="physical_attack")
        main.run_callbacks("callback_pc_is_targeted", entity_targeted=enemy_target, entity_attacking=enemy, attacker_action="physical_attack")
        enemy_damage = damage_calc(enemy, enemy_target, False)
        print_with_conf(f"The enemy attacks with their weapon and deals {enemy_damage} damage to {enemy_target.Name}!")
    else:
        main.run_callbacks("callback_entity_is_targeted", entity_targeted=enemy_target, entity_attacking=enemy, attacker_action="magic_attack")
        main.run_callbacks("callback_pc_is_targeted", entity_targeted=enemy_target, entity_attacking=enemy, attacker_action="magic_attack")
        enemy_damage = damage_calc(enemy, enemy_target, True)
        print_with_conf(f"The enemy casts a spell and deals {enemy_damage} damage to {enemy_target.Name}!")
        
    # deal damage
    enemy_target.HP -= enemy_damage
    if enemy_target.HP < 0:
        enemy_target.HP = 0
    main.run_callbacks("callback_entity_is_hit", entity_hit=enemy_target, entity_attacker=enemy, player_party=character, enemy_party=enemy_party)
    main.run_callbacks("callback_pc_is_hit", entity_hit=enemy_target, entity_attacker=enemy, player_party=character, enemy_party=enemy_party)
    print_with_conf(f"{enemy_target.Name} is at {enemy_target.HP}/{enemy_target.MaxHP} HP!")
    
    # check if the character died
    if enemy_target.HP <= 0:
        print_with_conf(f"{enemy_target.Name} Has Fallen!")
        main.run_callbacks("callback_entity_is_dead", entity_dead=enemy_target, entity_attacker=enemy)
        main.run_callbacks("callback_pc_is_dead", entity_dead=enemy_target, entity_attacker=enemy)
        bloodthirsty = enemy
        turn_order.remove(enemy_target)
        character.remove(enemy_target)
    return bloodthirsty


def damage_calc(attacker, defender, magic: bool = False, crit_enabled: bool = True):
    
    if crit_enabled:
        critical = 2 if random.uniform(0, 1) >= 0.95 else 1
    else:
        critical = 1
    level_differential = 1 + (attacker.Level / 40) - (defender.Level / 40)

    if critical > 1:
        print("It's a critical hit!")

    if not magic:
        print_with_conf("damage type = physical")
        damage = attacker.get_strength() * level_differential
        print_with_conf(f"attacker strength = {attacker.get_strength()} times level differential of {level_differential} = {damage}")
        damage = defender.get_res() * 0.6 / level_differential
        print_with_conf(f"defender res = {defender.get_res()} times 0.7 equals {defender.get_res() * 0.6} divided by level diff of {level_differential} = {damage}")
        damage = ((attacker.get_strength() * level_differential) - ((defender.get_res() * 0.6) / level_differential))
        damage = damage * critical
        print_with_conf(f"effective strength minus effective resilience times critical = {damage}")
        damage = int(damage * random.uniform(0.9, 1.1))
        print_with_conf(f"after variation of +-10% = {damage}")
        if damage >= 0:
            return damage
        else:
            return 0

    elif magic:
        print_with_conf("damage type = magic")
        damage = attacker.get_mind() * level_differential
        print_with_conf(f"attacker mind = {attacker.get_mind()} times level differential of {level_differential} = {damage}")
        print_with_conf(f"magic ignores enemy resilience")
        damage = damage * critical
        print_with_conf(f"effective mind times critical = {damage}")
        damage = int(damage * random.uniform(0.9, 1.1))
        print_with_conf(f"after integerification and variation of +-10% = {damage}")
        if damage >= 0:
            return damage
        else:
            return 0
    else:
        print("You forgot to set magic, dumbass.")
        return 0
    

def battle_cleanup(enemies, won_battle = True):
    os.system(CLEAR)
    if won_battle == True:
        print("B A T T L E  W O N !")
        if len(enemies) > 1:
            for actors in enemies:
                print(f"You defeated {actors.Name}!")
            print_with_conf("")
        else:
            print_with_conf(f"You defeated {enemies[0].Name}!")
        for pc in friendlies:
            pc.StatChanges["STR"] = 0
            pc.StatChanges["RES"] = 0
            pc.StatChanges["MND"] = 0
            pc.StatChanges["AGI"] = 0
    if won_battle == False:
        print_with_conf("Khorynn's party wiped! You lose!")
        main.open_file("assets/sprites/peter_griffin_fortnite.jpeg")
    return won_battle

def king_slime(player_party, gel_king, enemies, initiative_list, enemies_spawned):
    bloodthirsty = None

    if "king_slime_spawn_phase_handler" not in main.get_callback_triggers_map()["callback_enemy_is_hit"]:
        main.add_callback("callback_enemy_is_hit", "king_slime_spawn_phase_handler")
    if "king_slime_death_logic" not in main.get_callback_triggers_map()["callback_enemy_is_dead"]:
        main.add_callback("callback_enemy_is_dead", "king_slime_death_logic")

    enemy_target = None
    for player_character in player_party:
        if damage_calc(gel_king, player_character, False, False) > player_character.HP:
            enemy_target = player_character
            break
    enemy_target = random.choice(player_party) if enemy_target == None else enemy_target
    enemy_damage = damage_calc(gel_king, enemy_target, False)
    print_with_conf(f"The King jumps to {enemy_target.Name} and smothers them with its ginormous body, dealing {enemy_damage} damage!")
    enemy_target.HP -= enemy_damage
    # make sure the character doesn't have negative health
    if enemy_target.HP < 0:
        enemy_target.HP = 0
    # let the player know what health they're at
    print_with_conf(f"{enemy_target.Name} is at {enemy_target.HP}/{enemy_target.MaxHP} HP!")
    # check if the character died
    if enemy_target.HP <= 0:
        print_with_conf(f"{enemy_target.Name} Has Fallen!")
        bloodthirsty = gel_king
        initiative_list.remove(enemy_target)
        player_party.remove(enemy_target)
    return bloodthirsty 


def king_slime_spawn_phase_handler(entity_hit, entity_attacker, player_party, enemy_party):
    # Make sure we're working with the boss
    if entity_hit.Name == "Gelatinous King" and entity_hit.EntityType == "BossEnemy":
        gel_king = entity_hit
    else:
        return

    # At 80% health, spawn 1 servant
    if gel_king.HP < int(gel_king.MaxHP * 0.8):
        if gel_king.Phases["Spawn Phase 1"] == False:
            GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])
            print_with_conf("The Gelatinous King's gel wobbles...\nA Gelatinous Servent erupts from the King and joins the fight!")
            enemies.append(GelatinousServant)
            initiative_list.append(GelatinousServant)
            enemies_spawned.append(GelatinousServant)
            gel_king.Phases["Spawn Phase 1"] = True

    # At 60% health, spawn another servant
    if gel_king.HP < int(gel_king.MaxHP * 0.6):
        if gel_king.Phases["Spawn Phase 2"] == False:
            GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])
            print_with_conf("The Gelatinous King ejects another Servant from its wounded flesh!")
            enemies.append(GelatinousServant)
            initiative_list.append(GelatinousServant)
            enemies_spawned.append(GelatinousServant)
            gel_king.Phases["Spawn Phase 2"] 

    # At 40% health, spawn 2 servants
    if gel_king.HP < int(gel_king.MaxHP * 0.4):
        if gel_king.Phases["Spawn Phase 3"] == False:
            print_with_conf("The Gelatinous King is falling apart! Two servants are ripped from the main body!")
            for _ in range(2):
                GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])                
                enemies.append(GelatinousServant)
                initiative_list.append(GelatinousServant)
                enemies_spawned.append(GelatinousServant)
            gel_king.Phases["Spawn Phase 3"] = True

    # At 20% helath, spawn 3 servants
    if gel_king.HP < int(gel_king.MaxHP * 0.2):
        if gel_king.Phases["Spawn Phase 4"] == False:
            print_with_conf("The Gelatinous King is almost dead!\nThree Gelatinous Servants stream like a river from its flesh!")
            for _ in range(3):
                GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])
                enemies.append(GelatinousServant)
                initiative_list.append(GelatinousServant)
                enemies_spawned.append(GelatinousServant)   
            gel_king.Phases["Spawn Phase 4"] = True    

def king_slime_death_logic(entity_dead, entity_attaker, cause_of_death):
    if entity_dead.Name == "Gelatinous King" and entity_dead.EntityType == "BossEnemy":
        print_with_conf("The Gelatinous King's body ruptures, its body fracturing into five Servants!")
        for _ in range(5):
            GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])
            enemies.append(GelatinousServant)
            initiative_list.append(GelatinousServant)
            enemies_spawned.append(GelatinousServant) 
        main.remove_callback("callback_enemy_is_hit", "king_slime_spawn_phase_handler")
        main.remove_callback("callback_enemy_is_dead", "king_slime_death_logic")
    else:
        return


def stone_golem(player_party, golem, enemies, initiative_list, enemies_spawned):
    if "stone_golem_phase_handler" not in main.get_callback_triggers_map()["callback_enemy_is_hit"]:
        main.add_callback("callback_enemy_is_hit", "stone_golem_phase_handler")
    if "stone_golem_death_logic" not in main.get_callback_triggers_map()["callback_enemy_is_dead"]:
        main.add_callback("callback_enemy_is_dead", "stone_golem_phase_handler")


    cant_see_kill = True
    for player_character in player_party:
        if damage_calc(gel_king, player_character, False, False) > player_character.HP:
            enemy_target = player_character
            cant_see_kill = False
            break
    if cant_see_kill:
        enemy_target = random.choice(player_party)
        
    enemy_damage = damage_calc(golem, enemy_target, False)

    def golem_normal_attack(phase):
        nonlocal player_party
        nonlocal golem
        nonlocal enemies
        nonlocal initiative_list
        nonlocal enemies_spawned
        nonlocal enemy_target
        nonlocal enemy_damage

        main.run_callbacks("callback_entity_is_targeted")
        main.run_callbacks("callback_pc_is_targeted")
        
        if phase == 1:
            print_with_conf(f"The Golem slams its boulder fists down on {enemy_target.Name} and deals {enemy_damage}!")
        else:
            print_with_conf(f"The Golem rushes towards {enemy_target.Name} with undiluted rage!\nIt runs them over and deals {enemy_damage} damage!!")
            
        enemy_target.HP -= enemy_damage
        if enemy_target.HP < 0:
            enemy_target.HP = 0
            
        main.run_callbacks("callback_entity_is_hit", entity_hit=enemy_target, 
                           entity_attacker=golem, 
                           player_party=player_party, 
                           enemy_party=enemies)
        main.run_callbacks("callback_pc_is_hit", entity_hit=enemy_target, 
                           entity_attacker=golem, 
                           player_party=player_party, 
                           enemy_party=enemies)
        
        print_with_conf(f"{enemy_target.Name} is at {enemy_target.HP}/{enemy_target.MaxHP} HP!")
        # check if the character died
        if enemy_target.HP <= 0:
            print_with_conf(f"{enemy_target.Name} Has Fallen!")
            main.run_callbacks("callback_entity_is_dead", entity_dead=enemy_target, entity_attacker=golem)
            main.run_callbacks("callback_pc_is_dead", entity_dead=enemy_target, entity_attacker=golem)
            bloodthirsty = golem
            initiative_list.remove(enemy_target)
            player_party.remove(enemy_target)

    
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
                print_with_conf("The Golem swings in a wide arc that hits the enitre party!!!")
                enemy_target = player_party
                for pc in enemy_target:
                    enemy_damage = int(damage_calc(golem, pc, False) * 0.6)
                    print_with_conf(f"{pc.Name} takes {enemy_damage} damage!")
                    main.run_callbacks("callback_entity_is_hit", entity_hit=pc, 
                                   entity_attacker=golem, 
                                   player_party=player_party, 
                                   enemy_party=enemies)
                    main.run_callbacks("callback_pc_is_hit", entity_hit=pc, 
                                       entity_attacker=golem, 
                                       player_party=player_party, 
                                       enemy_party=enemies)
                    
                    print_with_conf(f"{pc.Name} is at {pc.HP}/{pc.MaxHP} HP!")
                    # check if the character died
                    if pc.HP <= 0:
                        print_with_conf(f"{pc.Name} Has Fallen!")
                        main.run_callbacks("callback_entity_is_dead", entity_dead=pc, entity_attacker=golem)
                        main.run_callbacks("callback_pc_is_dead", entity_dead=pc, entity_attacker=golem)
                        bloodthirsty = golem
                        initiative_list.remove(pc)
                        player_party.remove(pc)

        
    return bloodthirsty

def stone_golem_phase_handler(entity_hit, entity_attacker, player_party, enemy_party):
    if entity_hit.Name == "Stone Golem" and entity_hit.EntityType == "BossEnemy":
        golem = entity_hit
    else:
        return

    if golem.HP <= int(golem.MaxHP / 2):
        if not golem.Phases["Phase 2"]:
            print("The Stone Golem is starting to crack! A high-pitch shriek reverberates around you as it arches back in rage!")
            print_with_conf("The Stone Golem's attack increases drastically! It becomes considerably more aggressive!")
            golem.change_stat("STR", 4)
            main.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=golem, stat_changed="STR", change_stages=4)
            golem.Phases["Phase 2"] = True


def stone_golem_death_logic(entity_dead, entity_attaker, cause_of_death):
    if entity_dead.Name == "Stone Golem" and entity_dead.EntityType == "Boss Enemy":
        print_with_conf("The Stone Golem's body crumbles into rubble!")
        main.remove_callback("callback_enemy_is_hit", "stone_golem_phase_handler")
        main.remove_callback("callback_enemy_is_dead", "stone_golem_death_logic")
    else:
        return

#####################################
# \/\/\/ Ability Functions \/\/\/
#####################################

def skull_crusher(player_party, user, enemy, inititive_list):
    bloodthirsty = None
    
    if user.MP < 3:
        print_with_conf(f"{user.Name} didn't have enough MP to use Skull Crusher!")
        return False
        
    target = enemy[find_target(len(enemy))]
    main.run_callbacks("callback_entity_is_targeted", entity_targeted=target, entity_attacking=user, attacker_action="physical_attack")
    main.run_callbacks("callback_enemy_is_targeted", entity_targeted=target, entity_attacking=user, attacker_action="physical_attack")
    
    print_with_conf(f"{user.Name} uses Skull Crusher!")
    user.MP -= 3
    print_with_conf("They siphon 3 points of MP!")
    print_with_conf(f"{user.Name} slams their weapon onto {target.Name}'s head with a horrifying CRACK!")
    damage = int(damage_calc(user, target, False))
    print_with_conf(f"They deal {damage} damage!")
    target.HP -= damage
    main.run_callbacks("callback_entity_is_hit", entity_hit=target, entity_attacker=user, player_party=player_party, enemy_party=enemy)
    main.run_callbacks("callback_enemy_is_hit", entity_hit=target, entity_attacker=user, player_party=player_party, enemy_party=enemy)
    if target.HP <= 0:
        print_with_conf(f"{target.Name} has fallen!")
        main.run_callbacks("callback_entity_is_dead", entity_dead=target, entity_attacker=user)
        main.run_callbacks("callback_enemy_is_dead", entity_dead=target, entity_attacker=user)
        enemy.remove(target)
        inititive_list.remove(target)
        bloodthirsty = user
    else:
        print_with_conf(f"{target.Name}'s resilience was lowered one stage!")
        target.change_stat("RES", -1)
        main.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=target, stat_changed="RES", change_stages=-1)
    main.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=target, spell_casted="skull_crusher")
    return bloodthirsty


def forfireball(player_party, user, enemy, inititive_list):
    if user.MP < 40:
        print_with_conf(f"{user.Name} tried to use Fireball, but its immense mana cost proved too much for them!")
        return False
    
    defender = enemy[find_target(len(enemy))]
    main.run_callbacks("callback_entity_is_targeted", entity_targeted=defender, entity_attacking=user, attacker_action="magic_attack")
    main.run_callbacks("callback_enemy_is_targeted", entity_targeted=defender, entity_attacking=user, attacker_action="magic_attack")
    user.MP -= 40
    
    print_with_conf(f"{user.Name} casts Fireball!")
    defense_ignored = defender.get_res()
    defender.RES -= defense_ignored
    print_with_conf("Even the most powerful defenses shatter when the shockwave hits it!")
    damage = damage_calc(user, defender, True) * 2
    defender.RES += defense_ignored
    
    print_with_conf(f"{defender.Name} takes {damage} damage!")
    defender.HP -= damage
    main.run_callbacks("callback_entity_is_hit", entity_hit=defender, entity_attacker=user, player_party=player_party, enemy_party=enemy)
    main.run_callbacks("callback_enemy_is_hit", entity_hit=defender, entity_attacker=user, player_party=player_party, enemy_party=enemy)
    if defender.HP <= 0:
        print_with_conf(f"{defender.Name} has fallen!")
        main.run_callbacks("callback_entity_is_dead", entity_dead=defender, entity_attacker=user)
        main.run_callbacks("callback_enemy_is_dead", entity_dead=defender, entity_attacker=user)
        enemy.remove(defender)
        inititive_list.remove(defender)
        return user
    return None


def focus(player_party, user, enemy, turn_order):
    mind_multiple = (user.get_mind() * 0.05) + 1
    if mind_multiple > 5:
        mind_multiple = 5
        
    if user.MP < 5:
        print_with_conf(f"{user.Name} tried to use Focus, but they didn't have enough MP!")
        return False
    else:
        user.MP -= 5
        print_with_conf(f"{user.Name} used Focus!")
        print_with_conf("They take a deep breath and center their thoughts...")
        print_with_conf("They feel better already!")
        health_to_heal = int(user.MaxHP * 0.1 + (random.randrange(10, 15) * mind_multiple))
        if (health_to_heal + user.HP) > user.MaxHP:
            health_to_heal = user.MaxHP - user.HP
        print_with_conf(f"{user.Name} heals {health_to_heal} HP!")
        user.HP += health_to_heal
        print_with_conf("They gain a temporary boost to Mind!")
        user.change_stat("MND", 1)
        main.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=user, spell_casted="focus")
        main.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=user, stat_changed="MND", change_stages=1)


def slap(player_party, user, enemy, turn_order):
    print_with_conf(f"{user.Name} is panicking!")
    panic_thoughts = [
        f"{user.Name} thinks they left their refridgerator running!",
        f"{user.Name} suddenly forgets everything they were doing!",
        f"{user.Name} suddenly finds images of malformed monkeys very valuable!",
        f"{user.Name} realizes that their parents were right about their worthlessness!",
        f"{user.Name} remembers that one cringy thing they did when they were a kid!",
        f"{user.Name} shits the bed!"
    ]
    chosen_thought = random.choice(panic_thoughts)
    print_with_conf(f"{chosen_thought}")
    print_with_conf("They slap themselves to regain composure!")
    damage = damage_calc(user, user, False)
    print_with_conf(f"They suffer {damage} damage!")
    user.HP -= damage
    main.run_callbacks("callback_entity_is_hit", entity_hit=user, entity_attacker=user, player_party=player_party, enemy_party=enemy)
    main.run_callbacks("callback_pc_is_hit", entity_hit=user, entity_attacker=user, player_party=player_party, enemy_party=enemy)
    if user.HP <= 0:
        print_with_conf(f"{user.Name} killed themself!")
        main.run_callbacks("callback_entity_is_dead", entity_dead=user, entity_attacker=user)
        main.run_callbacks("callback_pc_is_dead", entity_dead=user, entity_attacker=user)
        turn_order.remove(user)
        player_party.remove(user)
        return None
    print_with_conf(f"{user.Name}'s mind settles!")
    user.change_stat("MND", 1)
    main.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=user, spell_casted="slap")
    main.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=user, stat_changed="MND", change_stages=1)    
    return None

def spark(player_party, user, enemy_party, turn_order):
    if user.MP < 4:
        print_with_conf(f"{user.Name} didn't have enough MP to use Spark!")
        return False
    defender = enemy_party[find_target(len(enemy_party))]
    main.run_callbacks("callback_entity_is_targeted", entity_targeted=defender, entity_attacking=user, attacker_action="magic_attack")
    main.run_callbacks("callback_enemy_is_targeted", entity_targeted=defender, entity_attacking=user, attacker_action="magic_attack")
    user.MP -= 4

    print_with_conf(f"{user.Name} casts Spark!")
    print_with_conf(f"A small flare shoots out from {user.Name}'s hand!")
    damage = damage_calc(user, defender, True)
    
    print_with_conf(f"{defender.Name} takes {damage} damage!")
    defender.HP -= damage
    main.run_callbacks("callback_entity_is_hit", entity_hit=defender, entity_attacker=user, player_party=player_party, enemy_party=enemy_party)
    main.run_callbacks("callback_enemy_is_hit", entity_hit=defender, entity_attacker=user, player_party=player_party, enemy_party=enemy_party)
    if defender.HP <= 0:
        print_with_conf(f"{defender.Name} has fallen!")
        main.run_callbacks("callback_entity_is_dead", entity_dead=defender, entity_attacker=user)
        main.run_callbacks("callback_enemy_is_dead", entity_dead=defender, entity_attacker=user)
        enemy_party.remove(defender)
        turn_order.remove(defender)
        return user
    main.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=defender, spell_casted="spark")
    return None
    
def heal(player_party, user, enemy, turn_order):
    if user.MP < 6:
        print_with_conf(f"{user.Name} didn't have enough MP to use Heal!")
        return False
    print("Party:")
    for pc in player_party:
        print(f"{pc.Name}")
    pc_to_heal = input("(print_with_conf PLAYER CHARACTER NAME) Which party member would you like to heal?").lower().strip()
    for character in player_party:
        if character.Name.lower() == pc_to_heal:
            pc_to_heal = character
            break
    print_with_conf(f"{user.Name} focuses on calming things...")
    print_with_conf("They siphon 6 MP!")
    print_with_conf(f"{user.Name} casts Heal!")
    HP_to_heal = int(user.MaxHP * 0.2) + int(user.get_mind() * 1.5)
    HP_to_heal = pc_to_heal.MaxHP - pc_to_heal.HP if pc_to_heal.HP + HP_to_heal > pc_to_heal.MaxHP else HP_to_heal
    print_with_conf(f"They heal {pc_to_heal.Name} for {HP_to_heal} HP!")
    pc_to_heal.HP += HP_to_heal
    main.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=pc_to_heal, spell_casted="heal")
    return None

def resilience_prayer(player_party, user, enemy, turn_order):
    if user.MP < 20:
        print_with_conf(f"{user.Name} didn't have enough MP to use Resilience Prayer!")
        return False
    print_with_conf(f"{user.Name} kneels down and prays for everyone to be safe...")
    for pc in player_party:
        pc.change_stat("RES", 1)
    print_with_conf("Everyone feels a little tougher! Party's resilience increases one stage!")
    main.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=player_party, spell_casted="resilience_prayer")
    for pc in player_party:
        main.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=pc, stat_changed="RES", change_stages=1)    
    return None

def talk(player_party, user, enemy, turn_order):
    target_found = False
    
    while not target_found:
        target = find_target(len(enemy))
        target_found = True
        if target.EntityType == "BossEnemy":
            print_with_conf("Something tells you that you can't calm that one down!")
            target_found = False
            
    print_with_conf(f"{user.Name} attempts to calm the {target.Name} down!")
    if target.MND == 0:
        print_with_conf(f"But it's no use! The {target.Name} can't understand them at all!")
        return None
    elif target.Level > int(target.MND / 10):
        print_with_conf(f"Most of your words fly over the enemy's head, but you might be convincing them...!")
        