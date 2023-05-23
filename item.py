import os
import copy
import random
import entity
import battle
import gamestate
from entity import Entity
from gamestate import GAME_STATE



class Item(object):
    def __init__(self, template):
        self.ItemType = template["ItemType"]
        self.ItemQuality = template["ItemQuality"]
        self.ItemCallback = template["ItemCallback"]
        self.ItemTrigger = template["ItemTrigger"]
        self.ItemName = template["ItemName"]
        self.ItemDesc = template["ItemDesc"]
        if self.ItemType == "equip":
            self.ItemSubtype = template["ItemSubtype"]
            self.ItemStats = template["ItemStats"]
            
    def obained(self, character):
        if self.ItemType == "passive":
            gamestate.add_callback(self.ItemTrigger, self.ItemCallback)
            GAME_STATE.passives.append(self)
        gamestate.run_callbacks("callback_item_pickup", entity_picking_up = character, item_picking_up = self)

    def equip(self, character):
        if self.ItemType != "equip":
            return
            
        if self in character.Items:
            if self.ItemSubtype == "weapon":
                if character.EquippedWeapon is not None:
                    gamestate.remove_callback(character.EquippedWeapon.ItemTrigger, character.EquippedWeapon.ItemCallback)
                    print_with_conf(f"{character.EquippedWeapon.ItemName} was unequipped!")                    
                character.EquippedWeapon = self
                gamestate.add_callback(character.EquippedWeapon.ItemTrigger, character.EquippedWeapon.ItemCallback)
                print_with_conf(f"{character.Name} equipped {self.ItemName}!")                
                
            elif self.ItemSubtype == "armor":
                if character.EquippedArmor is not None:
                    gamestate.remove_callback(character.EquippedArmor.ItemTrigger, character.EquippedArmor.ItemCallback)
                    print_with_conf(f"{character.EquippedArmor.ItemName} was unequipped!")                    
                character.EquippedArmor = self
                gamestate.add_callback(character.EquippedArmor.ItemTrigger, character.EquippedArmor.ItemCallback)
                print_with_conf(f"{character.Name} equipped {self.ItemName}!")                
                
            elif self.ItemSubtype == "accessory":
                if character.EquippedAccessories[1] is not None:
                    gamestate.remove_callback(character.EquippedAccessories[1].ItemTrigger, character.EquippedAccessories[1].ItemCallback)
                    print_with_conf(f"{character.EquippedAccessories[1].ItemName} was unequipped!")
                character.EquippedAccessories[1] = character.EquippedAccessories[0]
                character.EquippedAccessories[0] = self
                print_with_conf(f"{character.Name} equipped {self.ItemName}!")
                gamestate.add_callback(character.EquippedAccessories[0].ItemTrigger, character.EquippedAccessories[0].ItemCallback)
                
        character.calc_equipment_stats()

    def __repr__():
        return f"{self.ItemName}"

            
item_data = {
    1: { # Boss Drop Pool (standard item pool)
        "SpikedArmor": {
            "ItemName": "Spiked Armor",
            "ItemDesc": "Plated armor with dangerous spikes protruding out everywhere. Hurts assailants that attempt to hit the wearer for physical damage.",
            "ItemType": "equip",
            "ItemSubtype": "armor",
            "ItemQuality": 1,
            "ItemTrigger": "callback_pc_is_hit", # KWARGS FORMAT: entity_hit, entity_attacker
            "ItemCallback": "spiked_armor",
            "ItemStats": {
                "Max HP": 0,
                "Max MP": 0,
                "STR": 0,
                "RES": 10,
                "MND": 0,
                "AGI": 0
            },
        },
        "MedeasBlessing": {
            "ItemName": "Medea's Blessing",
            "ItemDesc": "Brooch with the Consecration of Medea carved into it. The wearer feels more mindful while wearing it and might cast a spell twice in a row.",
            "ItemType": "equip",
            "ItemSubtype": "accessory",
            "ItemQuality": 2,        
            "ItemCallback": "medeas_blessing",
            "ItemStats": {
                "Max HP": 0,
                "Max MP": 0,            
                "STR": 0,
                "RES": 0,
                "MND": 20,
                "AGI": 0
            },
        },
        "MedeasCurse": {
            "ItemName": "Medea's Curse",
            "ItemDesc": "A fractured brooch that used to inscribe the Consecration of Medea. The wearer feels more violent while wearing it and gets twice as strong while bloodthirsty.",
            "ItemType": "equip",
            "ItemSubtype": "accessory",
            "ItemQuality": 2,   
            "ItemCallback": "medeas_curse",
            "ItemStats": {
                "Max HP": 0,
                "Max MP": 0,            
                "STR": 10,
                "RES": 0,
                "MND": 0,
                "AGI": 10
            },
        },
    },
    2: { # Item Room Pool (Higher than standard: Item rooms are not guaranteed)
        
    },
    3: { # Ornaldo's Shop Pool (A little higher than standard: These cost money)
        
    }
}

def get_item_data_map():
    return item_data

def present_player_item(item_pool = 1):
    print_with_conf("You find a treasure chest near the boss's corpse!")
    print_with_conf("You reach inside...")
    random_item_from_pool = random.choice(item_data[item_pool].keys())
    item = Item(item_data[item_pool][random_item_from_pool])
    print_with_conf(f"You found a(n) {item.Name}!")
    counter = 0
    item_obtained = False
    for pc in GAME_STATE.player_party:
        counter += 1
        if len(pc.Items) < 8 and not item_obtained:
            print_with_conf(f"{pc.Name} puts it in their inventory.")
            pc.Items.append(item)
            item_obtained = True
            character_who_got_item = pc
        if counter == len(pc):
            if not item_obtained:
                print_with_conf("Khorynn puts it in the Stash.")
                GAME_STATE.bagged_items.append(item)
    item.obtained(pc)



def spiked_armor(entity_hit, entity_attacker, damage_dealt):
    if entity_hit.EquippedArmor is not None:
        if entity_hit.EquippedArmor.ItemCallback == "spiked_armor":
            damage_to_deal = int(damage_dealt*0.2)
            print_with_conf(f"{enitity_attacker} gets hurt by {entity_hit.Name}'s Spiked Armor!'")
            entity_attacker.HP -= damage
            gamestate.run_callbacks("callback_entity_is_hit", entity_hit=target, entity_attacker=character, player_party=player_party, enemy_party=enemy)
            gamestate.run_callbacks("callback_enemy_is_hit", entity_hit=target, entity_attacker=character, player_party=player_party, enemy_party=enemy)

            if entity_attacker.HP <= 0:
                print_with_conf(f"{entity_attacker.Name} has fallen!")
                gamestate.run_callbacks("callback_entity_is_dead", entity_dead=entity_attacker, entity_attacker=entity_hit)
                gamestate.run_callbacks("callback_enemy_is_dead", entity_dead=target, entity_attacker=entity_hit)
                turn_order.remove(target)
                enemy.remove(target)

