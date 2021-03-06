#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Classic battleship game

Classes:

1. Game  -- contains main loop encapsulates player and enemy GameBoards (implements observerable interface)
2. GameBoard -- encapsulates a game board for either a player or computer
3. RandomDeployEngine -- Randomly deploys ships to ocean sectors
4. Battleship -- encapsulates the different classes of battleship
5. BattleshipTerminalView -- encapsulates a view of the game in the Terminal (observer pattern)
6. UserTargetController -- Terminal Interface for selecting targerts
7. RandomTargetController -- Encapsulates a random target selectio.  Same Interface as UserTargetController 

Beginnings of two player game... still WIP

Displays enemy and player board

"""


UNKNOWN = '.'
MISSED = 'X'
HIT = '*'

from random import randint
from copy import deepcopy
from colorama import Fore, Style
import colorama


class Game(object):
   """
   A game 'has-a' player GameBoard and a enemy GameBoard
   """
   
   def __init__(self, player_board, enemy_board):
      self.player_board = player_board
      self.enemy_board = enemy_board
      self._observers = []

   def register_observer(self, to_register):
      self._observers.append(to_register)
      
   def notify_observers(self, *args, **kwargs):
      for observer in self._observers:
         observer.notify(self, *args, *kwargs)
      
   def setup_board(self):
      self.enemy_board.deploy_battleships()
      self.player_board.deploy_battleships()
   
      self.enemy_board.unhide_ships() # debug!
      self.player_board.unhide_ships()
      
   '''
   def display_title(self):
      
      self._broadcast("BATTLESHIP")
   
   def display(self):
            
      enemy_board.display()
      player_board.display()
   '''
         

   def play(self):
      """
      Main game loop
      
      Computer and player take turns until someone sinks all of their
      opponents battleships
      
      The game then terminates.
      
      """
      
      player_target_controller = UserTargetController()
      #player_target_controller = RandomTargetController(self.enemy_board.grid_size)
      enemy_target_controller = RandomTargetController(self.enemy_board.grid_size)
      
      while self.enemy_board.battleships_remaining() > 0 and self.player_board.battleships_remaining() > 0:
            
         self.take_turn(enemy_board, player_target_controller)  # players turn
         self.take_turn(player_board, enemy_target_controller) # enemys turn
         self._broadcast("display_board", player_board, enemy_board)
      
      self._display_winner()
         
   
   def take_turn(self, board, target_controller): 
      '''
      Battleship game loop.
      
      Keyword arguments:
   
      board -- a GameBoard encapsulating one of the boards in play.
      '''
   
      #could be missiles per turn... instead.
      #the there is an outer loop that switches between the two players
      #basically all of the code below becomes take_turn
      #board becomes a class
      #board.

      #This is the bit that varies between player and enemy
      # parameter or encapsulate whole function?
      #coordinate = read_coordinate('Row, Col to target')
      #coordinate = random_shot(board.grid_size)
      coordinate = target_controller.select_target()
      
      hit, sunk = board.missile_on_target(coordinate)
      
      if hit:
         
         self._broadcast('hit')
         board.record_hit(coordinate)
         
         if sunk:  
            self._broadcast('sunk')

      elif board.missile_out_of_bounds(coordinate):
         self._broadcast('out_bounds')
         
      elif board.previously_targetted(coordinate):
         self._broadcast('gone')
         
      
      else:
         
         self._broadcast("miss")
         board.record_miss(coordinate)


   def _display_winner(self):
      if self.enemy_board.battleships_remaining() == 0:
         self._broadcast("You sunk all my battleships!  You WIN!")
      else:
         self._broadcast("The enemy has sunk all of your battleships. You lose!")
         
   def _broadcast(self, *args):
      for observer in self._observers:
         kwargs = {}
         observer.notify(self, *args, **kwargs)
         
      
     


class BattleshipTerminalView(object):
   """
   Encapsulates a view of the Battleship game in the Terminal
   """
   
   def __init__(self, observable):
      observable.register_observer(self)
   
   def notify(self, observerable, *args, **kwargs):
      if len(args) > 0:
         
         msg = args[0].lower()
         
         if msg== 'hit':
            print(f'{Style.BRIGHT}{Fore.YELLOW}Hit!{Style.RESET_ALL}')
         elif msg == 'sunk':
            print(f"{Style.BRIGHT}{Fore.GREEN}You sunk my Battleship!{Style.RESET_ALL}")
         elif msg == 'out_bounds':
            print(f"{Style.BRIGHT}{Fore.RED}Sector is out of game play bounds{Style.RESET_ALL}")
         elif msg == "gone":
            print("This sector of the ocean grid has already been targeted.")
         elif msg == 'miss':
            print("Missed")
         elif msg == 'display_board':
            player_board = args[1]
            enemy_board = args[2]
            self._show_board("ENEMY", enemy_board.board)
            self._show_board("PLAYER", player_board.board)
         else:
            print(msg)
         

   def _show_board(self, name, board):
      
      headers = [str(i) for i in range(len(board))] 
      blanks = [' ' for i in range(len(board))]
      
      to_view = deepcopy(board)
   
      for row in range(len(to_view)):
         to_view[row].insert(0, headers[row]+'\t')
      
      headers.insert(0, name + '\t')
      blanks.insert(0, ' \t')
      to_view.insert(0, blanks)
      to_view.insert(0, headers)
      
      
      for row in range(len(to_view)):
            print(' '.join(to_view[row]))  

   def display_title(self):
      print(f"\n{Style.BRIGHT}{Fore.GREEN}BATTLESHIP!{Style.RESET_ALL}")

      
class UserTargetController(object):
   
   def __init__(self):
      pass
      
   def select_target(self):
      return read_coordinate('Row, Col to target')
   



class RandomTargetController(object):
   
   def __init__(self, grid_size):
      self.grid_size = grid_size
   
   def select_target(self):
      return random_shot(self.grid_size)


class RandomDeployEngine(object):
   """
   Encapsulates logic to deploy ships randomly on a
   n X n board.
   
   Key method is deploy()
   """
   
   def __init__(self, ship_sizes, grid_sizes):
      self.ship_sizes = ship_sizes
      self.grid_size = grid_sizes

   def deploy(self):
      """
      
      Returns a List of Battleships
      
      Randomly distribute ships on a board of grid_size X grid_size
      
      Trys until there is no overlap between ships

      """
      battleships = []
      
      #largest ships placed first
      ship_sizes.sort(reverse=True)
      
      for ship_size in self.ship_sizes:
         
         while True:
         
            start_row = self._random_location(self.grid_size, ship_size)
            start_col = self._random_location(self.grid_size, ship_size)
            
            if self._random_vertical_orientation():
               #vertical orientation
               end_row = start_row
               end_col = start_col + ship_size - 1
            else:
               #vertical orientation
               end_row = start_row + ship_size - 1
               end_col = start_col 
            
            to_add = Battleship([start_row, start_col], [end_row, end_col])
            
            if self._deploy_battleship(battleships, to_add):
               break
            
      return battleships
   
   def _random_location(self, grid_size, ship_size):
      """1
      Returns a uniformly distributed random number
      between 0 and grid_size - 1 representing a deployment of a Battleship
      """
      return randint(0, grid_size - 1 - ship_size) 

   def _random_vertical_orientation(self):
      """
      Returns True = vertical orientation
      Returns False = horizontal orientation
      """
      if randint(1, 10) >= 5:
         return True
      else:
         return False
      
      
   def _deploy_battleship(self, battleships, to_add):
       """
       Attempts to add a battleship to the list of battleships
       Reject to to_add Battleship if there is an overlap with 
       existing battleships
       """
       if len(battleships) == 0:
           battleships.append(to_add)
           print("added")
       else:
           for bs in battleships:
               if(bs.coordinates_overlap(to_add.coordinates)):
                   print("could not add")
                   return False
           
           print("added")
           battleships.append(to_add)
       
       return True   
      

class GameBoard(object):
   """
   Encapsulates a game board (e.g. for player 1 or the enemy)
   
   A game board has size grid_size X grid_size 
   A game board 'has-a' deploymenet engine to deploy ships at sea
   
   A game interacts with a game board by checking 
   1. If a missile hits a battleship
   2. If a missile is out of bounds
   3. If a missle hits a previously targeted ocean sector
   4. Mark an ocean sector has direct hit
   5. Mark an ocean sector as a miss
   6. Unhide battleships when displaying
   7. Request that gameboard is displayed
   
   Implements Observable interface
   register_observer(observer)
   notify_observers(observable, *args, **kwargs)
   
   """
   def __init__(self, grid_size, deploy_engine, name='PLAYER'):

      self.board = []
      self.battleships = []
      self.grid_size = grid_size
      self.deploy_engine = deploy_engine
      self.name = name
      self._observers = []
      
      self._init_board(self.board, self.grid_size)
      
      
   def _init_board(self, board, grid_size):
      """Initialises a board of ocean sectors '0' as a list of lists.
      Size is specified by grid_size."""
      
      for x in range(grid_size):
         board.append([UNKNOWN] * grid_size)
         
   def register_observer(self, observer):
      self._observers.append(observer)
 
   def notify_observers(self, *args, **kwargs):
      for observer in self._observers:
         observer.notify(self, *args, **kwargs)   
   
   def deploy_battleships(self):
      self.battleships = self.deploy_engine.deploy()
   
   def battleships_remaining(self):
      return len(self.battleships)
   
   def unhide_ships(self):
      ship_index = 0
      for ship in self.battleships:
         ship_index += 1
         for coordinate in ship.coordinates:
            self.board[coordinate[0]][coordinate[1]] = str(ship_index)
            

   def missile_on_target(self, coordinate):
      
      hit = False
      sunk = False
      
      for i in range(len(self.battleships)):
         
         if self.battleships[i].missile_hits(coordinate[0], coordinate[1]):
            
            hit = True
            
            if self.battleships[i].sunk():
               del self.battleships[i]
               sunk= True
               
            break
         
      return hit, sunk
   
   
   def record_hit(self, coordinate):
      '''
      Update board with hi
      
      Keyword arguments:
      coordinate -- list with 2 items [row, col]
      '''
      self.board[coordinate[0]][coordinate[1]] = HIT # f'{Style.BRIGHT}{Fore.GREEN}' + HIT + f'{Style.RESET_ALL}'
      
      
   def record_miss(self, coordinate):
      '''
      Update board with a miss
      
      Keyword arguments:
      coordinate -- list with 2 items [row, col]
      '''
      self.board[coordinate[0]][coordinate[1]] = MISSED
      
   
   def missile_out_of_bounds(self, coordinate):
      '''
      Returns boolean indicating if target is outside of the game play zone
      
      Keyword arguments:
      coordinate -- list with 2 items [row, col]
      '''
      return (coordinate[0] < 0 or coordinate[0] >= self.grid_size) or (coordinate[1] < 0 or coordinate[1] >= self.grid_size)
   
   
   def previously_targetted(self, coordinate):
      '''
      Returns booleaning indicating if target has been hit by a missile previously
      
      Keyword arguments:
      coordinate -- list with 2 items [row, col]
      '''
      return (self.board[coordinate[0]][coordinate[1]] == MISSED or self.board[coordinate[0]][coordinate[1]] == HIT)


            




class Battleship(object):
    """
    Represents a 1 x n or n X 1 battleship.
    The battleship can be targetted and destroyed.
    """
    def __init__(self, start, end):
        """
        Constructor method
        
        Keyword argument:
        start -- list of length 2. row, col coordinates of start of ship
        end -- list of ength 2. row, col coordinates of end of ship
        """
        self.coordinates = []
        self.set_coordinates(start, end)
    
    def set_coordinates(self, start, end):
        """
        Store all coordinates that the ship occupies.  Assume width of 1.
        
        Keyword argument:
        start -- list of length 2. row, col coordinates of start of ship
        end -- list of ength 2. row, col coordinates of end of ship
        """
        if start[0] == end[0]:
            self.coordinates = [[start[0], x] for x in range(start[1], end[1]+1)]
            #to see the list of coordinates generated by the comprehension          
            print(self.coordinates)
        else:
            self.coordinates = [[x, start[1]] for x in range(start[0], end[0]+1)]
            print(self.coordinates)
   
    def coordinate_overlap(self, coordinate):
        """Returns True/False is coordinate list [x,y] overlaps
        with the battleships coordinates
        
        Keyword arguments:
        coordinate - [row, col] list to check for overlap with ship
           
           """ 
        return coordinate in self.coordinates             
        
        
    def coordinates_overlap(self, coordinates):
        """
        Checks for an overlap in a list of coordinate pairs
        and the the coordinates of this battleship
        """
        for c in coordinates:
            if c in self.coordinates:
                return True
        
        return False
        
    def missile_hits(self, target_row, target_col):
        """
        Is the missle on target?  Does it hit the battleship?
        Returns True or False
        """
        if self.coordinate_overlap([target_row, target_col]):
            
            self.coordinates.remove([target_row, target_col])
            #for debug - we can see that hit coordinate pair has been removed. 
            print(self.coordinates)
            return True
        else:
            return False

            
    def sunk(self):
        return len(self.coordinates) == 0 
        
    




         
#functions to incorporate into gmae class later on?
def random_shot(grid_size):
   """
   Returns a uniformly distributed random number
   between 0 and grid_size - 1 representing a deployment of a Battleship
   """
   return [randint(0, grid_size - 1), randint(0, grid_size - 1)]    
      
      
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






if __name__ == "__main__":
   
   #colorama.init()  # for somoe reason this slows the code substantially?!!
   
   #game is played on a n X n grid of size   
   grid_size = 10
  
   #enemy ships sizes
   ship_sizes = [5, 4, 3, 3, 2]
   
   #new code using GameBoard object
   player_board = GameBoard(grid_size, RandomDeployEngine(ship_sizes, grid_size))
   enemy_board = GameBoard(grid_size, RandomDeployEngine(ship_sizes, grid_size), name='ENEMY')
   
   game = Game(player_board, enemy_board)
   
   view = BattleshipTerminalView(game)
   
   game.setup_board()
   view.display_title()
   
   game.play()
   
   #colorama.deinit()
   
  
   
      
   
   
   
