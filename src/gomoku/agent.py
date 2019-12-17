import numpy as np

from gomoku.player import Player
from gomoku.rules import Rules


def is_node_terminal(gameHandler):
  end = Rules.check_winner(gameHandler.board, gameHandler.players)
  return end


class Node(object):
  def __init__(self, lower=-np.Inf, upper=np.Inf):
    self.lowerbound = lower
    self.upperbound = upper


class Agent(Player):
  """Class Agent. Abstract class for our gomoku bot.

  Parameters
  ----------
  color: int
    The color of the stone of the Agent.
  """
  def __init__(self, color):
    super().__init__(color)

  def find_move(self, gameHandler):
    """Returns best move (x, y) given current board position.

    Parameters
    ----------
    gameHandler: GameHandler
      The game handler corresponding to the current position.

    Return
    ------
    (x,y): (int, int)
      The best move according to Agent.
    """
    pass
