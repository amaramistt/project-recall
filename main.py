# To-Do List
# 1) Create a separate file with classes so that findTurnOrder, initiateBattle, and takeTurn function as intended
# 2) Start reworking takeTurn() to make it more concise and fun to use
# 3) Rework magic in so that non-damaging spells may be used in the same way
# 4) Create a system where I can create spell functions (a la SkullCracker()) in a different file and import
#    them for use without too much rewriting of code
# 5) Start using pygame/libtcod and working on room generation and battle UI


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


def gen_starting_stats(character):
    # grab the character and their job
    # create random values according to the job's stat value that correspond to each stat
    # make those stats their stats
    # would act as a complete reset
    global jobs, stats_order
    character["Level"] = 1
    char_job = jobs[character["Job"]]
    job_stat = 0
    sheet_stat = 1
    while sheet_stat <= 6:
        generated_stat = char_job[job_stat] + (char_job[job_stat] * 3) + random.randrange(0, (char_job[job_stat] + 1))
        character[stats_order[sheet_stat]] = generated_stat
        print(f"{character['Name']}'s {stats_order[sheet_stat]} stat: {generated_stat}")
        job_stat += 1
        sheet_stat += 1
    character["HP"] = character["Max HP"]
    character["MP"] = character["Max MP"]
    pass


def level_up(character):
    global jobs, stats_order

    print(f"{character['Name']} Leveled Up!")
    job_stat = 0
    sheet_stat = 1
    while sheet_stat <= 6:
        character["HP"] = character["Max HP"]
        character["MP"] = character["Max MP"]
        lvl_up_stat = random.randrange((jobs[character["Job"]][job_stat]), (jobs[character["Job"]][job_stat] + 5))
        character[stats_order[sheet_stat]] = character[stats_order[sheet_stat]] + lvl_up_stat
        job_stat += 1
        sheet_stat += 1
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


def take_turn(character, enemy):
    turn_order = find_turn_order([character, enemy])
    os.system('cls' if os.name == 'nt' else 'clear')
    first_entity = turn_order[0]
    target = None

    # Start of the first entity's turn
    print(f"It's {turn_order[0]['Name']}'s turn!")
    # Check whether the first entity is a PC
    if turn_order[0]["EntityType"] == "PlayerCharacter":
        cmd = input('Command? ')
        # Ask for and deal with command
        if cmd.lower() == "attack":
            # find the target of melee
            target = find_target(len(enemy))
            # deal damage to it
            damage = damage_calc(character, enemy[target], False)
            input(f"You attack the enemy with your weapon, dealing {damage} damage!")
            enemy[target]["HP"] -= damage
            # remove first entity from turn order
            turn_order.remove(turn_order[0])

        elif cmd.lower() == "magic":
            if len(character["Abilities"]) >= 1:
                print("Your available abilities:", character["Abilities"].keys())
                chosen_ability = input("Which ability do you choose?")
                use_ability = globals()[character["Abilities"][chosen_ability]["abilityFunc"]]
                if chosen_ability in character["Abilities"]:
                    if character["Abilities"][chosen_ability]["abilityType"] == "NOT_OFFENSIVE":
                        use_ability(character)
                    elif character["Abilities"][chosen_ability]["abilityType"] == "OFFENSIVE":
                        target = find_target(len(enemy))
                        damage = use_ability(character, enemy[target])
                        input(f"You deal {damage} damage!")
                        enemy[target]["HP"] -= damage
                        turn_order.remove(turn_order[0])
                else:
                    input("That is not an available ability!")
                    take_turn(character, enemy)
            else:
                input("you don't have an ability dummy")
                take_turn(character, enemy)

        if enemy[target]["HP"] <= 0:
            turn_order.remove(enemy[target])
            enemy.remove(enemy[target])
        else:
            input("fuck you")
            take_turn(character, enemy)

    if turn_order[0]["EntityType"] == "Enemy":
        enemy_target = random.randrange(0, len(character))
        if turn_order[0]["STR"] > turn_order[0]["MND"]:
            enemy_damage = damage_calc(turn_order[0], character[enemy_target], False)
            input(f"The enemy attacks with their weapon and deals {enemy_damage} damage!")
        else:
            enemy_damage = damage_calc(turn_order[0], character[enemy_target], True)
            input(f"The enemy casts a spell and deals {enemy_damage} damage!")
        character[enemy_target]["HP"] -= enemy_damage
        if character[enemy_target]["HP"] <= 0:
            input(f"{character[enemy_target]['Name']} Has Fallen!")
            turn_order.remove(character[enemy_target])
            character.remove(character[enemy_target])

    # After the turn
    if first_entity != turn_order[0]:
        # check if there's no more enemies
        if len(enemy) == 0:
            # cleanup
            battle_cleanup(character, enemy, 10, 12)


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
                (attacker["STR"] - (defender["RES"] * 0.5) * critical)
            ))
        if damage >= 0:
            return damage
        else:
            return 0

    elif magic:
        damage = int(random.uniform(0.9, 1.1) *
                     (attacker["MND"] - (defender["RES"] * 0.3) * critical))
        if damage >= 0:
            return damage
        else:
            return 0
    else:
        print("You forgot to set magic, dumbass.")
        return 0


def battle_cleanup(character, enemy, exp, gold):
    if character["HP"] > 0:
        print("B A T T L E  W O N !")
        print(f"You defeated {enemy.name}!")
        print(f"You got {exp} experience points!")
        input(f"You got {gold} gold pieces!")
        return True
    elif character["HP"] <= 0:
        print("Y O U  D I E D")
        input(" game over...")
        return False


def skull_crusher(attacker, defender):
    if attacker["MP"] < 3:
        input(f"{attacker['Name']} didn't have enough MP to use Skull Crusher!")
        return 0
    input(f"{attacker['Name']} uses Skull Crusher!")
    attacker["MP"] -= 3
    input("They siphon 3 points of MP!")
    defense_ignored = int(defender["RES"] * 0.8)
    defender["RES"] -= defense_ignored
    input(f"{attacker['Name']} slams their weapon onto {defender['Name']}'s head with a horrifying CRACK!")
    damage = damage_calc(attacker, defender, False)
    defender["RES"] += defense_ignored
    return int(damage)


def forfireball(attacker, defender):
    if attacker["MP"] < 40:
        return 0
    else:
        attacker["MP"] -= 40
        input("")
        defense_ignored = int(defender["RES"] * 0.5)
        defender["RES"] -= defense_ignored
        damage = damage_calc(attacker, defender, True) * 2
        defender["RES"] += defense_ignored
        return damage


def focus(user):
    mind_multiple = (user["MND"] * 0.05) + 1
    if mind_multiple > 5:
        mind_multiple = 5
    if user["MP"] < 5:
        input(f"{user['Name']} tried to use Focus, but they didn't have enough MP!")
        return None
    else:
        input(f"{user['Name']} used Focus!")
        input("They take a deep breath and center their thoughts...")
        input("They feel better already!")
        health_to_heal = int(user["Max HP"] * 0.1 + (random.randrange(10, 15) * mind_multiple))
        if (health_to_heal + user["HP"]) > user["Max HP"]:
            health_to_heal = user["Max HP"] - user["HP"]
        input(f"{user['Name']} heals {health_to_heal} HP!")
        user["HP"] += health_to_heal
        input("They gain a boost to Mind!")
        mind_to_gain = int(user["MND"] * 0.1)
        if mind_to_gain == 0:
            mind_to_gain = 1
        user["MND"] += mind_to_gain


def main():
    gen_starting_stats(entities["Billie"])
    input(entities["Billie"])
    for _ in range(15):
        level_up(entities["Billie"])
    for _ in range(10):
        level_up(entities["EnemyWizard"])
    for _ in range(10):
        level_up(entities["EnemyWarrior"])

    entities["Billie"]["HP"] -= damage_calc(entities["EnemyWizard"], entities["Billie"], True)
    input(f"{entities['Billie']['HP']}")
    focus(entities["Billie"])
    input(f"{entities['Billie']['HP']}")
    # findTurnOrder([entities["Billie"], [entities["EnemyWizard"], entities["EnemyWarrior"]]])
    # initiateBattle([entities["Billie"]])
    print(skull_crusher(entities["Billie"], entities["EnemyWizard"]))
    print(forfireball(entities["EnemyWizard"], entities["Billie"]))

    # Have to find a way to make turnOrder() work before I can start debugging the new takeTurn()
    # takeTurn([entities["Billie"]], [entities["EnemyWizard"],entities["EnemyWarrior"]])


if __name__ == "__main__":
    main()
