import os
import entity
from entity import Entity
import random
import copy
import sys
import subprocess
import main 

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
            "You see wwo adventurers sitting at a campfire...\nThey rise and draw their weapons when they see you!\nAn Enraged Wizard and a Stalwart Warrior draw near!",
            "Three Volakumas draw near!",
            "Two slimes and a Volakuma draw near!"
        ]
    },
    
    2: { # Second encounter; balanced around level 10 party members
        "encounters": [
            [entities["EnragedWarrior"], entities["StalwartWizard"]]
        ],
        
        "encounter_dialogue": [
            "An Enraged Warrior and a Stalwart Wizard draw near!"
        ]
    },
    
    3: { # Third encounter; balanced around level 20 party members
        "encounters": [
            [entities["DisgracedMonk"], entities["SorcererSupreme"], entities["CraftyThief"]]
        ],
        
        "encounter_dialogue": [
            "A Disgraced Monk, Sorcerer Supreme, and Crafty Thief draw near!"
        ]
    },
    
    4: { # Fourth encounter; boss monster balanced around level 30 party members
        "encounters": [
            [entities["GelatinousKing"]],
            [entities["StoneGolem"]]
        ],
        
        "encounter_dialogue": [
            "An army of slimes appear all around you and coagulate before you!\nYou face down the boss of the floor; the Gelatinous King!",
            "A collection of boulders rise from the floor and take humanoid shape!\nYou face down the boss of the floor; the Stone Golem!"
        ]
    }
}


# \/\/ NEEDS REWORK \/\/
def initiate_battle(player_party, enemy_pool = -9999):
    #For now, I'm just going to have it call run_encounter similarly to how it would will in future
    global entities
    os.system(CLEAR)
    enemies_spawned = []

    # find appropriate encouters and choose one
    possible_encounters = enemy_pools[enemy_pool]["encounters"]
    chosen_encounter = random.randrange(0, len(possible_encounters))
    
    input("The party encounters a group of enemies!")

    # Spawn 
    if enemy_pool != -9999:
        for enemy in possible_encounters[chosen_encounter]:
            enemy_to_spawn = copy.deepcopy(enemy)
            enemies_spawned.append(enemy_to_spawn)
        input(enemy_pools[enemy_pool]["encounter_dialogue"][chosen_encounter])
        return run_encounter(player_party, enemies_spawned)
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

def find_turn_order(pc_party: list[Entity], enemies_in_battle: list[Entity]):
    entity_list = []
    for actors in pc_party:
        entity_list.append(actors)
    for actors in enemies_in_battle:
        entity_list.append(actors)
    return sorted(entity_list, key=lambda x: x.AGI, reverse=True)

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
                if bloodthirsty_check.EntityType == "PlayerCharacter" or bloodthirsty_check.EntityType == "Khorynn":
                    input(f"{bloodthirsty_check.Name} is bloodthirsty!")
                    pc_turn_handler(friendlies, bloodthirsty_check, enemies, initiative_list, True)
                    input(f"{bloodthirsty_check.Name}'s primal rage dims!")
                    os.system(CLEAR)
                elif bloodthirsty_check.EntityType == "Enemy":
                    input(f"{bloodthirsty_check.Name} is bloodthirsty!")
                    enemy_AI(friendlies, bloodthirsty_check, enemies, initiative_list)
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
            if actor.EntityType == "PlayerCharacter" or actor.EntityType == "Khorynn":
                # do PC shit
                bloodthirsty_check = pc_turn_handler(friendlies, actor, enemies, initiative_list, False)
    
            # check if entity is an enemy
            if actor.EntityType == "Enemy":
                # do enemy shit
                bloodthirsty_check = enemy_AI(friendlies, actor, enemies, initiative_list)

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
            main.run_callbacks("callback_entity_is_targeted", entity_targeted=target, entity_attacking=character, attacker_action="physical_attack")
            main.run_callbacks("callback_enemy_is_targeted", entity_targeted=target, entity_attacking=character, attacker_action="physical_attack")
            
            # deal damage to it
            damage = damage_calc(character, target, False)
            input(f"You attack {target.Name} with your weapon, dealing {damage} damage!")
            target.HP -= damage
            main.run_callbacks("callback_entity_is_hit", entity_hit=target, entity_attacker=character, player_party=player_party, enemy_party=enemy)
            main.run_callbacks("callback_enemy_is_hit", entity_hit=target, entity_attacker=character, player_party=player_party, enemy_party=enemy)
            
            if target.HP <= 0:
                input(f"{target.Name} has fallen!")
                main.run_callbacks("callback_entity_is_dead", entity_dead=target, entity_attacker=character)
                main.run_callbacks("callback_enemy_is_dead", entity_dead=target, entity_attacker=character)
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
                input(f"{character.Abilities[chosen_ability]}")
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
    KhorynnCount = 0
    
    if len(friendlies) == 0:
        return False
        
    for player_character in friendlies:
        if player_character.EntityType == "Khorynn":
            KhorynnCount += 1
    if KhorynnCount == 0:
        return False
        
    elif len(enemies) == 0:
        return True
        
    else:
        return None

def enemy_AI(character: list[Entity], enemy, enemy_party, turn_order):
    bloodthirsty = None
    
    # choose a random target 
    enemy_target = character[random.randrange(0, len(character))]
    
    # check if its mind is higher than its strength and use the higher stat in the damage calc
    if enemy.get_strength() > enemy.get_mind():
        main.run_callbacks("callback_entity_is_targeted", entity_targeted=enemy_target, entity_attacking=enemy, attacker_action="physical_attack")
        main.run_callbacks("callback_pc_is_targeted", entity_targeted=enemy_target, entity_attacking=enemy, attacker_action="physical_attack")
        enemy_damage = damage_calc(enemy, enemy_target, False)
        input(f"The enemy attacks with their weapon and deals {enemy_damage} damage to {enemy_target.Name}!")
    else:
        main.run_callbacks("callback_entity_is_targeted", entity_targeted=enemy_target, entity_attacking=enemy, attacker_action="magic_attack")
        main.run_callbacks("callback_pc_is_targeted", entity_targeted=enemy_target, entity_attacking=enemy, attacker_action="magic_attack")
        enemy_damage = damage_calc(enemy, enemy_target, True)
        input(f"The enemy casts a spell and deals {enemy_damage} damage to {enemy_target.Name}!")
        
    # deal damage
    enemy_target.HP -= enemy_damage
    if enemy_target.HP < 0:
        enemy_target.HP = 0
    main.run_callbacks("callback_entity_is_hit", entity_hit=enemy_target, entity_attacker=enemy, player_party=character, enemy_party=enemy_party)
    main.run_callbacks("callback_pc_is_hit", entity_hit=enemy_target, entity_attacker=enemy, player_party=character, enemy_party=enemy_party)
    input(f"{enemy_target.Name} is at {enemy_target.HP}/{enemy_target.MaxHP} HP!")
    
    # check if the character died
    if enemy_target.HP <= 0:
        input(f"{enemy_target.Name} Has Fallen!")
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
    input(f"The King jumps to {enemy_target.Name} and smothers them with its ginormous body, dealing {enemy_damage} damage!")
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
            input("The Gelatinous King's gel wobbles...\nA Gelatinous Servent erupts from the King and joins the fight!")
            enemies.append(GelatinousServant)
            initiative_list.append(GelatinousServant)
            enemies_spawned.append(GelatinousServant)
            gel_king.Phases["Spawn Phase 1"] = True

    # At 60% health, spawn another servant
    if gel_king.HP < int(gel_king.MaxHP * 0.6):
        if gel_king.Phases["Spawn Phase 2"] == False:
            GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])
            input("The Gelatinous King ejects another Servant from its wounded flesh!")
            enemies.append(GelatinousServant)
            initiative_list.append(GelatinousServant)
            enemies_spawned.append(GelatinousServant)
            gel_king.Phases["Spawn Phase 2"] 

    # At 40% health, spawn 2 servants
    if gel_king.HP < int(gel_king.MaxHP * 0.4):
        if gel_king.Phases["Spawn Phase 3"] == False:
            input("The Gelatinous King is falling apart! Two servants are ripped from the main body!")
            for _ in range(2):
                GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])                
                enemies.append(GelatinousServant)
                initiative_list.append(GelatinousServant)
                enemies_spawned.append(GelatinousServant)
            gel_king.Phases["Spawn Phase 3"] = True

    # At 20% helath, spawn 3 servants
    if gel_king.HP < int(gel_king.MaxHP * 0.2):
        if gel_king.Phases["Spawn Phase 4"] == False:
            input("The Gelatinous King is almost dead!\nThree Gelatinous Servants stream like a river from its flesh!")
            for _ in range(3):
                GelatinousServant = copy.deepcopy(entity.get_entities_map()["GelatinousServant"])
                enemies.append(GelatinousServant)
                initiative_list.append(GelatinousServant)
                enemies_spawned.append(GelatinousServant)   
            gel_king.Phases["Spawn Phase 4"] = True    

def king_slime_death_logic(entity_dead, entity_attaker, cause_of_death):
    if entity_dead.Name == "Gelatinous King" and entity_dead.EntityType == "BossEnemy":
        input("The Gelatinous King's body ruptures, its body fracturing into five Servants!")
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
            input(f"The Golem slams its boulder fists down on {enemy_target.Name} and deals {enemy_damage}!")
        else:
            input(f"The Golem rushes towards {enemy_target.Name} with undiluted rage!\nIt runs them over and deals {enemy_damage} damage!!")
            
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
        
        input(f"{enemy_target.Name} is at {enemy_target.HP}/{enemy_target.MaxHP} HP!")
        # check if the character died
        if enemy_target.HP <= 0:
            input(f"{enemy_target.Name} Has Fallen!")
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
                input("The Golem swings in a wide arc that hits the enitre party!!!")
                enemy_target = player_party
                for pc in enemy_target:
                    enemy_damage = int(damage_calc(golem, pc, False) * 0.6)
                    input(f"{pc.Name} takes {enemy_damage} damage!")
                    main.run_callbacks("callback_entity_is_hit", entity_hit=pc, 
                                   entity_attacker=golem, 
                                   player_party=player_party, 
                                   enemy_party=enemies)
                    main.run_callbacks("callback_pc_is_hit", entity_hit=pc, 
                                       entity_attacker=golem, 
                                       player_party=player_party, 
                                       enemy_party=enemies)
                    
                    input(f"{pc.Name} is at {pc.HP}/{pc.MaxHP} HP!")
                    # check if the character died
                    if pc.HP <= 0:
                        input(f"{pc.Name} Has Fallen!")
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
            input("The Stone Golem's attack increases drastically! It becomes considerably more aggressive!")
            golem.change_stat("STR", 4)
            main.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=golem, stat_changed="STR", change_stages=4)
            golem.Phases["Phase 2"] = True


def stone_golem_death_logic(entity_dead, entity_attaker, cause_of_death):
    if entity_dead.Name == "Stone Golem" and entity_dead.EntityType == "Boss Enemy":
        input("The Stone Golem's body crumbles into rubble!")
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
        input(f"{user.Name} didn't have enough MP to use Skull Crusher!")
        return False
        
    target = enemy[find_target(len(enemy))]
    main.run_callbacks("callback_entity_is_targeted", entity_targeted=target, entity_attacking=user, attacker_action="physical_attack")
    main.run_callbacks("callback_enemy_is_targeted", entity_targeted=target, entity_attacking=user, attacker_action="physical_attack")
    
    input(f"{user.Name} uses Skull Crusher!")
    user.MP -= 3
    input("They siphon 3 points of MP!")
    input(f"{user.Name} slams their weapon onto {target.Name}'s head with a horrifying CRACK!")
    damage = int(damage_calc(user, target, False))
    input(f"They deal {damage} damage!")
    target.HP -= damage
    main.run_callbacks("callback_entity_is_hit", entity_hit=target, entity_attacker=user, player_party=player_party, enemy_party=enemy)
    main.run_callbacks("callback_enemy_is_hit", entity_hit=target, entity_attacker=user, player_party=player_party, enemy_party=enemy)
    if target.HP <= 0:
        input(f"{target.Name} has fallen!")
        main.run_callbacks("callback_entity_is_dead", entity_dead=target, entity_attacker=user)
        main.run_callbacks("callback_enemy_is_dead", entity_dead=target, entity_attacker=user)
        enemy.remove(target)
        inititive_list.remove(target)
        bloodthirsty = user
    else:
        input(f"{target.Name}'s resilience was lowered one stage!")
        target.change_stat("RES", -1)
        main.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=target, stat_changed="RES", change_stages=-1)
    main.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=target, spell_casted="skull_crusher")
    return bloodthirsty


def forfireball(player_party, user, enemy, inititive_list):
    if user.MP < 40:
        input(f"{user.Name} tried to use Fireball, but its immense mana cost proved too much for them!")
        return False
    
    defender = enemy[find_target(len(enemy))]
    main.run_callbacks("callback_entity_is_targeted", entity_targeted=defender, entity_attacking=user, attacker_action="magic_attack")
    main.run_callbacks("callback_enemy_is_targeted", entity_targeted=defender, entity_attacking=user, attacker_action="magic_attack")
    user.MP -= 40
    
    input(f"{user.Name} casts Fireball!")
    defense_ignored = defender.get_res()
    defender.RES -= defense_ignored
    input("Even the most powerful defenses shatter when the shockwave hits it!")
    damage = damage_calc(user, defender, True) * 2
    defender.RES += defense_ignored
    
    input(f"{defender.Name} takes {damage} damage!")
    defender.HP -= damage
    main.run_callbacks("callback_entity_is_hit", entity_hit=defender, entity_attacker=user, player_party=player_party, enemy_party=enemy)
    main.run_callbacks("callback_enemy_is_hit", entity_hit=defender, entity_attacker=user, player_party=player_party, enemy_party=enemy)
    if defender.HP <= 0:
        input(f"{defender.Name} has fallen!")
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
        main.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=user, spell_casted="focus")
        main.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=user, stat_changed="MND", change_stages=1)


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
    main.run_callbacks("callback_entity_is_hit", entity_hit=user, entity_attacker=user, player_party=player_party, enemy_party=enemy)
    main.run_callbacks("callback_pc_is_hit", entity_hit=user, entity_attacker=user, player_party=player_party, enemy_party=enemy)
    if user.HP <= 0:
        input(f"{user.Name} killed themself!")
        main.run_callbacks("callback_entity_is_dead", entity_dead=user, entity_attacker=user)
        main.run_callbacks("callback_pc_is_dead", entity_dead=user, entity_attacker=user)
        turn_order.remove(user)
        player_party.remove(user)
        return None
    input(f"{user.Name}'s mind settles!")
    user.change_stat("MND", 1)
    main.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=user, spell_casted="slap")
    main.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=user, stat_changed="MND", change_stages=1)    
    return None

def spark(player_party, user, enemy_party, turn_order):
    if user.MP < 4:
        input(f"{user.Name} didn't have enough MP to use Spark!")
        return False
    defender = enemy_party[find_target(len(enemy_party))]
    main.run_callbacks("callback_entity_is_targeted", entity_targeted=defender, entity_attacking=user, attacker_action="magic_attack")
    main.run_callbacks("callback_enemy_is_targeted", entity_targeted=defneder, entity_attacking=user, attacker_action="magic_attack")
    user.MP -= 4

    input(f"{user.Name} casts Spark!")
    input(f"A small flare shoots out from {user.Name}'s hand!")
    damage = damage_calc(user, defender, True)
    
    input(f"{defender.Name} takes {damage} damage!")
    defender.HP -= damage
    main.run_callbacks("callback_entity_is_hit", entity_hit=defender, entity_attacker=user, player_party=player_party, enemy_party=enemy)
    main.run_callbacks("callback_enemy_is_hit", entity_hit=defender, entity_attacker=user, player_party=player_party, enemy_party=enemy)
    if defender.HP <= 0:
        input(f"{defender.Name} has fallen!")
        main.run_callbacks("callback_entity_is_dead", entity_dead=defender, entity_attacker=user)
        main.run_callbacks("callback_enemy_is_dead", entity_dead=defender, entity_attacker=user)
        enemy.remove(defender)
        inititive_list.remove(defender)
        return user
    main.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=defender, spell_casted="spark")
    return None
    
def heal(player_party, user, enemy, turn_order):
    if user.MP < 6:
        input(f"{user.Name} didn't have enough MP to use Heal!")
        return False
    print("Party:")
    for pc in player_party:
        print(f"{pc.Name}")
    pc_to_heal = input("(INPUT PLAYER CHARACTER NAME) Which party member would you like to heal?").lower().strip()
    for character in player_party:
        if character.Name.lower() == pc_to_heal:
            pc_to_heal = character
            break
    input(f"{user.Name} focuses on calming things...")
    input("They siphon 6 MP!")
    input(f"{user.Name} casts Heal!")
    HP_to_heal = int(user.MaxHP * 0.2) + int(user.get_mind() * 1.5)
    HP_to_heal = pc_to_heal.MaxHP - pc_to_heal.HP if pc_to_heal.HP + HP_to_heal > pc_to_heal.MaxHP else HP_to_heal
    input(f"They heal {pc_to_heal.Name} for {HP_to_heal} HP!")
    pc_to_heal.HP += HP_to_heal
    main.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=pc_to_heal, spell_casted="heal")
    return None

def resilience_prayer(player_party, user, enemy, turn_order):
    if user.MP < 20:
        input(f"{user.Name} didn't have enough MP to use Resilience Prayer!")
        return False
    input(f"{user.Name} kneels down and prays for everyone to be safe...")
    for pc in player_party:
        pc.change_stat("RES", 1)
    input("Everyone feels a little tougher! Party's resilience increases one stage!")
    main.run_callbacks("callback_spell_is_casted", entity_casting=user, enitity_targeted=player_party, spell_casted="resilience_prayer")
    for pc in player_party:
        main.run_callbacks("callback_stat_is_changed", entity_buffing_debuffing=pc, stat_changed="RES", change_stages=1)    
    return None

def bodyguard(player_party, user, enemy, turn_order):
    print("Party:")
    for pc in player_party:
        print(f"{pc.Name}")
    pc_to_heal = input("(INPUT PLAYER CHARACTER NAME) Which party member would you like to heal?").lower().strip()
    for character in player_party:
        if character.Name.lower() == pc_to_heal:
            pc_to_heal = character
            break