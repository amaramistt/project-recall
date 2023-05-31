# To-Do List
#
#    \/ THINGS TO ACTUALLY WORK ON RIGHT NOW \/
#
# 1) Have enemies provide unique EXP and gold rewards that are provided after winning a battle
#
#
#    \/ DO AT SOME POINT LATER \/
#    
# 1) Implement Ornaldo's Shop
#
# 2) Rework the structure of the game: Have 4 encounters of the same pool and finish with a boss
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
        if GAME_STATE.debug_mode:
            GAME_STATE.money = 10000000
            item.buy_thing_for_money()
            print_with_conf("balls")
        else:
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
                entity.party_place_handler()
                if not battle.initiate_battle(run):
                    began = False
                run += 1
                os.system(CLEAR)
                
            elif run == 2:
                for guy in GAME_STATE.player_party:
                    entity.level_up(guy, 9)
                os.system(CLEAR)
                print_with_conf("In the aftermath of the battle, gathering your bearings, you notice a bright yellow door behind a corner.")
                print_with_conf("Music blares from inside so loudly that the thick stone walls of the cave can't drown it out.")
                print_with_conf("The door slams open! You ready yourself for battle as a slightly chubby middle-aged man appears.")
                print_with_conf("The man dashes towards you, shouting in disbelief and wonder!\n")
                print_with_conf("STRANGE MAN) Oh! Oh, ho ho! Wow! You're real, right? I'm not seeing things again, right?!")
                print_with_conf("KHORYNN) ...What?")
                print_with_conf("STRANGE MAN) OH! She speaks! Hello, customer! My name is Ornaldo!")
                print_with_conf("KHORYNN) ...Nice to meet you?")
                print_with_conf("ORNALDO) It is MORE nice to meet YOU! I run a shop in this cave. The most locations out of any shop here!")
                print_with_conf("KHORYNN) ...Really? Can I find you anywhere?")
                print_with_conf("ORNALDO) Absolutely anywhere!")
                print_with_conf("ORNALDO) If you aren't getting attacked by monster, there is a shop within 30 seconds of your location.")
                print_with_conf("KHORYNN) Convenient.")
                print_with_conf("ORNALDO) You can say that again!")
                print_with_conf("ORNALDO) My stock is super diverse as well! I sell everything from weapons to armor to supplies.")
                print_with_conf("ORNALDO) If you ever have extra gold to spend, come to one of my 3,174 locations in the cave!")
                print_with_conf("ORNALDO) What is your name, by the way?")
                print_with_conf("KHROYNN) ...Khorynn.")
                print_with_conf("ORNALDO) Very nice name, Khorynn.")
                print_with_conf("ORNALDO) I'm sure we will come to many mutually beneficial business transactions! Goodbye!")
                print_with_conf("\nOrnaldo dashes back into his shop with a hearty laugh.")
                print_with_conf("That interaction leaves you confused, but interested.")
                print_with_conf("Whenever you have a break, it would be wise to check Ornaldo's shop.")
                gamestate.rest_time()
                if not battle.initiate_battle(run):
                    began = False
                run += 1
                    
            elif run == 5:
                print_with_conf("Congratulations! You beat the game!")
                print_with_conf("That's all I have for now. Thanks for playing!")
                began = False
                break
                
            if run != 1:
                for guy in GAME_STATE.player_party:
                    entity.level_up(guy, 10)
                gamestate.rest_time()
                if not battle.initiate_battle(run):
                    began = False
                if run <= 4:
                    run += 1
    
    



while __name__ == "__main__":
    main()
