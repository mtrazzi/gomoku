from abc import abstractmethod
import numpy as np
import os
import time
import copy

from core.board import Board
from core.heuristics import simple_heuristic
from core.player import Player
from core.utils import is_there_stones_around

class Agent(Player):
  """Class Agent. Abstract class for our gomoku bot.

  Parameters
  ----------
  stone: int
    The color of the stone of the Agent.
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
    The color of the stone of the Agent.
  depth: int
    The maximum depth of the tree for lookahead in the minimax algorithm.
  heuristic: string
    The heuristic used to evaluate nodes.
  max_top_moves: int
    Maximum number of moves checked with depth > 1.
  """
  def __init__(self, stone=1, depth=2, heuristic='simple', max_top_moves=4):
    super().__init__(stone)
    self.depth = depth
    self.heuristic = heuristic
    self.max_top_moves = max_top_moves

  def input(self, gh):
    # find the best candidates using a depth = 1 evaluation
    candidates = self.simple_evaluation(gh)
    # return the best move among the candidates using minimax with full depth
    return self.best_move(candidates)
  
  def simple_evaluation(self, game_handler):
    """Returns the best `max_top_moves` moves using depth = 1 evaluation.

    Parameters
    ----------
    game_handler: GameHandler
      The game handler corresponding to the current position.

    Return
    ------
    list: (int, int) list
      The list of coordinates of the best `max_top_moves` moves.
    """
    gh, size = game_handler, game_handler.size
    score_map = np.full((size, size), -np.inf)
    player = gh.players[gh.current]
    for x in range(size):
      for y in range(size):
        # only do moves that are near current stones
        if not is_there_stones_around(gh.board.board, x, y):
          score_map[x][y] = -np.inf
          continue
        # select top max_moves_checked moves with evaluation of depth one
        if gh.can_place(x, y, player):
          score_map[x][y] = self.eval(gh.board.board)

  def eval(self, node):
    """Evaluation function used for estimating the value of a node in minimax.

    Parameters
    ----------
    node: GameHandler
      The current node being evaluated (a.k.a. board position).
    player: Player
      The current player that is being evaluated.
    heuristic: string
      The heuristic used to evaluate nodes.

    Return
    ------
    value: int
      The estimated value of the current node (position) being evaluated.
    """
    if self.heuristic == 'simple':
      return simple_heuristic(node.board.board, self.stone)
    return 0

  def minimax(self, node, move, depth, max_player, alpha=-np.inf, beta=np.inf):
    """The minimax function returns a heuristic value for leaf nodes (terminal nodes and nodes at the maximum search depth). Non leaf nodes inherit their value from a descendant leaf node.

    Parameters
    ----------
    node: GameHandler
      The current node being evaluated (a.k.a. board position)
    move: int, int
      The last move being played in the position to be evaluated
    depth: int
      The maximum depth of the tree for lookahead in the minimax algorithm
    max_player: bool
      True if in recursion we're considering the position according to the original player making the move, False if we're considering the opponent.

    Return
    ------
    value: int
      The estimated value of the current node (position) being evaluated.
    """
    return 0

AGENTS = {
  "minmax": MiniMaxAgent,
  "random": RandomAgent
}
