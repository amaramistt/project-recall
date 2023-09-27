# To-Do List
#
#    \/ THINGS TO ACTUALLY WORK ON RIGHT NOW \/
#
# 1) more items lmao
#
#    \/ DO AT SOME POINT LATER \/
#
# 1) Rework the structure of the game: Have 4 encounters of the same pool and finish with a boss
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
    cycle = 1
    GAME_STATE.floor = 1
    
    while not began:
        began = gamestate.title_screen()
    while began:
        if GAME_STATE.debug_mode:
            item_given = False
            while True:
                gamestate.rest_time()

        
        else:
            
            if cycle >= 5:
                if not battle.initiate_battle(floor, True):
                    began = False
                    continue
                GAME_STATE.floor += 1
                cycle = 1
                print_with_conf(f"Floor Increased to {GAME_STATE.floor}")
                continue
                
            if cycle == 1 and GAME_STATE.floor == 1:
                gamestate.clear_terminal()
                gamestate.load_cutscene(2)
                entity.party_place_handler()
                if not battle.initiate_battle(floor):
                    began = False
                    continue
                cycle += 1
                gamestate.clear_terminal()
                
            elif cycle == 2 and GAME_STATE.floor == 1:
                for guy in GAME_STATE.player_party:
                    entity.level_up(guy, 9)
                gamestate.clear_terminal()
                gamestate.run_cutscene(3)
                gamestate.rest_time()
                if not battle.initiate_battle(floor):
                    began = False
                cycle += 1
                    
            elif GAME_STATE.floor == 2:
                print_with_conf("Congratulations! You beat the game!")
                print_with_conf("That's all I have for now. Thanks for playing!")
                began = False
                continue
                
            else:
                for guy in GAME_STATE.player_party:
                    entity.level_up(guy, 10)
                gamestate.rest_time()
                if not battle.initiate_battle(floor):
                    began = False
                    continue
                if cycle <= 4:
                    cycle += 1


while __name__ == "__main__":
    main()
