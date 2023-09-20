import os
import copy
import random
import gamestate
import uuid
from gamestate import GAME_STATE, print_with_conf, clear_terminal, deal_damage_to_target
import entity as ENTY

CLEAR = 'cls' if os.name == 'nt' else 'clear'

class Item(object):
    def __init__(self, template):
        self.id = None
        self.ItemType = template["ItemType"]
        self.ItemQuality = template["ItemQuality"]
        self.ItemCallback = template["ItemCallback"]
        self.ItemTrigger = template["ItemTrigger"]
        self.ItemUseEffect = template["ItemUseEffect"]
        self.ItemName = template["ItemName"]
        self.ItemDesc = template["ItemDesc"]
        self.Activated = False
        self.ItemHolder = None
        if self.ItemType == "equip" or self.ItemType == "none":
            self.ItemSubtype = template["ItemSubtype"]
            self.ItemStats = template["ItemStats"]
            self.Equipped = False
            self.CharacterEquipped = None
        self.ItemUseCount = 0
        self.ItemCost = 0

    
    @staticmethod
    def copy(other):
        clone = copy.deepcopy(other)
        clone.id = uuid.uuid4()
        return clone

    
    def obtained(self, character = "stash"):
        if character == "stash":
            character = GAME_STATE.bagged_items
        if self.ItemType == "passive":
            gamestate.add_callback(self.ItemTrigger, self.ItemCallback)
            GAME_STATE.passives.append(self)
            
        self.ItemHolder = character
        gamestate.run_callbacks("callback_item_pickup", entity_picking_up=character, item_picking_up=self)


    def equip(self, character):
        if self.ItemType != "equip":
            return
        if self.Equipped == True:
            print(f"This is currently equipped by {character.Name}!")
            cmd = input("(INPUT Y/N) Would you like to unequip it?    ").lower().strip()
            if cmd == "y":
                input(f"{self.ItemName} was unequipped!")
                if character.EquippedWeapon.id == self.id:
                    character.EquippedWeapon = item_data["no_equip"]
                    self.Equipped = False
                    self.CharacterEquipped = None
                    gamestate.remove_callback(self.ItemTrigger, self.ItemCallback)
                if character.EquippedArmor.id == self.id:
                    character.EquippedArmor = item_data["no_equip"]
                    self.Equipped = False
                    self.CharacterEquipped = None
                    gamestate.remove_callback(self.ItemTrigger, self.ItemCallback)
                for accessory in range(len(character.EquippedAccessories)):
                    if character.EquippedAccessories[accessory].id == self.id:
                        character.EquippedAccessories[accessory] = item_data["no_equip"]
                        self.Equipped = False
                        self.CharacterEquipped = None
                        gamestate.remove_callback(self.ItemTrigger, self.ItemCallback)
                        break 
            character.calc_equipment_stats()
            return
            
        if self in character.Items:
            
            if self.ItemSubtype == "weapon":
                if character.EquippedWeapon.ItemType is not "none":
                    gamestate.remove_callback(character.EquippedWeapon.ItemTrigger, character.EquippedWeapon.ItemCallback)
                    input(f"{character.EquippedWeapon.ItemName} was unequipped!")   
                    character.EquippedWeapon.Equipped = False
                    character.EquippedWeapon.CharacterEquipped = None 
                    
                character.EquippedWeapon = self
                self.Equipped = True
                self.CharacterEquipped = character
                gamestate.add_callback(character.EquippedWeapon.ItemTrigger, character.EquippedWeapon.ItemCallback)
                input(f"{character.Name} equipped {self.ItemName}!")
                
            elif self.ItemSubtype == "armor":
                if character.EquippedArmor.ItemType is not "none":
                    gamestate.remove_callback(character.EquippedArmor.ItemTrigger, character.EquippedArmor.ItemCallback)
                    input(f"{character.EquippedArmor.ItemName} was unequipped!")
                    character.EquippedArmor.Equipped = False
                    character.EquippedArmor.CharacterEquipped = None
                    
                character.EquippedArmor = self
                self.Equipped = True               
                self.CharacterEquipped = character
                gamestate.add_callback(character.EquippedArmor.ItemTrigger, character.EquippedArmor.ItemCallback)
                input(f"{character.Name} equipped {self.ItemName}!")                
                
            elif self.ItemSubtype == "accessory":
                if character.EquippedAccessories[1].ItemType is not "none":
                    gamestate.remove_callback(character.EquippedAccessories[1].ItemTrigger, character.EquippedAccessories[1].ItemCallback)
                    input(f"{character.EquippedAccessories[1].ItemName} was unequipped!")
                    character.EquippedAccessories[1].Equipped = False
                    character.EquippedAccessories[1].CharacterEquipped = None
                    
                character.EquippedAccessories[1] = character.EquippedAccessories[0]
                character.EquippedAccessories[0] = self
                self.Equipped = True
                self.CharacterEquipped = character
                input(f"{character.Name} equipped {self.ItemName}!")
                gamestate.add_callback(character.EquippedAccessories[0].ItemTrigger, character.EquippedAccessories[0].ItemCallback)
                
                
        character.calc_equipment_stats()

    def use(self):
        if self.ItemUseEffect is None:
            input("This item does not have a use effect!")
            return
        else:
            use_effect = self.ItemUseEffect
            if use_effect(self) == "dont_end_turn":
                return "dont_end_turn"
            self.ItemUseCount += 1

    def __repr__(self):
        return f"{self.ItemName}"

##########################
#     ITEM CALLBACKS     #
##########################


def spiked_armor(entity_hit, entity_attacker, damage_dealt):
    if entity_hit.EntityType != "PlayerCharacter" and entity_hit.EntityType != "Khorynn":
        return
    if entity_hit.EquippedArmor.ItemName == "Spiked Armor":
        damage_to_deal = int(damage_dealt * 0.3)
        gamestate.print_with_conf(f"{entity_hit.Name}'s Spiked Armor hurt their attacker for {damage_to_deal} damage!")
        gamestate.deal_damage_to_target(entity_hit, entity_attacker, damage_dealt) 


def golem_heart_item_use_count_reset():
    heart_exists = False
    for pc in GAME_STATE.player_party:
        for item in pc.Inventory:
            if item.Name == "Golem Heart":
                item.ItemUseCount = 0


def golem_heart(entity_hit, entity_attacker, damage_dealt):
    if entity_hit.EntityType != "PlayerCharacter" and entity_hit.EntityType != "Khorynn":
        return

    equipped = False
    for _ in range(len(entity_hit.EquippedAccessories)):
        if entity_hit.EquippedAccessories[_ - 1].ItemName == "Golem Heart":
            equipped = True
            heart = entity_hit.EquippedAccessories[_ - 1]
    if not equipped:
        return
        
    if entity_hit.HP <= int(entity_hit.get_max_hp() * 0.33) and heart.ItemUseCount <= 1:
        print_with_conf(f"{entity_hit.Name} is enraged! Their attack is maxed out!")
        entity_hit.change_stat("STR", 4)
        heart.ItemUseCount += 1
        gamestate.add_callback("callback_battle_is_finished", golem_heart_item_use_count_reset)
    return


def medeas_blessing(entity_casting, entity_targeted, spell_casted):  
    blessing_is_equipped = False
    if entity_casting.EntityType == "Player_Character" or entity_casting.EntityType == "Khorynn":
        for accessory in entity_casting.EquippedAccessories:
            if accessory.ItemName == "Medea's Blessing":
                blessing_is_equipped = True
                break
            
    if blessing_is_equipped:
        random_chance = random.uniform(0, 1)
        if random_chance > 0.9:
            input(f"The Medea's Blessing equipped by {entity_casting} glows! The spell repeats!")
            spell_casted(entity_casting, True)
            

def medeas_curse(entity_hit, entity_attacker, damage_dealt):
    equipped = False
    for _ in range(len(entity_attacker.EquippedAccessories)):
        if entity_attacker.EquippedAccessories[_ - 1].ItemName == "Medea's Curse":
            equipped = True
    if not equipped:
        return

    if GAME_STATE.battle_bloodthirsty_triggered:
        print_with_conf(f"{entity_attacker.Name}'s Medea's Curse glows a dim red! They swing at their target!")
        damage = int(damage_dealt * 0.5)
        print_with_conf(f"{entity_hit.Name} takes {damage} points of damage!")
        
        entity_hit.HP - damage
        if entity_hit.HP < 0:
            entity_hit.HP = 0
            
        if entity_hit.HP <= 0:
            print_with_conf(f"{entity_hit.Name} Has Fallen!")
            GAME_STATE.enemy_party.remove(entity_hit)
            run_callbacks("callback_entity_is_dead", entity_dead=entity_hit, entity_attacker=entity_attacker)
            run_callbacks("callback_pc_is_dead", entity_dead=entity_hit, entity_attacker=entity_attacker)
        


def pliabrand_target_override(attacker_action):
    if GAME_STATE.battle_entity_attacking.EquippedWeapon.ItemName == "Pliabrand":
        GAME_STATE.battle_entity_targeted = GAME_STATE.enemy_party

    
def pliabrand(item):
    if GAME_STATE.in_battle != True:
        input("This item can only be used in battle!")
        return "dont_end_turn"
        
    try:
        if item.ItemHolder.EquippedWeapon != item:
            input("This item must be equipped to a character to be used!")
            return "dont_end_turn"
    except AttributeError:
        input("This item must be equipped to a character to be used!")
        return "dont_end_turn"

    char = item.CharacterEquipped
    mp_to_spend = int(char.get_max_mp() * 0.1)
    cmd = input(f"Do you want to spend 10% of {char.Name}'s max mana ({mp_to_spend} MP) to activate the Pliabrand?\n(INPUT Y/N) They will hit every enemy with their physical attacks for the rest of the battle!   ").lower().strip()
    if cmd == "y":
        if char.MP >= mp_to_spend:
            char.MP - mp_to_spend
            input(f"{char.Name} spends {mp_to_spend} MP and activates their Pliabrand!")
            input("The blade unravels, coiling up on the ground by their side! The Pliabrand becomes a whip!")
            gamestate.add_callback("callback_enemy_is_targeted", pliabrand_target_override)
    else:
        return "dont_end_turn"



def medicinal_herb_bag(item):
    print("PARTY\n")
    for _ in range(len(GAME_STATE.player_party)):
        print(f"Party Member {_ + 1}: {GAME_STATE.player_party[_].Name} (HP: {GAME_STATE.player_party[_].HP}/{GAME_STATE.player_party[_].get_max_hp()})")
    print("\n\n")
    
    cmd = input(f"Input the numbered party member you would like to heal. For example, '1' is {GAME_STATE.player_party[0].Name}.\n(INPUT NUM) Input anything else to go back.").strip().lower()
    try:
        target = int(cmd) - 1 if int(cmd) - 1 > -1 else 0
        if target > len(GAME_STATE.player_party) - 1:
            target = len(GAME_STATE.player_party) - 1
        target_pc = GAME_STATE.player_party[target]
    except ValueError:
        return "dont_end_turn"

    input(f"{target_pc.Name} is healed to full, using one of the Medicinal Herb Bag's three pouches!")
    target_pc.HP = target_pc.get_max_hp()

    if item.ItemUseCount >= 2:
        input("That was the last of the pouches! You throw away the now empty bag!")
        try:
            item.ItemHolder.Items.remove(item)
        except AttributeError:
            item.ItemHolder.remove(item)
    return


def medicinal_herb(item):
    print("PARTY\n")
    for _ in range(len(GAME_STATE.player_party)):
        print(f"Party Member {_ + 1}: {GAME_STATE.player_party[_].Name} (HP: {GAME_STATE.player_party[_].HP}/{GAME_STATE.player_party[_].get_max_hp()})")
    print("\n\n")
    
    cmd = input(f"Input the numbered party member you would like to heal. For example, '1' is {GAME_STATE.player_party[0].Name}.\n(INPUT NUM) Input anything else to go back.").strip().lower()
    try:
        target = int(cmd) - 1 if int(cmd) - 1 > -1 else 0
        if target > len(GAME_STATE.player_party) - 1:
            target = len(GAME_STATE.player_party) - 1
        target_pc = GAME_STATE.player_party[target]
    except ValueError:
        return "dont_end_turn"

    input(f"{target_pc.Name} is healed to full using the Medicinal Herb!")
    target_pc.HP = target_pc.get_max_hp()
    input("You throw away the now empty pouch!")
    try:
        item.ItemHolder.Items.remove(item)
    except AttributeError:
        item.ItemHolder.remove(item)
    return

def sage_for_dummies(item):
    if GAME_STATE.in_battle:
        print_with_conf("You can't use this item in battle!")
        return "dont_end_turn"
    print("PARTY\n")
    for _ in range(len(GAME_STATE.player_party)):
        print(f"Party Member {_ + 1}: {GAME_STATE.player_party[_].Name} (Current Job: {GAME_STATE.player_party[_].Job})")
    print("\n\n")
    
    cmd = input(f"Input the numbered party member you would like to become a Sage. For example, '1' is {GAME_STATE.player_party[0].Name}.\n(INPUT NUM) Input anything else to go back.").strip().lower()
    try:
        target = int(cmd) - 1 if int(cmd) - 1 > -1 else 0
        if target > len(GAME_STATE.player_party) - 1:
            target = len(GAME_STATE.player_party) - 1
        target_pc = GAME_STATE.player_party[target]
    except ValueError:
        return

    cmd2 = input(f"(INPUT Y/N) Are you sure you want {target_pc.Name} to become a Sage?    ").strip().lower()
    if cmd2 != "y":
        return
    else:
        target_pc.change_job("sage")
        input(f"{target_pc.Name} successfully became a Sage!")
        try:
            item.ItemHolder.Items.remove(item)
        except AttributeError:
            item.ItemHolder.remove(item)


def spellblade_for_dummies(item):
    if GAME_STATE.in_battle:
        print_with_conf("You can't use this item in battle!")
        return "dont_end_turn"
    print("PARTY\n")
    for _ in range(len(GAME_STATE.player_party)):
        print(f"Party Member {_ + 1}: {GAME_STATE.player_party[_].Name} (Current Job: {GAME_STATE.player_party[_].Job})")
    print("\n\n")
    
    cmd = input(f"Input the numbered party member you would like to become a Spellblade. For example, '1' is {GAME_STATE.player_party[0].Name}.\n(INPUT NUM) Input anything else to go back.").strip().lower()
    try:
        target = int(cmd) - 1 if int(cmd) - 1 > -1 else 0
        if target > len(GAME_STATE.player_party) - 1:
            target = len(GAME_STATE.player_party) - 1
        target_pc = GAME_STATE.player_party[target]
    except ValueError:
        return

    cmd2 = input(f"(INPUT Y/N) Are you sure you want {target_pc.Name} to become a Spellblade?    ").strip().lower()
    if cmd2 != "y":
        return
    else:
        target_pc.change_job("sage")
        input(f"{target_pc.Name} successfully became a Spellblade!")
        try:
            item.ItemHolder.Items.remove(item)
        except AttributeError:
            item.ItemHolder.remove(item)

def hero_for_dummies(item):
    if GAME_STATE.in_battle:
        print_with_conf("You can't use this item in battle!")
        return "dont_end_turn"
    print("PARTY\n")
    for _ in range(len(GAME_STATE.player_party)):
        print(f"Party Member {_ + 1}: {GAME_STATE.player_party[_].Name} (Current Job: {GAME_STATE.player_party[_].Job})")
    print("\n\n")
    
    cmd = input(f"Input the numbered party member you would like to become a Hero. For example, '1' is {GAME_STATE.player_party[0].Name}.\n(INPUT NUM) Input anything else to go back.").strip().lower()
    try:
        target = int(cmd) - 1 if int(cmd) - 1 > -1 else 0
        if target > len(GAME_STATE.player_party) - 1:
            target = len(GAME_STATE.player_party) - 1
        target_pc = GAME_STATE.player_party[target]
    except ValueError:
        return

    cmd2 = input(f"(INPUT Y/N) Are you sure you want {target_pc.Name} to become a Hero?    ").strip().lower()
    if cmd2 != "y":
        return
    else:
        target_pc.change_job("hero")
        input(f"{target_pc.Name} successfully became a Hero!")
        try:
            item.ItemHolder.Items.remove(item)
        except AttributeError:
            item.ItemHolder.remove(item)

def strength_complimentary(item):
    if GAME_STATE.in_battle:
        print_with_conf("You can't use this item in battle!")
        return "dont_end_turn"
    print("PARTY\n")
    for _ in range(len(GAME_STATE.player_party)):
        print(f"Party Member {_ + 1}: {GAME_STATE.player_party[_].Name}")
    print("\n\n")
    
    cmd = input(f"Input the numbered party member you would like to take the Complimentary. For example, '1' is {GAME_STATE.player_party[0].Name}.\n(INPUT NUM) Input anything else to go back.").strip().lower()
    try:
        target = int(cmd) - 1 if int(cmd) - 1 > -1 else 0
        if target > len(GAME_STATE.player_party) - 1:
            target = len(GAME_STATE.player_party) - 1
        target_pc = GAME_STATE.player_party[target]
    except ValueError:
        return

    target_pc.STR += 2
    input(f"{target_pc.NAME} drank the Complimentary and permanently gained 2 strength!")
    try:
        item.ItemHolder.Items.remove(item)
    except AttributeError:
        item.ItemHolder.remove(item)    


def resistance_complimentary(item):
    if GAME_STATE.in_battle:
        print_with_conf("You can't use this item in battle!")
        return "dont_end_turn"
    print("PARTY\n")
    for _ in range(len(GAME_STATE.player_party)):
        print(f"Party Member {_ + 1}: {GAME_STATE.player_party[_].Name}")
    print("\n\n")
    
    cmd = input(f"Input the numbered party member you would like to take the Complimentary. For example, '1' is {GAME_STATE.player_party[0].Name}.\n(INPUT NUM) Input anything else to go back.").strip().lower()
    try:
        target = int(cmd) - 1 if int(cmd) - 1 > -1 else 0
        if target > len(GAME_STATE.player_party) - 1:
            target = len(GAME_STATE.player_party) - 1
        target_pc = GAME_STATE.player_party[target]
    except ValueError:
        return

    target_pc.RES += 2
    input(f"{target_pc.NAME} drank the Complimentary and permanently gained 2 resistance!")
    try:
        item.ItemHolder.Items.remove(item)
    except AttributeError:
        item.ItemHolder.remove(item)    


def mind_complimentary(item):
    if GAME_STATE.in_battle:
        print_with_conf("You can't use this item in battle!")
        return "dont_end_turn"
    print("PARTY\n")
    for _ in range(len(GAME_STATE.player_party)):
        print(f"Party Member {_ + 1}: {GAME_STATE.player_party[_].Name}")
    print("\n\n")
    
    cmd = input(f"Input the numbered party member you would like to take the Complimentary. For example, '1' is {GAME_STATE.player_party[0].Name}.\n(INPUT NUM) Input anything else to go back.").strip().lower()
    try:
        target = int(cmd) - 1 if int(cmd) - 1 > -1 else 0
        if target > len(GAME_STATE.player_party) - 1:
            target = len(GAME_STATE.player_party) - 1
        target_pc = GAME_STATE.player_party[target]
    except ValueError:
        return

    target_pc.MND += 2
    input(f"{target_pc.NAME} drank the Complimentary and permanently gained 2 mind!")
    try:
        item.ItemHolder.Items.remove(item)
    except AttributeError:
        item.ItemHolder.remove(item)    
        

def agility_complimentary(item):
    if GAME_STATE.in_battle:
        print_with_conf("You can't use this item in battle!")
        return "dont_end_turn"
    print("PARTY\n")
    for _ in range(len(GAME_STATE.player_party)):
        print(f"Party Member {_ + 1}: {GAME_STATE.player_party[_].Name}")
    print("\n\n")
    
    cmd = input(f"Input the numbered party member you would like to take the Complimentary. For example, '1' is {GAME_STATE.player_party[0].Name}.\n(INPUT NUM) Input anything else to go back.").strip().lower()
    try:
        target = int(cmd) - 1 if int(cmd) - 1 > -1 else 0
        if target > len(GAME_STATE.player_party) - 1:
            target = len(GAME_STATE.player_party) - 1
        target_pc = GAME_STATE.player_party[target]
    except ValueError:
        return

    target_pc.AGI += 2
    input(f"{target_pc.NAME} drank the Complimentary and permanently gained 2 agility!")
    try:
        item.ItemHolder.Items.remove(item)
    except AttributeError:
        item.ItemHolder.remove(item)    
    

def hand_grenade(item):
    if not GAME_STATE.in_battle:
        print_with_conf("You get the feeling that you really shouldn't use this outside of battle.")
        return
    clear_terminal()
    print_with_conf("You hold the grenade with shaky hands, unsure of its power but determined to use it.")
    print_with_conf("You pull the pin and throw it towards the enemy, watching it as it explodes!")
    bloodthirsty = None
    for _ in range(len(GAME_STATE.enemy_party)):
        if bloodthirsty is not None:
            deal_damage_to_target(item.ItemHolder, GAME_STATE.enemy_party[_ - 1], 9999999)
        else:
            bloodthirsty = deal_damage_to_target(item.ItemHolder, GAME_STATE.enemy_party[_ - 1], 9999999)
    print_with_conf("You solemnly pick up a piece of shrapnel from the shattered grenade, thinking about what you've done.")
    item.ItemHolder.Items.remove(item)


def merchants_crest():
    number_of_items_to_generate = 4 - len(GAME_STATE.shop_stock)
    items_genned = 0
    while items_genned < number_of_items_to_generate:
        item_to_present = random.choice(list(item_data[3].keys())) # Choose a random item from the shop item pool
        dupe = False
        for items_already_chosen in GAME_STATE.shop_stock: # For each item that's already spwaned:
            if dupe: # If the dupe flag is set, skip through the loop til the end
                continue
            if item_to_present == items_already_chosen.ItemName: # If the item we're about to spawn is already spawned, flag it
                dupe = True
        if dupe: # If the dupe flag is set, try again
            continue
        else: # If it isn't, spawn the item and tick the counter
            GAME_STATE.shop_stock.append(Item.copy(item_data[3][item_to_present]))
            items_genned += 1


def messiahs_cloak_damage_override(entity_hit, entity_attacker, damage_dealt):
    equipped = False
    for _ in range(len(entity_hit.EquippedAccessories)):
        if entity_hit.EquippedAccessories[_ - 1].ItemName == "Messiah's Cloak":
            equipped = True
            cloak = entity_hit.EquippedAccessories[_ - 1]
    if not equipped:
        return
    
    if cloak.ItemUseCount == 1:
        entity_hit.HP += damage_dealt
        if entity_hit.HP > entity_hit.MaxHP:
            entity_hit.HP = entity_hit.MaxHP
        print_with_conf(f"The magic of the barrier nullifies the damage and then fades away!")
        gamestate.remove_callback("callback_pc_is_hit", messiahs_cloak_damage_override)


def messiahs_cloak_use_count_reset():
    cloak_exists = False
    for pc in GAME_STATE.player_party:
        for item in pc.Inventory:
            if item.Name == "Messiah's Cloak":
                item.ItemUseCount = 0
                

def messiahs_cloak(entity_hit, entity_attacker, damage_dealt):
    equipped = False
    for _ in range(len(entity_hit.EquippedAccessories)):
        if entity_hit.EquippedAccessories[_ - 1].ItemName == "Messiah's Cloak":
            equipped = True
            cloak = entity_hit.EquippedAccessories[_ - 1]
    if not equipped:
        return

    if entity_hit.HP <= int(entity_hit.get_max_hp() * 0.33) and cloak.ItemUseCount <= 0:
        print_with_conf(f"A magical barrier surrounds {entity_hit.Name}!")
        gamestate.add_callback("callback_pc_is_hit", messiahs_cloak_damage_override)
        gamestate.add_callback("callback_battle_finished", messiahs_cloak_use_count_reset)
        cloak.ItemUseCount += 1
        



##########################
#       ITEM DATA        #
##########################

item_data = {
    1: { # 

        
    },

    
    2: { # Item Room Pool (More versatile than boss drops: these have the potential to shape runs)


        
    },

    
    3: { # Ornaldo's Shop Pool (A little higher than standard: These cost money)

        
        "SpikedArmor": Item({
            "ItemName": "Spiked Armor",
            "ItemDesc": "Plated armor with dangerous spikes protruding out everywhere. Enchanted with a curse that hurts its wearer's assailants.",
            "ItemType": "equip",
            "ItemSubtype": "armor",
            "ItemQuality": 1,
            "ItemTrigger": "callback_pc_is_hit", # KWARGS FORMAT: entity_hit, entity_attacker
            "ItemCallback": spiked_armor,
            "ItemUseEffect": None,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 20,
                "MND": 0,
                "AGI": 0
            },
        }),
        "Pliabrand": Item({
            "ItemName": "Pliabrand",
            "ItemDesc": "A sword that has the potential to unravel into a whip. Paying some mana allows the wielder to attack every enemy on the field at once.",
            "ItemType": "equip",
            "ItemSubtype": "weapon",
            "ItemQuality": 2,
            "ItemTrigger": None, # KWARGS FORMAT: entity_hit, entity_attacker
            "ItemCallback": None,
            "ItemUseEffect": pliabrand,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 30,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),
        "MedicinalHerb": Item({
            "ItemName": "Medicinal Herb",
            "ItemDesc": "A small bag containing magical herbs that can heal those who consume them. Good for one use.",
            "ItemType": "active",
            "ItemQuality": 1,
            "ItemTrigger": None, # KWARGS FORMAT: entity_hit, entity_attacker
            "ItemCallback": None,
            "ItemUseEffect": medicinal_herb,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),
        "MedicinalHerbBag": Item({
            "ItemName": "Medicinal Herb Bag",
            "ItemDesc": "A compartmented box containing three bags of Medicinal Herbs. Small and portable. Perfect for in-battle use.",
            "ItemType": "active",
            "ItemQuality": 2,
            "ItemTrigger": "", # KWARGS FORMAT: entity_hit, entity_attacker
            "ItemCallback": None,
            "ItemUseEffect": medicinal_herb_bag,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),
        "BerserkerGarb": Item({
            "ItemName": "Berserker's Garb",
            "ItemDesc": "Toga-esque clothing that does not protect its wearer from danger very well. Wearing it increases your strength.",
            "ItemType": "equip",
            "ItemSubtype": "armor",
            "ItemQuality": 2,
            "ItemTrigger": None,
            "ItemCallback": None,
            "ItemUseEffect": None,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 30,
                "RES": 10,
                "MND": 0,
                "AGI": 0
            },
        }),
        "SageForDummies": Item({
            "ItemName": "Sage For Dummies",
            "ItemDesc": "A book detailing the ins and outs of being a good Sage.\nAllows one party member to become a Sage without talking to Olivia.",
            "ItemType": "active",
            "ItemQuality": 2,
            "ItemTrigger": None,
            "ItemCallback": None,
            "ItemUseEffect": sage_for_dummies,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),
        "SpellbladeForDummies": Item({
            "ItemName": "Spellblade For Dummies",
            "ItemDesc": "A book detailing the ins and outs of being a good Spellblade.\nAllows one party member to become a Spellblade without talking to Olivia.",
            "ItemType": "active",
            "ItemQuality": 2,
            "ItemTrigger": None,
            "ItemCallback": None,
            "ItemUseEffect": spellblade_for_dummies,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),
        "MedeasBlessing": Item({
            "ItemName": "Medea's Blessing",
            "ItemDesc": "Brooch with the Consecration of Medea carved into it. The wearer feels more mindful while wearing it and might cast a spell twice in a row.",
            "ItemType": "equip",
            "ItemSubtype": "accessory",
            "ItemQuality": 2,        
            "ItemTrigger": "callback_spell_is_casted",
            "ItemCallback": medeas_blessing,
            "ItemUseEffect": None,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,            
                "STR": 0,
                "RES": 0,
                "MND": 30,
                "AGI": 0
            },
        }),
        "MedeasCurse": Item({
            "ItemName": "Medea's Curse",
            "ItemDesc": "A fractured brooch that used to inscribe the Consecration of Medea. The wearer feels more violent while wearing it and attacks twice while bloodthirsty.",
            "ItemType": "equip",
            "ItemSubtype": "accessory",
            "ItemQuality": 2,   
            "ItemCallback": medeas_curse,
            "ItemUseEffect": None,
            "ItemTrigger": "callback_enemy_is_hit",
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,            
                "STR": 20,
                "RES": 0,
                "MND": 0,
                "AGI": 10
            },
        }),
    },
    },

    
    4: { # Secret Shop Pool (only quality 4)

        
        "JulietsPoison": Item({
            "ItemName": "Juliet's Poison",
            "ItemDesc": "A complicated piece of contraband that begins a new Loop while keeping your possessions and strength.\nTakes preparation. Can't be used in battle.",
            "ItemType": "active",
            "ItemQuality": 4,
            "ItemTrigger": None,
            "ItemCallback": None,
            "ItemUseEffect": None,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),        
        "HeroForDummies": Item({
            "ItemName": "Hero For Dummies",
            "ItemDesc": "A book detailing the ins and outs of being a good Hero.\nAllows one party member to become a Hero without talking to Olivia.",
            "ItemType": "active",
            "ItemQuality": 4,
            "ItemTrigger": None,
            "ItemCallback": None,
            "ItemUseEffect": hero_for_dummies,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),
    },

    
    5: { # Items dropped by enemies, but not found anywhere else

        "TemplateItem": Item({
            "ItemName": "",
            "ItemDesc": "",
            "ItemType": "",
            "ItemSubtype": "",
            "ItemQuality": 1,
            "ItemTrigger": None,
            "ItemCallback": None,
            "ItemUseEffect": None,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),

        "MerchantsCrest": Item({
            "ItemName": "Merchant's Crest",
            "ItemDesc": "A crest commonly found in Osthaven worn by the moguls of the area. The wearer demands respect from Ornaldo and improves his stock.",
            "ItemType": "equip",
            "ItemSubtype": "accessory",
            "ItemQuality": 3,
            "ItemTrigger": "callback_shop_items_generated",
            "ItemCallback": merchants_crest,
            "ItemUseEffect": None,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),

        "HandGrenade": Item({
            "ItemName": "A Fucking Hand Grenade",
            "ItemDesc": "Time fuckery allowed for this WWII era grenade to show in the Prison. The poor slimes won't know what hit them.",
            "ItemType": "active",
            "ItemQuality": 4,
            "ItemTrigger": None,
            "ItemCallback": None,
            "ItemUseEffect": hand_grenade,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),
        
        "StrengthComplimentary": Item({
            "ItemName": "Strength Complimentary",
            "ItemDesc": "A small vial containing a potion designed to help its drinker gain a small amount of Strength. Contains one dose.",
            "ItemType": "",
            "ItemSubtype": "",
            "ItemQuality": 2,
            "ItemTrigger": None,
            "ItemCallback": None,
            "ItemUseEffect": strength_complimentary,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),

        "ResistanceComplimentary": Item({
            "ItemName": "Strength Complimentary",
            "ItemDesc": "A small vial containing a potion designed to help its drinker gain a small amount of Resistance. Contains one dose.",
            "ItemType": "",
            "ItemSubtype": "",
            "ItemQuality": 2,
            "ItemTrigger": None,
            "ItemCallback": None,
            "ItemUseEffect": resistance_complimentary,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),

        "MindComplimentary": Item({
            "ItemName": "Strength Complimentary",
            "ItemDesc": "A small vial containing a potion designed to help its drinker gain a small amount of Mind. Contains one dose.",
            "ItemType": "",
            "ItemSubtype": "",
            "ItemQuality": 2,
            "ItemTrigger": None,
            "ItemCallback": None,
            "ItemUseEffect": mind_complimentary,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),

        "AgilityComplimentary": Item({
            "ItemName": "Strength Complimentary",
            "ItemDesc": "A small vial containing a potion designed to help its drinker gain a small amount of Agility. Contains one dose.",
            "ItemType": "",
            "ItemSubtype": "",
            "ItemQuality": 2,
            "ItemTrigger": None,
            "ItemCallback": None,
            "ItemUseEffect": agility_complimentary,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),

        "GelatinousCrown": Item({
            "ItemName": "Gelatinous Crown",
            "ItemDesc": "The crown of a deceased Gelatinous King. Bordered by various jewels. The spirit of the King empowers the wearer and greatly increases maximum HP.",
            "ItemType": "equip",
            "ItemSubtype": "accessory",
            "ItemQuality": 3,
            "ItemTrigger": None,
            "ItemCallback": None,
            "ItemUseEffect": None,
            "ItemStats": {
                "MaxHP": 30,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),

        "GolemHeart": Item({
            "ItemName": "Golem Heart",
            "ItemDesc": "A pendant crowned with the heart of a deceased Stone Golem. The spirit of the Golem empowers its wearer and vastly increases their attack when near death.",
            "ItemType": "equip",
            "ItemSubtype": "accessory",
            "ItemQuality": 3,
            "ItemTrigger": "callback_pc_is_hit",
            "ItemCallback": golem_heart,
            "ItemUseEffect": None,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),
        
        "MessiahsCloak": Item({
            "ItemName": "Messiah's Cloak",
            "ItemDesc": "A black cloak embroidered with complex designs weaved with gold string. The spirit of the Messiah empowers its wearer and activates a magical barrier when near death.",
            "ItemType": "equip",
            "ItemSubtype": "accessory",
            "ItemQuality": 3,
            "ItemTrigger": "callback_pc_is_hit",
            "ItemCallback": messiahs_cloak,
            "ItemUseEffect": None,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),
    },

    
    6: { # Other: FIll later


        
    },

    
    7: { #Other: Fill later
        
    },

    
    "no_equip": Item({
        "ItemName": "None",
        "ItemDesc": "",
        "ItemType": "none",
        "ItemSubtype": "",
        "ItemQuality": 0,   
        "ItemCallback": "",
        "ItemTrigger": "",
        "ItemUseEffect": None,
        "ItemStats": {
            "MaxHP": 0,
            "MaxMP": 0,            
            "STR": 0,
            "RES": 0,
            "MND": 0,
            "AGI": 0        
        }
    })
}

def get_item_data_map():
    return item_data


def present_player_boss_item(item_pool = 1):
    print_with_conf("You find a treasure chest near the boss's corpse!")
    print_with_conf("You reach inside...")

    random_item_from_pool = random.choice(list(item_data[item_pool].keys()))
    input(random_item_from_pool)
    item = Item.copy(item_data[item_pool][random_item_from_pool])
    give_player_item(item)


def get_clone_by_name(item_id):
    got_it = False
    for item_pools in item_data.keys():
        if isinstance(item_data[item_pools], Item):
            continue
        if item_id in item_data[item_pools].keys():
            return Item.copy(item_data[item_pools][item_id])
    if not got_it:
        input(f"ItemError: get_clone_by_name could not find item with given item ID {item_id}")
        return Item.copy(item_data["no_equip"])

def give_player_item(item):
    print_with_conf(f"You obtained a(n) {item.ItemName}!")
    item_obtained = False
    for pc in GAME_STATE.player_party:
        if len(pc.Items) < 8 and not item_obtained:
            print_with_conf(f"{pc.Name} puts it in their inventory.")
            pc.Items.append(item)
            item.obtained(pc)
            item_obtained = True
    if not item_obtained:
        print_with_conf("Khorynn puts it in the Stash.")
        GAME_STATE.bagged_items.append(item)
        item.obtained()


def create_shop_stock():
    items_available = []
    amount_of_items_to_buy = random.randrange(1,4) # Decide how many items are available (1, 2, or 3)
    items_spawned = 0
    while items_spawned < amount_of_items_to_buy: # Stop when you've spawned the amount of items you're supposed to
        item_to_present = random.choice(list(item_data[3].keys())) # Choose a random item from the shop item pool
        dupe = False
        for items_already_chosen in items_available: # For each item that's already spwaned:
            if dupe: # If the dupe flag is set, skip through the loop til the end
                continue
            if item_to_present == items_already_chosen.ItemName: # If the item we're about to spawn is already spawned, flag it
                dupe = True
        if dupe: # If the dupe flag is set, try again
            continue
        else: # If it isn't, spawn the item and tick the counter
            items_available.append(Item.copy(item_data[3][item_to_present]))
            items_spawned += 1
    GAME_STATE.shop_stock = items_available
    gamestate.run_callbacks("callback_shop_items_generated")


def shop():
    clear_terminal()
    stock_already_decided = False
    if len(GAME_STATE.shop_stock) > 0:
        stock_already_decided = True
    if GAME_STATE.player_bought_something: # Make sure the player can only buy things from Ornaldo once per cycle
        print_with_conf("ORNALDO) Weren't you just here a second ago?")
        print_with_conf("ORNALDO) Nothing's changed about my stock right now, Khorynn. Come back later.")
        return


    print_with_conf("ORNALDO) Welcome to my emporium, Khroynn! Why don't you have a look-see at my wonderful wares?")
    
    # Get the stock
    if stock_already_decided: # If this is already done, skip this bit
        items_available = GAME_STATE.shop_stock
    else:
        create_shop_stock()
        items_available = GAME_STATE.shop_stock
    
    # Purchasing handling 
    print("ORNALDO) Here's what I've got!")
    numbered_item = 0
    cant_buy_anything = True
    for item in items_available:
        numbered_item += 1
        min_cost = item.ItemQuality * 15
        max_cost = item.ItemQuality * 20
        item.ItemCost = random.randrange(min_cost, max_cost + 1)
        print(f"{numbered_item}: {item.ItemName}, costs {item.ItemCost} gold")
        if item.ItemCost < GAME_STATE.money:
            cant_buy_anything = False
    if cant_buy_anything:
        print_with_conf("ORNALDO) Uh... I hate to say this, but you can't afford any of these. How about you, uh... come back later?")
        print_with_conf("You leave in an awkward silence.")
        return

    print_with_conf("ORNALDO) Come on, these are wonderful deals! You couldn't get this quality anywhere else.\n")
    
    player_chose_item = False
    while not player_chose_item:
        cmd = input("(INPUT) Which numbered item would you like to buy? Input 'back' to exit the shop.   ")
        try:
            cmd = int(cmd)
        except ValueError:
            if cmd == "back":
                print_with_conf("ORNALDO) Aww, nothing caught your eye? Come back if you change your mind!")
                return
            input("You inputted something other than a number! PLEASE only input a number!")
            continue

        cmd = 1 if cmd <= 0 else cmd
        cmd = len(items_available) if cmd > len(items_available) else cmd
        chosen_item = items_available[cmd - 1]
        if GAME_STATE.money < chosen_item.ItemCost:
            print_with_conf("ORNALDO) Oh, girl, you don't have enough money to buy that! Choose something else.")
        else:
            conf = input(f"(INPUT Y/N) Are you sure you would like to buy the {chosen_item.ItemName} for {chosen_item.ItemCost} gold?")
            if conf == "y":
                GAME_STATE.money -= chosen_item.ItemCost
                GAME_STATE.bagged_items.append(chosen_item)
                print_with_conf(f"ORNALDO) Thank you for buying my {chosen_item.ItemName}!! Wonderful doing business with you as always, Khorynn.")
                GAME_STATE.player_bought_something = True
                GAME_STATE.shop_stock = []
    print_with_conf("ORNALDO) Come back when you have more money!")


