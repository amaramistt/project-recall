# To-Do List
# 1) Create a separate file with classes so that findTurnOrder, initiateBattle, and takeTurn function as intended
# 2) Start reworking takeTurn() to make it more concise and fun to use
# 3) Rework magic in so that non-damaging spells may be used in the same way
# 4) Create a system where I can create spell functions (a la SkullCracker()) in a different file and import
#    them for use without too much rewriting of code
# 5) Start using pygame/libtcod and working on room generation and battle UI


import os
import random
from entity import entities, entities_by_id, Entity, find_turn_order

CLEAR_COMMAND = 'cls' if os.name == 'nt' else 'clear'

stats_order = {
    # required to let levelUp() or any function like it work at all
    1: "Max HP",
    2: "Max MP",
    3: "STR",
    4: "RES",
    5: "MND",
    6: "AGI"
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
def roll_stat(modifier: int):
    return (modifier * 4) + random.randrange(0, modifier+1)


def gen_starting_stats(character: Entity):
    # grab the character and their job
    # create random values according to the job's stat value that correspond to each stat
    # make those stats their stats
    # would act as a complete reset
    global jobs, stats_order
    character.Level = 1
    char_job = jobs[character.Job]

    character.STR = roll_stat(char_job[2])
    character.RES = roll_stat(char_job[3])
    character.MND = roll_stat(char_job[4])
    character.AGI = roll_stat(char_job[5])

    character.HP = character.MaxHP
    character.MP = character.MaxMP
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


def initiate_battle(player_party: list[Entity]):
    enemies_rolled = [entities_by_id[f'ENEMY_{random.randrange(1, 3)}'] for _ in range(random.randrange(1, 3))]

    print(enemies_rolled)
    take_turn(player_party, enemies_rolled)


def select_target(max_targets):
    target = int(input("Which numbered enemy would you like to attack?")) - 1
    return 0 if target < 0 else max_targets - 1 if target >= max_targets else target


def process_player_input(pc: Entity):
    pass


def take_turn(character: list[Entity], enemy: list[Entity]):
    actors = find_turn_order(character + enemy)
    os.system(CLEAR_COMMAND)

    for actor in actors:
        print(f"It's {actor.Name}'s turn!")

        if actor.EntityType == "PlayerCharacter":
            process_player_input(actor)



    first_entity = actors[0]
    target = None

    # Start of the first entity's turn
    print(f"It's {actors[0]['Name']}'s turn!")
    # Check whether the first entity is a PC
    if actors[0]["EntityType"] == "PlayerCharacter":
        cmd = input('Command? ').strip().lower()
        # Ask for and deal with command
        if cmd == "attack":
            # find the target of melee
            target = select_target(len(enemy))
            # deal damage to it
            damage = damage_calc(character, enemy[target], False)
            input(f"You attack the enemy with your weapon, dealing {damage} damage!")
            enemy[target]["HP"] -= damage
            # remove first entity from turn order
            actors.remove(actors[0])

        elif cmd.lower() == "magic":
            if len(character["Abilities"]) >= 1:
                print("Your available abilities:", character["Abilities"].keys())
                chosen_ability = input("Which ability do you choose?")
                use_ability = globals()[character["Abilities"][chosen_ability]["abilityFunc"]]
                if chosen_ability in character["Abilities"]:
                    if character["Abilities"][chosen_ability]["abilityType"] == "NOT_OFFENSIVE":
                        use_ability(character)
                    elif character["Abilities"][chosen_ability]["abilityType"] == "OFFENSIVE":
                        target = select_target(len(enemy))
                        damage = use_ability(character, enemy[target])
                        input(f"You deal {damage} damage!")
                        enemy[target]["HP"] -= damage
                        actors.remove(actors[0])
                else:
                    input("That is not an available ability!")
                    # take_turn(character, enemy)
            else:
                input("you don't have an ability dummy")
                # take_turn(character, enemy)

        if enemy[target]["HP"] <= 0:
            actors.remove(enemy[target])
            enemy.remove(enemy[target])
        else:
            input("fuck you")
            # take_turn(character, enemy)

    if actors[0]["EntityType"] == "Enemy":
        enemy_target = random.randrange(0, len(character))
        if actors[0]["STR"] > actors[0]["MND"]:
            enemy_damage = damage_calc(actors[0], character[enemy_target], False)
            input(f"The enemy attacks with their weapon and deals {enemy_damage} damage!")
        else:
            enemy_damage = damage_calc(actors[0], character[enemy_target], True)
            input(f"The enemy casts a spell and deals {enemy_damage} damage!")
        character[enemy_target]["HP"] -= enemy_damage
        if character[enemy_target]["HP"] <= 0:
            input(f"{character[enemy_target]['Name']} Has Fallen!")
            actors.remove(character[enemy_target])
            character.remove(character[enemy_target])

    # After the turn
    if first_entity != actors[0]:
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
