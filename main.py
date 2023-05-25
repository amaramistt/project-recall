# To-Do List
#
#    \/ THINGS TO ACTUALLY WORK ON RIGHT NOW \/
# 1) Create a system in which passive, consumable, and non-consumable items can be seamlessly acquired and used
#    ^^^^^^^^^ IN DEVELOPMENT ^^^^^^^^^
# 2) Squash Bugs!!!
#
#    \/ DO AT SOME POINT LATER \/
#    



import os
import sys
import subprocess
import random
import copy
import entity
import item
import battle
import gamestate
from gamestate import GAME_STATE, print_with_conf

CLEAR = 'cls' if os.name == 'nt' else 'clear'

def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


def main():
    began = False
    run = 1
    
    while not began:
        began = gamestate.title_screen()
    while began:
        if not GAME_STATE.debug_mode:
            if run == 1:
                os.system(CLEAR)
                print_with_conf("Welcome to Project Recall!\nAt this moment, this game is mostly just a battle simulator.")
                print_with_conf("You will be presented with mutliple encounters, getting new party members and levelling up between fights.")
                print_with_conf("The party members you find are entirely randomized!\nMake sure to see what each class does in the tutorial if you haven't already.")
                print_with_conf("Have fun! <3")
                os.system(CLEAR)
                print_with_conf("You, Khorynn, stand before the entrance of a cave. It is a special cave, one that you have planned to explore for some time.")
                print_with_conf("Although the looming mouth of the cave is intimidating, you swallow your nerves and begin your expedition down.")
                print_with_conf("After a few twists and turns, you discover an incredibly red door labeled 'Olivia's Party Place' that, for good reason, catches your attention.")
                print_with_conf("Without really thinking about it too much, you open the door and are greeted by an eccentric woman who immediately introduces herself as Olivia.")
                print_with_conf("OLIVIA) Hey, love! I'm Olivia. You're the first honest-to-god customer I've had in a VERY long time. What's your name?")
                print_with_conf("KHORYNN) ...Khorynn.")
                print_with_conf("OLIVIA) Well, welcome to my Party Planning Place, Khorynn. Why're you here? Wait, let me guess--Trying to get to the bottom?")
                print_with_conf("KHORYNN) ...Yeah.")
                print_with_conf("OLIVIA) You're in luck! I've dedicated my entire life to helping adventurers like you meet with like-minded individuals and helping your journeys.")
                print_with_conf("OLIVIA) At my place, you can find more people to join your party and change one of your party member's jobs, letting them learn more skills!")
                print_with_conf("OLIVIA) I have locations all over the cave, so you'll be able to speak to me after each of your fights easily!")
                print_with_conf("KHORYNN) *How... how does she move between locations...????*")
                print_with_conf("KHORYNN) ...Thanks, Olivia. I'll use your services as much as I can.")
                print_with_conf("OLIVIA) Say, while you're here, why don't you sample my services? Let me give you my spiel...")
                os.system(CLEAR)
                
            elif run == 2:
                for guy in GAME_STATE.player_party:
                    entity.level_up(guy, 9)
                    
            elif run == 5:
                print_with_conf("Congratulations! You beat the game!")
                print_with_conf("That's all I have for now. Thanks for playing!")
                began = False
                break
                
            else:
                for guy in GAME_STATE.player_party:
                    entity.level_up(guy, 10)
            
            entity.party_place_handler(GAME_STATE.player_party)
            if not battle.initiate_battle(GAME_STATE.player_party, run):
                began = False
            if run <= 4:
                run += 1

        elif GAME_STATE.debug_mode:
            item.give_player_item(item.get_clone_by_name("MedeasBlessing"))
            item.give_player_item(item.get_clone_by_name("MedeasBlessing"))
            item.give_player_item(item.get_clone_by_name("SpikedArmor"))
            while True:
                print_with_conf("balls")
    



while __name__ == "__main__":
    main()
