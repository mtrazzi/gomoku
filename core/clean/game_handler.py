import time
import copy

from core.clean.bot import Agent

class GameHandler(object):
  """Class GameHandler

  Parameters
  ----------
  board: Board
    The board
  players: list
    List of Players OR Bot
  rules: Rules
    The rules to respect
  script: Script (Default: None)
    Script to run

  Attributes
  ----------
  current: int
    The current player who need to make a move
  error: str
    Error string
  capture_history: list
    List of coordinates of captured stones.
  move_history: list
    List of corrdinates of done moves
  size: int
    Size of the board
  """
  def __init__(self, board, players, rules, mode, script=None, size=19):
    self.board = board
    self.players = players
    self.rules = rules
    self.mode = mode
    self.script = script
    self.current = 0
    self.error = ""
    self.capture_history = []
    self.move_history = []
    self.size = size

  def start(self):
    """Main Function, run the game"""
    while 1:
      player = self.players[self.current]
      print(self)

      if isinstance(player, Agent):
        move = player.input(self)
      elif not self.script or not self.script.running():
        move = player.input()
      else:
        move = self.script.input()
        print(f"{move[0] + 1, move[1] + 1}")

      if len(move) == 0:
        return

      if self.can_place(*move, player):
        self.do_move(move[0], move[1], player)
        winner = self.rules.check_winner(self.board, self.players)
        if winner:
          print(self)
          print(f"Player {winner.stone} won.")
          return
        self.current = (self.current + 1) % 2
        time.sleep(0.25)
    return

  def can_place(self, x, y, player):
    """See if player can place stone at emplacement (x, y)

    Parameters
    ----------
    x, y: int
      Coordinates
    player: Player
      Current Player

    Return
    ------
    succeed: bool
      True if we can place the stone else False
    """
    if x < 0                or y < 0                \
    or x >= self.board.size or y >= self.board.size \
    or not  self.board.is_empty(x, y):
      self.error = f"\033[1;31mIntersection must be empty (\'.\' or *)\033[0m"
      return False

    self.board.place(x, y, player)
    if not self.rules.no_double_threes(self.board, player):
      self.board.remove(x, y)
      self.error = f"\033[1;31mNo double free-threes allowed\033[0m"
      return False
    self.board.remove(x, y)
    return True
  
  def do_move(self, x, y, player):
    """Place stone at emplacement (x, y)

    Parameters
    ----------
    x, y: int
      Coordinates
    player: Player
      Current Player
    """
    self.board.place(x, y, player)
    player.last_move = (x, y)
    self.move_history.append((x, y))
    self.capture_history.append(self.rules.capture(self.board, player))
  
  def undo_last_move(self, player):
    """Undo previous move from player

    Parameters
    ----------
    player: Player
      Current Player
    """
    x, y = self.move_history.pop()
    previous_dead = self.capture_history.pop()
    self.board.remove(x, y)
    opponent = self.players[1 - self.players.index(player)]
    for (x_0, y_0) in previous_dead:
      self.board.place(x_0, y_0, opponent)
  
  def child(self, player):
    """
    List all the possible gamehandlers that could result from the current board with current player being player

    Parameters
    ----------
    player: Player
      Current Player
    
    Return
    ------
    l: list
      List of gamehandlers that are one legal move from current position
    """
    l = []
    for x in range(self.size):
      for y in range(self.size):
        if self.can_place(x, y, player):
          new_gh = copy.deepcopy(self)
          new_gh.do_move(x, y)
          l.append(new_gh)
    return l

  def __str__(self):
    representation =  f"\033[2J\033[H{self.board}"
    representation += f"X: {self.players[0].captures} stone captured\n"
    representation += f"O: {self.players[1].captures} stone captured"
    if len(self.error) != 0:
      representation += f"\n{self.error}"
    self.error = ""
    return representation
