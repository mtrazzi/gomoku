import time

from gomoku.agent import Agent
from gomoku.agents import MiniMaxAgent
from gomoku.rules import Rules
from gomoku.utils import is_there_stones_around


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
  size: int (Default: 19)
    Size of the board

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
  turn: int
    Current In-game turn
  winner: Player
    Player who won
  helpAgent: Agent
    Agent who predict the next move if we need help
  """
  def __init__(self, board, players, script=None, size=19):
    self.board = board
    self.players = players
    self.script = script
    self.size = size

    self.current = 0
    self.error = ""
    self.capture_history = []
    self.move_history = []
    self.state_history = []
    self.turn = 1
    self.winner = None
    self.helpAgent = MiniMaxAgent()
    self.begin = -1

  def restart(self):
    """Reset all attributes to their initial states"""
    self.board.restart()
    self.players[0].captures = 0
    self.players[0].last_move = (-2, -2)
    self.players[0].aligned_five_prev = False
    self.players[1].captures = 0
    self.players[1].last_move = (-2, -2)
    self.players[1].aligned_five_prev = False
    if self.script:
      self.script.restart()

    self.current = 0
    self.error = ""
    self.capture_history = []
    self.move_history = []
    self.state_history = []
    self.turn = 1
    self.winner = None
    self.begin = -1
    return self

  def start(self):
    """Main Function, run the game"""
    print(self)
    while 1:
      player = self.players[self.current]

      self.begin = time.time()
      if isinstance(player, Agent):
        move = player.find_move(self)
      elif not self.script or not self.script.running():
        move = player.get_move()
      else:
        move = self.script.get_move()
        print(f"Player {player.color}: {move[0] + 1, move[1] + 1}")
      if len(move) == 0:
        return

      self.play(move)
      if self.winner:
        print(self)
        print(f"P{self.winner.color} won.")
        return

      if self.script and self.script.running():
        time.sleep(0.25)
    return

  def play(self, move):
    """Try to play the given move.

    Parameters
    ----------
    move: tuple, 2d-array
      The intersection where we want to play (x, y)

    Return
    ------
    succed: bool
      True if we can play at this intersection, else False
    """
    player = self.players[self.current]

    if not self.can_place(*move, player):
      return False
    self.do_move(move, player)

    self.turn += 1

    self.winner = Rules.check_winner(self.board, self.players)
    self.current = (self.current + 1) % 2

    print(self)
    return True

  def move_help(self):
    """Return the best predicted move for the player"""
    return self.helpAgent.find_move(self)

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
    if (x < 0 or x >= self.board.size or y < 0 or y >= self.board.size or not
        self.board.is_empty(x, y)):
      self.error = f"\033[1;31mIntersection must be empty (\'.\' or *)\033[0m"
      return False
    player.last_move = (x, y)

    self.board.place(x, y, player.color)
    if not Rules.no_double_threes(self.board, player):
      self.board.remove(x, y)
      self.error = f"\033[1;31mNo double free-threes allowed\033[0m"
      return False
    self.board.remove(x, y)
    return True

  def do_move(self, move, player):
    self.state_history.append([player.last_move,
                               player.captures,
                               player.aligned_five_prev])
    self.board.place(*move, player.color)
    player.last_move = move
    self.move_history.append(move)
    self.capture_history.append(Rules.capture(self.board, player))
    return True

  def undo_move(self):
    x, y = self.move_history.pop()
    previous_dead = self.capture_history.pop()
    last_move, captures, aligned_five_prev = self.state_history.pop()
    stone = self.board.board[x][y]
    player = self.players[0 if stone == 1 else 1]
    opponent = self.players[1 if stone == 1 else 0]
    self.board.remove(x, y)
    for x, y in previous_dead:
      self.board.place(x, y, opponent.color)
    player.last_move = last_move
    player.captures = captures
    player.aligned_five_prev = aligned_five_prev
    return self

  def child(self, player):
    """
    List all the possible gamehandlers that could result from the current board
    with current player being player

    Parameters
    ----------
    player: Player
      Current Player

    Return
    ------
    children: list
      List of coordinates that are legal move from current position
    """
    children = []
    for x in range(self.size):
      for y in range(self.size):
        if not is_there_stones_around(self.board.board, x, y):
          continue
        if self.can_place(x, y, player):
          children.append((x, y))
    return children

  def __str__(self):
    player = self.players[self.current]

    representation = f"\033[2J\033[H{self.board}"
    representation += f"X: {self.players[0].captures} stone captured\n"
    representation += f"O: {self.players[1].captures} stone captured\n"
    if self.begin > 0:
      representation += f"Last move took {time.time() - self.begin}s\n"
    if len(self.error) != 0 and isinstance(player, Agent):
      representation += f"{self.error}"
    self.error = ""
    return representation
