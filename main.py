# To-Do List
# 1) Finishing touches on find_turn_order() my BEHATED.
# 2) Create a system where I can create spell functions (a la SkullCracker()) in a different file and import
#    them for use without too much rewriting of code
# 3) Create a system in which the player may exist outside of battle, so that items/equipment/accessories/menuing
#    may be implimented and debugged
# 4) Create a system in which passive, consumable, and non-consumable items can be seamlessly acquired and used,
#    preferably complete with item pools and broken synergies :3
# FAR IN THE FUTURE) Start using pygame/libtcod and work on room generation and battle UI


import os
import random
from entity import Entity, find_turn_order

stats_order = {
    # required to let levelUp() or any function like it work at all
    1: "Max HP",
    2: "Max MP",
    3: "STR",
    4: "RES",
    5: "MND",
    6: "AGI"
}

entities = {
    "Billie": Entity({
        "Name": "Billie",
        "EntityType": "PlayerCharacter",
        "Job": "mage",
        "Level": 1,
        "Max HP": 10,
        "Max MP": 2,
        "STR": 9,
        "RES": 11,
        "MND": 3,
        "AGI": 3,
        "HP": 10,
        "MP": 2,
        "Abilities": {
            "SkullCrusher": {
                "abilityFunc": "SkullCrusher",
                "abilityType": "OFFENSIVE"
            },
            "Focus": {
                "abilityFunc": "Focus",
                "abilityType": "NOT_OFFENSIVE"
            },
        }
    }),
    "EnemyWizard": Entity({
        # Basic things that should be easy to call like name, id, and stats
        "Name": "Enraged Wizard",
        "EntityType": "Enemy",
        "EntityID": "ENEMY_1",
        "Job": "mage",
        "Level": 1,
        "Max HP": 4,
        "Max MP": 11,
        "STR": 3,
        "RES": 3,
        "MND": 12,
        "AGI": 6,
        "HP": 4,
        "MP": 11,
        "Abilities": {
            "Fireball": "forfireball"
        }
    }),
    "EnemyWarrior": Entity({
        "Name": "Stalwart Warrior",
        "EntityType": "Enemy",
        "EntityID": "ENEMY_2",
        "Job": "warrior",
        "Level": 1,
        "Max HP": 10,
        "Max MP": 2,
        "STR": 10,
        "RES": 12,
        "MND": 3,
        "AGI": 4,
        "HP": 10,
        "MP": 2,
        "Abilities": {
            "Skull Crusher": "SkullCrusher"
        }
    })
}

# JOB STATS SYNTAX
# 1 means low
# 2 means middling
# 3 means high
# 4 means exceptional
# stats go HP > MP > STR > RES > MND > AGI
# !!! IN ORDER !!!
jobs = {
    "warrior": [3, 1, 3, 3, 1, 1],
    "just a guy": [1, 1, 1, 1, 1, 1],
    "mage": [1, 3, 1, 1, 3, 2],
    "priest": [1, 3, 2, 1, 2, 2]
}


# 1 -> 4-5
# 2 -> 8-10
# 3 -> 12-15
# 4 -> 16-20
def roll_stat(modifier: int, start: bool):
    #start is true if it's the first level, used in gen_starting_stats
    #start is false if it's being used anywhere else, like in level_up
    if start == True:
        return (modifier * 4) + random.randrange(0, modifier+1)
    if start == False:
        return modifier + random.randrange(modifier, modifier+4)


def gen_starting_stats(character: Entity):
    # grab the character and their job
    # create random values according to the job's stat value that correspond to each stat
    # make those stats their stats
    # would act as a complete reset
    global jobs, stats_order
    character.Level = 1
    char_job = jobs[character.Job]

    character.MaxHP = roll_stat(char_job[0], True)
    character.MaxMP = roll_stat(char_job[1], True)
    character.STR = roll_stat(char_job[2], True)
    character.RES = roll_stat(char_job[3], True)
    character.MND = roll_stat(char_job[4], True)
    character.AGI = roll_stat(char_job[5], True)
    character.HP = character.MaxHP
    character.MP = character.MaxMP
    pass


def level_up(character):
    global jobs, stats_order
    
    char_job = jobs[character.Job]
    print(f"{character.Name} Leveled Up!")
    character.MaxHP += roll_stat(char_job[0], False)
    character.MaxMP += roll_stat(char_job[1], False)
    character.STR += roll_stat(char_job[2], False)
    character.RES += roll_stat(char_job[3], False)
    character.MND += roll_stat(char_job[4], False)
    character.AGI += roll_stat(char_job[5], False)
    character.HP = character.MaxHP
    character.MP = character.MaxMP
    print("New stats:", character, "\n")


def initiate_battle(player_party):
    enemies_to_spawn = random.randrange(1, 3)
    enemies_rolled = []
    for _ in range(0, enemies_to_spawn):
        enemy_spawned = f"ENEMY_{random.randrange(1, 3)}"
        enemies_rolled.append(enemy_spawned)
    print(enemies_rolled)
    take_turn(player_party, enemies_rolled)


def find_target(amount_of_enemies):
    target = int(input("Which numbered enemy would you like to attack?"))
    target -= 1
    if target > 0:
        target = 0
    elif target > amount_of_enemies:
        target = amount_of_enemies - 1
    return target


def take_turn(character: list[Entity], enemy: list[Entity]):
    turn_order = find_turn_order([character, enemy])
    os.system('cls' if os.name == 'nt' else 'clear')
    target = None

    #go through this process for every entity and provide a more concise way to refer to the entity taking the turn
    for entity in turn_order:    
        # Start of the first entity's turn
        print(f"It's {entity['Name']}'s turn!")
        # Check whether the first entity is a PC
        if entity["EntityType"] == "PlayerCharacter":
            #do PC shit
            pc_turn_handler(entity,enemy,turn_order)
            
    
        #check whether or not the first entity is an enemy
        if entity["EntityType"] == "Enemy":
            #find a random target (advanced targeting will be developed later most likely (make this all just a more complex function))
            enemy_target = random.randrange(0, len(character))
            #check if its mind is higher than its strength and use the higher stat in the damage calc
            if entity["STR"] > entity["MND"]:
                enemy_damage = damage_calc(entity, character[enemy_target], False)
                input(f"The enemy attacks with their weapon and deals {enemy_damage} damage!")
            else:
                enemy_damage = damage_calc(entity, character[enemy_target], True)
                input(f"The enemy casts a spell and deals {enemy_damage} damage!")
            #deal damage
            character[enemy_target]["HP"] -= enemy_damage
            #check if the character died
            if character[enemy_target]["HP"] <= 0:
                #kill them
                input(f"{character[enemy_target]['Name']} Has Fallen!")
                turn_order.remove(character[enemy_target])
                character.remove(character[enemy_target])
        


def pc_turn_handler(character, enemy: list[Entity], turn_order: list[Entity]):
    cmd = input("Command?\n").strip().lower()
    if cmd == "attack":
        # find the target of melee
        target = find_target(len(enemy))
        # deal damage to it
        damage = damage_calc(character, enemy[target], False)
        input(f"You attack the enemy with your weapon, dealing {damage} damage!")
        enemy[target]["HP"] -= damage
        if enemy[target["HP"]] <= 0:
            input(f"{enemy[target]['Name']} has fallen!")
            turn_order.remove(enemy[target])
            enemy.remove(enemy[target])
    elif cmd == "ability":
        ability_handler(character,enemy,turn_order)
    else:
        input("Invalid command!")
        pc_turn_handler(character,enemy,turn_order)
        return None
    if enemy[target]["HP"] <= 0:
        turn_order.remove(enemy[target])
        enemy.remove(enemy[target])

def ability_handler(character: list[Entity], enemy: list[Entity], turn_order: list[Entity]):
    #check if you have an abiltiy
    if len(character["Abilities"]) >= 1:
        #print the abilities and let you choose one
        print("Your available abilities:", character["Abilities"].keys())
        chosen_ability = input("Which ability do you choose?")
        use_ability = globals()[character["Abilities"][chosen_ability]["abilityFunc"]]
        #check if the input is an ability you have
        if chosen_ability in character["Abilities"]:
            #if it's not an offensive ability, just do the function as any damage calcs involved will be in the corresponding function
            if character["Abilities"][chosen_ability]["abilityType"] == "NOT_OFFENSIVE":
                #!!!CRITICAL REMINDER!!!
                #SINCE THE ABILITY HANDLER DOESN'T CHECK IF ANYTHING DIED, THE ABILITY FUNCTION HAS TO DEAL WITH IT
                #THIS ONLY MATTERS IF THE ABILITY TYPE IS NOT_OFFENSIVE BUT STILL DEALS DAMAGE
                #!!!CRITICAL REMINDER!!!
                use_ability(character)
            #if it is an offensive ability, use it as a glorified damage calc
            elif character["Abilities"][chosen_ability]["abilityType"] == "OFFENSIVE":
                target = find_target(len(enemy))
                damage = use_ability(character, enemy[target])
                input(f"You deal {damage} damage!")
                enemy[target]["HP"] -= damage
                turn_order.remove(entity)
        #if the input isn't something you have, give an error
        else:
            input("That is not an available ability!")
            pc_turn_handler(character, enemy, turn_order)
            return None
    #if you don't have an ability, don't let them do anything
    else:
        input("you don't have an ability dummy")
        pc_turn_handler(character, enemy, turn_order)
###

def damage_calc(attacker, defender, magic):
    critical = 2 if random.uniform(0, 1) >= 0.95 else 1

    if critical > 1:
        print("It's a critical hit!")

    if not magic:
        damage = (
            # make sure we don't have float damage numbers (PLAYERS WOULD KILL ME!)
            int(
                # randomize damage (+/- 10%)
                random.uniform(0.9, 1.1) *
                (attacker.STR - (defender.RES * 0.5) * critical)
            ))
        if damage >= 0:
            return damage
        else:
            return 0

    elif magic:
        damage = int(random.uniform(0.9, 1.1) *
                     (attacker.MND - (defender.RES * 0.3) * critical))
        if damage >= 0:
            return damage
        else:
            return 0
    else:
        print("You forgot to set magic, dumbass.")
        return 0


#\/\/ Probably needs a rework \/\/
# def battle_cleanup(character, enemy, exp, gold):
#     if character["HP"] > 0:
#         print("B A T T L E  W O N !")
#         print(f"You defeated {enemy.Name}!")
#         print(f"You got {exp} experience points!")
#         input(f"You got {gold} gold pieces!")
#         return True
#     elif character["HP"] <= 0:
#         print("Y O U  D I E D")
#         input(" game over...")
#         return False


def skull_crusher(attacker, defender):
    if attacker.MP < 3:
        input(f"{attacker.Name} didn't have enough MP to use Skull Crusher!")
        return 0
    input(f"{attacker.Name} uses Skull Crusher!")
    attacker.MP -= 3
    input("They siphon 3 points of MP!")
    defense_ignored = int(defender.RES * 0.8)
    defender.RES -= defense_ignored
    input(f"{attacker.Name} slams their weapon onto {defender.Name}'s head with a horrifying CRACK!")
    damage = damage_calc(attacker, defender, False)
    defender.RES += defense_ignored
    return int(damage)


def forfireball(attacker, defender):
    if attacker.MP < 40:
        return 0
    else:
        attacker.MP -= 40
        input(f"{attacker.Name} casts Fireball!")
        defense_ignored = defender.RES
        defender.RES -= defense_ignored
        input("Even the most powerful armor shatters when the shockwave hits it!")
        damage = damage_calc(attacker, defender, True) * 2
        defender.RES += defense_ignored
        return damage


def focus(user):
    mind_multiple = (user.MND * 0.05) + 1
    if mind_multiple > 5:
        mind_multiple = 5
    if user.MP < 5:
        input(f"{user.Name} tried to use Focus, but they didn't have enough MP!")
        return None
    else:
        input(f"{user.Name} used Focus!")
        input("They take a deep breath and center their thoughts...")
        input("They feel better already!")
        health_to_heal = int(user.MaxHP * 0.1 + (random.randrange(10, 15) * mind_multiple))
        if (health_to_heal + user.HP) > user.MaxHP:
            health_to_heal = user.MaxHP - user.HP
        input(f"{user.Name} heals {health_to_heal} HP!")
        user.HP += health_to_heal
        input("They gain a boost to Mind!")
        mind_to_gain = int(user.MND * 0.1)
        if mind_to_gain == 0:
            mind_to_gain = 1
        user.MND += mind_to_gain


def main():
    gen_starting_stats(entities["Billie"])
    input(entities["Billie"])
    for _ in range(15):
        level_up(entities["Billie"])
    for _ in range(10):
        level_up(entities["EnemyWizard"])
    for _ in range(10):
        level_up(entities["EnemyWarrior"])

    entities["Billie"].HP -= damage_calc(entities["EnemyWizard"], entities["Billie"], True)
    input(f"{entities['Billie'].HP}")
    focus(entities["Billie"])
    input(f"{entities['Billie'].HP}")
    turn_order = find_turn_order([entities["Billie"], [entities["EnemyWizard"], entities["EnemyWarrior"]]])
    for entity in turn_order:
        print(entity.Name)

    # initiateBattle([entities["Billie"]])
    print(skull_crusher(entities["Billie"], entities["EnemyWizard"]))
    print(forfireball(entities["EnemyWizard"], entities["Billie"]))

    # Have to find a way to make turnOrder() work before I can start debugging the new takeTurn()
    # takeTurn([entities["Billie"]], [entities["EnemyWizard"],entities["EnemyWarrior"]])


if __name__ == "__main__":
    main()
