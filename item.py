import os
import copy
import random
import gamestate
import uuid
from gamestate import GAME_STATE, print_with_conf

CLEAR = 'cls' if os.name == 'nt' else 'clear'

class Item(object):
    def __init__(self, template):
        self.id = None
        self.ItemType = template["ItemType"]
        self.ItemQuality = template["ItemQuality"]
        self.ItemCallback = template["ItemCallback"]
        self.ItemTrigger = template["ItemTrigger"]
        self.ItemName = template["ItemName"]
        self.ItemDesc = template["ItemDesc"]
        if self.ItemType == "equip" or self.ItemType == "none":
            self.ItemSubtype = template["ItemSubtype"]
            self.ItemStats = template["ItemStats"]
            self.Equipped = False
        self.ItemCost = 0

    @staticmethod
    def copy(other):
        clone = copy.deepcopy(other)
        clone.id = uuid.uuid4()
        return clone

    def obtained(self, character):
        if self.ItemType == "passive":
            gamestate.add_callback(self.ItemTrigger, self.ItemCallback)
            GAME_STATE.passives.append(self)

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
                if character.EquippedArmor.id == self.id:
                    character.EquippedArmor = item_data["no_equip"]
                    self.Equipped = False
                for accessory in range(len(character.EquippedAccessories)):
                    if character.EquippedAccessories[accessory].id == self.id:
                        character.EquippedAccessories[accessory] = item_data["no_equip"]
                        self.Equipped = False
                        break 
            character.calc_equipment_stats()
            return
            
        if self in character.Items:
            
            if self.ItemSubtype == "weapon":
                if character.EquippedWeapon.ItemType is not "none":
                    gamestate.remove_callback(character.EquippedWeapon.ItemTrigger, character.EquippedWeapon.ItemCallback)
                    print_with_conf(f"{character.EquippedWeapon.ItemName} was unequipped!")   
                    character.EquippedWeapon.Equipped = False
                character.EquippedWeapon = self
                self.Equipped = True
                gamestate.add_callback(character.EquippedWeapon.ItemTrigger, character.EquippedWeapon.ItemCallback)
                print_with_conf(f"{character.Name} equipped {self.ItemName}!")
                
            elif self.ItemSubtype == "armor":
                if character.EquippedArmor.ItemType is not "none":
                    gamestate.remove_callback(character.EquippedArmor.ItemTrigger, character.EquippedArmor.ItemCallback)
                    print_with_conf(f"{character.EquippedArmor.ItemName} was unequipped!")
                    character.EquippedArmor.Equipped = False
                character.EquippedArmor = self
                self.Equipped = True                
                gamestate.add_callback(character.EquippedArmor.ItemTrigger, character.EquippedArmor.ItemCallback)
                print_with_conf(f"{character.Name} equipped {self.ItemName}!")                
                
            elif self.ItemSubtype == "accessory":
                if character.EquippedAccessories[1].ItemType is not "none":
                    gamestate.remove_callback(character.EquippedAccessories[1].ItemTrigger, character.EquippedAccessories[1].ItemCallback)
                    print_with_conf(f"{character.EquippedAccessories[1].ItemName} was unequipped!")
                    character.EquippedAccessories[1].Equipped = False                    
                character.EquippedAccessories[1] = character.EquippedAccessories[0]
                character.EquippedAccessories[0] = self
                self.Equipped = True                
                print_with_conf(f"{character.Name} equipped {self.ItemName}!")
                gamestate.add_callback(character.EquippedAccessories[0].ItemTrigger, character.EquippedAccessories[0].ItemCallback)
                
        character.calc_equipment_stats()

    def __repr__(self):
        return f"{self.ItemName}"

##########################
#    ITEM CALLBACKS      #
##########################


def spiked_armor(entity_hit, entity_attacker, damage_dealt):
    pass


def medeas_blessing(entity_buffing_debuffing, stat_changed, change_stages):
    pass


##########################
#       ITEM DATA        #
##########################

item_data = {
    1: { # Boss Drop Pool (standard item pool)
        "MedeasBlessing": Item({
            "ItemName": "Medea's Blessing",
            "ItemDesc": "Brooch with the Consecration of Medea carved into it. The wearer feels more mindful while wearing it and might cast a spell twice in a row.",
            "ItemType": "equip",
            "ItemSubtype": "accessory",
            "ItemQuality": 2,        
            "ItemTrigger": "callback_spell_is_casted",
            "ItemCallback": medeas_blessing,
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,            
                "STR": 0,
                "RES": 0,
                "MND": 20,
                "AGI": 0
            },
        }),
        "MedeasCurse": Item({
            "ItemName": "Medea's Curse",
            "ItemDesc": "A fractured brooch that used to inscribe the Consecration of Medea. The wearer feels more violent while wearing it and gets twice as strong while bloodthirsty.",
            "ItemType": "equip",
            "ItemSubtype": "accessory",
            "ItemQuality": 2,   
            "ItemCallback": "medeas_curse",
            "ItemTrigger": "callback_bloodthirsty_triggered",
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,            
                "STR": 10,
                "RES": 0,
                "MND": 0,
                "AGI": 10
            },
        }),
    },
    2: { # Item Room Pool (Higher than standard: Item rooms are not guaranteed)

    },
    3: { # Ornaldo's Shop Pool (A little higher than standard: These cost money)
                "SpikedArmor": Item({
            "ItemName": "Spiked Armor",
            "ItemDesc": "Plated armor with dangerous spikes protruding out everywhere. Hurts assailants that attempt to hit the wearer for physical damage.",
            "ItemType": "equip",
            "ItemSubtype": "armor",
            "ItemQuality": 1,
            "ItemTrigger": "callback_pc_is_hit", # KWARGS FORMAT: entity_hit, entity_attacker
            "ItemCallback": "spiked_armor",
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 0,
                "RES": 10,
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
            "ItemTrigger": "", # KWARGS FORMAT: entity_hit, entity_attacker
            "ItemCallback": "pliabrand",
            "ItemStats": {
                "MaxHP": 0,
                "MaxMP": 0,
                "STR": 20,
                "RES": 0,
                "MND": 0,
                "AGI": 0
            },
        }),
        "MedicinalHerbBag": Item({
            "ItemName": "Medicinal Herb Bag",
            "ItemDesc": "A bag containing enough medicine to heal wounds three times. Small and portable. Perfect for in-battle use.",
            "ItemType": "active",
            "ItemQuality": 1,
            "ItemTrigger": "", # KWARGS FORMAT: entity_hit, entity_attacker
            "ItemCallback": "medicinal_herb_bag",
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
    4: { # Secret Shop Pool (Some of the best items in the game)
        
    },
    5: { # Other: Fill later
        
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
        if item_id in item_data[item_pools].keys():
            return Item.copy(item_data[item_pools][item_id])
    if not got_it:
        input("ItemError: get_clone_by_name could not find item with given item ID")
        return Item.copy(item_data["no_equip"])

def give_player_item(item):
    print_with_conf(f"You obtained a(n) {item.ItemName}!")
    item_obtained = False
    for pc in GAME_STATE.player_party:
        if len(pc.Items) < 8 and not item_obtained:
            print_with_conf(f"{pc.Name} puts it in their inventory.")
            pc.Items.append(item)
            item_obtained = True
    if not item_obtained:
        print_with_conf("Khorynn puts it in the Stash.")
        GAME_STATE.bagged_items.append(item)
    item.obtained(pc)

def shop():
    os.system(CLEAR)
    if GAME_STATE.player_bought_something:
        print_with_conf("ORNALDO) Weren't you just here a second ago?")
        print_with_conf("ORNALDO) Nothing's changed about my stock right now, Khorynn. Come back later.")
        return
    print_with_conf("ORNALDO) Welcome to my emporium, Khroynn! Why don't you have a look-see at my wonderful wares?")
    items_available = []
    amount_of_items_to_buy = random.randrange(1,3)
    for item in range(amount_of_items_to_buy):
        item_to_present = random.choice(list(item_data[3].keys()))
        if item_to_present in items_available:
            pass
        else:
            items_available.append(Item.copy(item_data[3][item_to_present]))
    print("ORNALDO) Here's what I've got!")
    numbered_item = 0
    for item in items_available:
        numbered_item += 1
        min_cost = item.ItemQuality * 10
        max_cost = item.ItemQuality * 20
        item.ItemCost = random.randrange(min_cost, max_cost + 1)
        print(f"{numbered_item}: {item.ItemName}, costs {item.ItemCost} gold")
    print_with_conf("ORNALDO) Come on, these are wonderful deals! You couldn't get this quality anywhere else.\n")
    player_chose_item = False
    while not player_chose_item:
        cmd = input("(INPUT) Which numbered item would you like to buy? Input 'back' to exit the shop.   ")
        try:
            cmd = int(cmd)
            player_chose_item = True
        except ValueError:
            if cmd == "back":
                print_with_conf("ORNALDO) Aww, nothing caught your eye? My stock's always changing, you know! Come back later~!")
                GAME_STATE.player_bought_something = True
                return
            input("You inputted something other than a number! PLEASE only input a number!")
            player_chose_item = False

    cmd = 1 if cmd <= 0 else cmd
    cmd = len(items_available) if cmd > len(items_available) else cmd
    chosen_item = items_available[cmd - 1]
    if GAME_STATE.money < chosen_item.ItemCost:
        print_with_conf("ORNALDO) Oh, girl, you don't have enough money to buy that! Are you trying to con me?")
    else:
        conf = input(f"(INPUT Y/N) Are you sure you would like to buy the {chosen_item.ItemName} for {chosen_item.ItemCost} gold?")
        if conf == "y":
            GAME_STATE.money -= chosen_item.ItemCost
            GAME_STATE.bagged_items.append(chosen_item)
            print_with_conf(f"ORNALDO) Thank you for buying my {chosen_item.ItemName}!! Wonderful doing business with you as always, Khorynn.")
            GAME_STATE.player_bought_something = True
        else:
            return
    print_with_conf("ORNALDO) Come back when you have more money!")


