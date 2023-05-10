class Entity(object):
    def __init__(self, template):
        self.Name = template["Name"]
        self.EntityType = template["EntityType"]
        self.Level = template["Level"]
        self.MaxHP = template["Max HP"]
        self.MaxMP = template["Max MP"]
        self.STR = template["STR"]
        self.RES = template["RES"]
        self.MND = template["MND"]
        self.AGI = template["AGI"]
        self.MP = template["MP"]
        self.HP = template["HP"]
        self.Abilities = template["Abilities"]
        if self.EntityType == "Enemy" or self.EntityType == "BossEnemy":
            self.ExperienceReward = 0
            self.MoneyReward = 0
        if self.EntityType == "BossEnemy":
            self.BossLogic = template["BossLogic"]
        elif self.EntityType == "PlayerCharacter":
            self.ExperienceCount = 0
            self.Job = template["Job"]  
            self.MasteredJobs = []
            self.Items = {}

    def __repr__(self):
        #makes it so that whenever the class object itself is printed, it prints the below instead!
        return f'\nName: {self.Name}\nLevel: {self.Level}\nHP: {self.HP}/{self.MaxHP}\nMP: {self.MP}/{self.MaxMP}\nJOB: {self.Job}\nSTR: {self.STR}\nRES: {self.RES}\nMND: {self.MND}\nAGI: {self.AGI}'

    


def find_turn_order(pc_party: list[Entity], enemies_in_battle: list[Entity]):
    entity_list = []
    for actors in pc_party:
        entity_list.append(actors)
    for actors in enemies_in_battle:
        entity_list.append(actors)
    return sorted(entity_list, key=lambda x: x.AGI, reverse=True)


def find_party_level(party):
    party_levels = []
    for member in party:
        party_levels.append(member.Level)
    party_levels = sorted(party_levels, reverse=True)
    return party_levels[0]


def roll_stat(modifier: int, start: bool):
    # start is true if it's the first level, used in gen_starting_stats
    # start is false if it's being used anywhere else, like in level_up
    if start:
        return (modifier * 4) + random.randrange(0, modifier + 1)
    if not start:
        return modifier + random.randrange(modifier, modifier + 4)


def gen_starting_stats(character: Entity, first_generation: bool):
    # Generates and distributes the starting stats of a character with any given job.
    # first_generation is True if it is the first time this character is being generated.
    # first_generation is False if it is not; i.e. changing to a new job.
    # If first_generation is False, the character retains their old abilities from other jobs and their level
    # However, their level is subtracted by 5
    global jobs, stats_order
    char_job = jobs[character.Job]
    character.MaxHP = roll_stat(char_job["stats"][0], True)
    character.MaxMP = roll_stat(char_job["stats"][1], True)
    character.STR = roll_stat(char_job["stats"][2], True)
    character.RES = roll_stat(char_job["stats"][3], True)
    character.MND = roll_stat(char_job["stats"][4], True)
    character.AGI = roll_stat(char_job["stats"][5], True)
    character.HP = character.MaxHP
    character.MP = character.MaxMP

    if first_generation:
        character.Level = 1
        character.Abilities = {}
    elif not first_generation:
        old_level = character.Level
        new_level = old_level - 5 if old_level - 5 > 0 else 1
        character.Level = 1
        for _ in range(1, new_level):
            level_up(character, True)
    

def level_up(character: Entity, invisible: bool):
    global jobs, stats_order
    char_job = jobs[character.Job]
    char_learned_ability = False

    character.Level += 1
    character.MaxHP += roll_stat(char_job["stats"][0], False)
    character.MaxMP += roll_stat(char_job["stats"][1], False)
    character.STR += roll_stat(char_job["stats"][2], False)
    character.RES += roll_stat(char_job["stats"][3], False)
    character.MND += roll_stat(char_job["stats"][4], False)
    character.AGI += roll_stat(char_job["stats"][5], False)
    character.HP = character.MaxHP
    character.MP = character.MaxMP
    if character.Level in char_job["abilities"]:
        ability_to_learn = char_job["abilities"][character.Level]
        character.Abilities[ability_to_learn["NAME"]] = ability_to_learn[ability_to_learn["NAME"]]
        char_learned_ability = True
        #there is a better way to do this and I do not know it
    
    if not invisible:
        input(f"{character.Name} Leveled Up!")
        if char_learned_ability:
            input(f"{character.Name} learned {ability_to_learn['NAME']}!")
        input(f"New stats:\n{character}\n")


def lvl_up_bulk(levelee, amount_to_lvl, hide_display: bool = True):
    for _ in range(amount_to_lvl):
        level_up(levelee, hide_display)

def generate_party_member(party_level):
    # Creates a new PlayerCharacter entity object returns it  
    # For now, every new entity will just be named "Billie", but i'll need to add a random name mechanic later
    # Should have appropriate starting stats for the job it rolls 
    global jobs
    # get a name from the names list
    gen_char_name = random.choice(player_character_names)
    player_character_names.remove(gen_char_name)
    #make a new entity
    entities[f"{gen_char_name}"] = Entity({
        "Name": f"{gen_char_name}",
        "EntityType": "PlayerCharacter",
        "Job": "undecided",
        "Level": 1,
        "Max HP": 1,
        "Max MP": 1,
        "STR": 1,
        "RES": 1,
        "MND": 1,
        "AGI": 1,
        "HP": 1,
        "MP": 1,
        "Abilities": {}
    })
    # make it a variable so it is more readable
    generated_character = entities[f"{gen_char_name}"]
    # give it a job
    generated_character.Job = random.choice(list(jobs.keys()))
    # give it starting stats
    gen_starting_stats(generated_character, True)
    # level it up to be useful to the party
    for _ in range(1,party_level):
        level_up(generated_character, True)
    return generated_character

def present_player_party_members(party_level):
    os.system(CLEAR)
    if len(player_party) <= 3:
        input(f"You may choose one of two adventurers to join your party!")
        char_1 = generate_party_member(party_level)
        print(f"Option 1\n{char_1}\n")
        char_2 = generate_party_member(party_level)
        print(f"Option 2\n{char_2}\n")
        cmd = input("(INPUT) Which option do you choose to join your party?")
        while not isinstance(cmd, int):
            try:
                cmd = int(cmd)
            except ValueError:
                input("You must input a number!")
                cmd = input("(INPUT) Which option do you choose to join your party?")
        if cmd == 1:
            if len(player_party) >= 3:
                input(f"You chose {char_1.Name}! They join your party!")
                player_party.append(char_1)
                input(player_party)
        elif cmd == 2:
            input(f"You chose {char_2.Name}! They join your party!")
            player_party.append(char_2)
            input(player_party)
    elif len(player_party) > 3:
        input("You are given the option to choose one of two party members, but your party is full!")
        input("You leave in an awkward silence.")


###




