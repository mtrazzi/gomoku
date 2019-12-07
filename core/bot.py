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
  def __init__(self, stone=1, depth=2, heuristic='simple', max_top_moves=5):
    super().__init__(stone)
    self.depth = depth
    self.heuristic = heuristic
    self.max_top_moves = max_top_moves

  def input(self, gh):
    # Estimate moves using a depth = 1 evaluation
    score_map = self.simple_evaluation(gh)
    # Find the list of best moves using this score map
    candidates = self.best_moves(score_map)
    # estimate the value of those candidates using minimax at full depth
    values = [self.minimax(gh, coord, self.depth, True) for coord in candidates]
    # return the best candidate
    return candidates[np.argmax(values)]
  
  def simple_evaluation(self, game_handler):
    """Returns a score map for possible moves using a depth = 1 evaluation.

    Parameters
    ----------
    game_handler: GameHandler
      The game handler corresponding to the current position.

    Return
    ------
    score_map: numpy.ndarray
      For each coordinate, its depth = 1 evaluation.
    """
    gh, size = game_handler, game_handler.size
    score_map = np.full((size, size), -np.inf)
    player = gh.players[gh.current]
    # opponent = gh.players[1 - gh.current]
    for x in range(size):
      for y in range(size):
        # only do moves that are near current stones
        if not is_there_stones_around(gh.board.board, x, y):
          score_map[x][y] = -np.inf
          continue
        # select top max_moves_checked moves with evaluation of depth one
        if gh.can_place(x, y, player):
          score_map[x][y] = self.minimax(gh, (x,y), 0, False)
    return score_map
  
  def best_moves(self, score_map):
    """Returns the top `max_top_moves` moves according to the score map.

    Parameters
    ----------
    score_map: numpy.ndarray
      For each coordinate, its depth = 1 evaluation.

    Return
    ------
    top_move_list: (int, int) list
      The list of coordinates of the best `max_top_moves` moves.
    """
    top_move_list = []
    for _ in range(self.max_top_moves):
      x_max, y_max = np.unravel_index(np.argmax(score_map, axis=None),                                          score_map.shape)
      top_move_list.append((x_max, y_max))
      score_map[x_max][y_max] = -np.inf
    return top_move_list

  def eval(self, position, color_to_move, max_player):
    """Evaluation function used for estimating the value of a node in minimax.

    Parameters
    ----------
    node: numpy.ndarray
      The current board position being evaluated.
    color_to_move: int
      Stone color of the player that will play next (1 for black, 2 for white).

    Return
    ------
    value: int
      The estimated value of the current node (position) being evaluated.
    """
    if self.heuristic == 'simple':
      return simple_heuristic(position, color_to_move, max_player)
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
    # current player depends on the index of max. player and if we're maximizing
    player = node.players[(node.current + (1 - max_player)) % 2]
    opponent = node.players[(node.current + max_player) % 2]
    # start your estimation of the move by doing the move
    node.do_move(move[0], move[1], player)
    if depth == 0:
      val = self.eval(node.board.board, opponent.stone, max_player)
    else:
      # using a sign to avoid two conditions in minimax
      sign = -1 if max_player else 1
      val = sign * np.inf
      bounds = [alpha, beta]
      for new_move in node.child(player):
        val = sign * min(sign * val,
                        sign * self.minimax(node, new_move, depth - 1, 
                                            not max_player, bounds[0], bounds[1]))
        if sign * (bounds[max_player] - val) >= 0:
          # input(f"breaking with val = {bounds[0]}<={val}<={bounds[1]} (max_player is {max_player})")
          break
        # input("not breaking")
        bounds[1 - max_player] = sign * min(sign * bounds[1 - max_player], 
                                            sign * val)
    node.undo_last_move(player)
    return val

AGENTS = {
  "minimax": MiniMaxAgent,
  "random": RandomAgent
}
