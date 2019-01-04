#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple battleship game

Simplfications

1. One player game - its just you and limited ammo
2. Battleships are limited to 1x1 

"""

from random import randint

UNKNOWN = 'O'
MISSED = 'X'
HIT = '*'


def load_title():
   print('\n***** BATTLESHIP ******')
   print('A simple 1-player game to locate randomly deployed 1x1 ships')
   print('Can you hit all battleships before your missiles run out?\n')
   print('***********************')


def setup_board(grid_size):
   """
   Initialises a board of ocean sectors '0' as a list of lists.
   Size is specified by grid_size.
   """
   board = []
   for x in range(grid_size):
      board.append([UNKNOWN] * grid_size)
      
   return board
        
   
def random_deployment(grid_size):
   """1
   Returns a uniformly distributed random number
   between 0 and grid_size - 1 representing a deployment of a Battleship
   """
   return randint(0, grid_size - 1)


def deploy_battleships(grid_size, n):
   """
   Randomly allocates n 1X1 battleships to a grid_size x grid_size grid of ocean sectors.
   There is no overlapping of battleships.
   """
   
   battleships = []
   for battleship in range(n):
      while True:
         bs_row = random_deployment(grid_size)
         bs_col = random_deployment(grid_size)
         
         if([bs_row, bs_col] not in battleships):
            battleships.append([bs_row, bs_col])
            break
      
   return battleships


 
def play_game(board, battleships, missiles=10): 
   '''
   Battleship game loop.
   
   Plays until all missiles are depleted or all battleships are sunk.
   
   Keyword arguments:

   board -- a list of lists.  Each list is a row on the board.
   battleships -- a list of lists.  Each list is a coordiate pair location of a bettleship
   missiles -- the number of missiles available (default = 10)
   '''
   #This would not be included in the shipped version of the game.  It is just there so we can test our code.
   print('DEBUG: Battleship locations are {0}\n'.format(battleships))

   for missile in range(missiles):
      show_board(board)
      print("Missile #{0} of {1}".format(missile + 1, missiles))

      coordinate = read_coordinate('Row, Col to target')
      
      if missile_on_target(battleships, coordinate):
         
         print("You sunk my Battleship!")
         record_hit(board, coordinate, battleships)
         
         if len(battleships) == 0:  
            print("You sunk all of my Battleships!")
            break
         
      elif missile_out_of_bounds(coordinate, grid_size):
         print("Sector is out of game play bounds")
      
      elif previously_targetted(coordinate):
         print("This sector of the ocean grid has already been targeted.")
      
      else:
         
         print("Missed")
         record_miss(board, coordinate)
     
     
      if missile == missiles - 1 :
         print("You have no more missiles.  You lose.  Game Over")
         print('Remaining enemy battleship locations were {0}\n'.format(battleships))



def show_board(board):
   '''
   Display the current state of the play board to the user
   
   Keyword arguments:
   board -- list of lists represesnting game board.
   '''
   for row in board:
      print("-".join(row))
      
      
      
def read_coordinate(prompt):
   '''
   Loops until valid input has been made to game.  
   Format is "1,2"
   
   Returns a coordinate to target on baord.
   
   Keyword arguments:
   prompt -- msg to user.
   '''
   
   coordinate = []
   
   while True:
      
      x = input("{0} >>> ".format(prompt))

      try:
         if len(x.split(',')) < 2:
            raise ValueError()
         else:
            
            coordinate = [int(i) for i in x.split(",")]
      except ValueError:
            
            print("Invalid input please input {0}".format(prompt))
            
      else:
         break

   return coordinate

def missile_on_target(battleships, coordinate):
    """
    Returns True/False indicating if a missile target contains a Battleship.
    """
    if coordinate in battleships:
        return True
    else:
        return False
     
      
def record_hit(board, coordinate, battleships):
   '''
   Update board with hit remove battleship
   
   Keyword arguments:
   board -- a list of lists.  Each list is a row on the board.
   coordinate -- list with 2 items [row, col]
   battleships -- a list of lists.  Each list is a coordiate pair location of a bettleship
   '''
   board[coordinate[0]][coordinate[1]] = HIT
   battleships.remove([coordinate[0], coordinate[1]])
   
def record_miss(board, coordinate):
   '''
   Update board with a miss
   
   Keyword arguments:
   board -- a list of lists.  Each list is a row on the board.
   coordinate -- list with 2 items [row, col]
   '''
   board[coordinate[0]][coordinate[1]] = MISSED

def missile_out_of_bounds(coordinate, grid_size):
   '''
   Returns boolean indicating if target is outside of the game play zone
   
   Keyword arguments:
   coordinate -- list with 2 items [row, col]
   grid_size -- size of the nXn game playing board
   '''
   return (coordinate[0] < 0 or coordinate[0] >= grid_size) or (coordinate[1] < 0 or coordinate[1] >= grid_size)


def previously_targetted(coordinate):
   '''
   Returns booleaning indicating if target has been hit by a missile previously
   
   Keyword arguments:
   coordinate -- list with 2 items [row, col]
   '''
   return (board[coordinate[0]][coordinate[1]] == MISSED or board[coordinate[0]][coordinate[1]] == HIT)



if __name__ == "__main__":
   grid_size = 10
   board = setup_board(grid_size)
   battleships = deploy_battleships(grid_size, 3)
   load_title()
   play_game(board, battleships, missiles = 2)
      