from abc import abstractmethod
import numpy as np
import os
import time
import copy

from core.clean.board import Board
from core.clean.heuristics import simple_heuristic
from core.clean.player import Player

class Agent(Player):
  """Class Agent. Abstract class for our gomoku bot.

  Parameters
  ----------
  stone: int
    The color of the stone of the Agent
  """
  def __init__(self, stone):
    super().__init__(stone)
  
  @abstractmethod
  def input(self, game_handler) -> (int, int):
    """Returns best move (x, y) given current board position.
    
    Parameters
    ----------
    game_handler: GameHandler
      The game handler corresponding to the current position.

    Return
    ------
    (x,y): (int, int)
      The best move according to Agent.
    """

class RandomAgent(Agent):
  """Class RandomAgent. Plays valid random moves.

  Parameters
  ----------
  stone: int
    The color of the stone of the Agent
  """
  def __init__(self, stone):
    super().__init__(stone)

  def input(self, game_handler):
    player = game_handler.players[game_handler.current]
    while True:
      size = game_handler.size
      x, y = np.random.randint(size), np.random.randint(size)
      if game_handler.can_place(x, y, player):
        break
    return x, y

class MiniMaxAgent(Agent):
  """Class MinMaxAgent. Apply the MiniMax algorithm (cf. https://en.wikipedia.org/wiki/Minimax#Pseudocode.)
  
  Parameters
  ----------
  stone: int
    The color of the stone of the Agent
  depth: int
    The maximum depth of the tree for lookahead in the minimax algorithm
  heuristic: string
    The heuristic used to evaluate nodes.
  """
  def __init__(self, stone=1, depth=0, heuristic='simple'):
    super().__init__(stone)
    self.depth = depth

  def input(self, game_handler):
    size = game_handler.size
    score_map = np.full((size, size), -np.inf)
    player = game_handler.players[game_handler.current]
    for x in range(size):
      for y in range(size):
        if game_handler.can_place(x, y, player):
          game_handler.do_move(x, y, player)
          score_map[x][y] = self.minimax(game_handler, self.depth, True)
          game_handler.undo_last_move(player)
    return np.unravel_index(np.argmax(score_map, axis=None), score_map.shape)

  def eval(self, node, heuristic='simple'):
    """Evaluation function used for estimating the value of a node in minimax
    
    Parameters
    ----------
    node: GameHandler
      The current node being evaluated (a.k.a. board position)
    heuristic: string
      The heuristic used to evaluate nodes.

    Return
    ------
    value: int
      The estimated value of the current node (position) being evaluated.
    """
    position = node.board.board
    if heuristic == 'simple':
      return simple_heuristic(position, self.stone)
    return 0
  
  def minimax(self, node, depth, maximizing_player):
    """The minimax function returns a heuristic value for leaf nodes (terminal nodes and nodes at the maximum search depth). Non leaf nodes inherit their value from a descendant leaf node.
    
    Parameters
    ----------
    node: GameHandler
      The current node being evaluated (a.k.a. board position)
    depth: int
      The maximum depth of the tree for lookahead in the minimax algorithm
    maximizing_player: bool
      True if in recursion we're considering the position according to the original player making the move, False if we're considering the opponent.

    Return
    ------
    value: int
      The estimated value of the current node (position) being evaluated.
    """
    if depth == 0 or node.is_done():
      return self.eval(node)
    if maximizing_player:
      value = -np.inf
      for child in node.child():
        value = max(value, self.minimax(child, depth - 1, False))
        return value
    else:
      value = np.inf
      for child in node.child():
        value = min(value, self.minimax(child, depth - 1, True))
      return value

AGENTS = {
  "minmax": MiniMaxAgent,
  "random": RandomAgent
}