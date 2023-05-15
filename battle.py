import os
import entity
import random
import copy
import sys
import subprocess
import main 

entities = entity.get_entity_map()

enemy_pools = {
    1: { # First encounter; balanced around level 1 party members
        "encounters": [
            [entities["EnemyWizard"], entities["EnemyWarrior"]],
            [entities["Volakuma"], entities["Volakuma"], entites["Volakuma"]],
            [entities["Slime"], entities["Slime"], entities["Volakuma"]]
        ],
        
        "encounter_dialogue": [
            "An Enraged Wizard and a Stalwart Warrior draw near!",
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
            [entities["GelatinousKing"]]
        ],
        
        "encounter_dialogue": [
            "You face down the boss of the floor; the Gelatinous King!"
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
        for enemy in chosen_encounter:
            enemy_to_spawn = possible_encounters[chosen_encounter].deepcopy()
            enemies_spawned.append(enemy_to_spawn)
        print(enemy_pools[enemy_pool]["encounter_dialogue"][chosen_encounter])
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
            main.run_callbacks("callback_entity_is_hit")
            main.run_callbacks("callback_enemy_is_hit")
            if entity_is_dead(target):
                input(f"{target.Name} has fallen!")
                main.run_callbacks("callback_entity_is_dead")
                main.run_callbacks("callback_enemy_is_dead")
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
    
    # choose a random target 
    enemy_target = character[random.randrange(0, len(character))]
    
    # check if its mind is higher than its strength and use the higher stat in the damage calc
    if enemy.get_strength() > enemy.get_mind():
        enemy_damage = damage_calc(enemy, character[enemy_target], False)
        input(f"The enemy attacks with their weapon and deals {enemy_damage} damage to {character[enemy_target].Name}!")
    else:
        enemy_damage = damage_calc(enemy, character[enemy_target], True)
        input(f"The enemy casts a spell and deals {enemy_damage} damage to {character[enemy_target].Name}!")
        
    # deal damage
    character[enemy_target].HP -= enemy_damage
    if character[enemy_target].HP < 0:
        character[enemy_target].HP = 0
    main.run_callbacks("callback_entity_is_hit")
    main.run_callbacks("callback_pc_is_hit")
    input(f"{character[enemy_target].Name} is at {character[enemy_target].HP}/{character[enemy_target].MaxHP} HP!")
    
    # check if the character died
    if character[enemy_target].HP <= 0:
        input(f"{character[enemy_target].Name} Has Fallen!")
        main.run_callbacks("callback_entity_is_dead")
        main.run_callbacks("callback_pc_is_dead")
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
