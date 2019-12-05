import time

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
  """
  def __init__(self, board, players, rules, script=None):
    self.board = board
    self.players = players
    self.rules = rules
    self.script = script
    self.current = 0
    self.error = ""

  def start(self):
    """Main Function, run the game"""
    while 1:
      player = self.players[self.current]
      print(self)

      if not self.script or not self.script.running():
        move = player.input()
      else:
        move = self.script.input(player)

      if len(move) == 0:
        return

      if self.place(*move, player):
        self.rules.capture(self.board, player)
        winner = self.rules.check_winner(self.board, self.players)
        if winner:
          print(self)
          print(f"Player {winner.stone} won.")
          return
        self.current = (self.current + 1) % 2
        time.sleep(0.1)
    return

  def place(self, x, y, player):
    """Try to place player stone at emplacement (x, y)

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
    player.last_move = (x, y)

    self.board.place(x, y, player)
    if not self.rules.no_double_threes(self.board, player):
      self.board.remove(x, y)
      self.error = f"\033[1;31mNo double free-threes allowed\033[0m"
      return False
    return True

  def __str__(self):
    representation =  f"\033[2J\033[H{self.board}"
    representation += f"X: {self.players[0].captures} stone captured\n"
    representation += f"O: {self.players[1].captures} stone captured"
    if len(self.error) != 0:
      representation += f"\n{self.error}"
    self.error = ""
    return representation
