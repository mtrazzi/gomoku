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
    The heuristic used to evaluate nodes
  max_moves_checked: int
    Maximum number of moves checked with depth > 1
  """
  def __init__(self, stone=1, depth=4, heuristic='simple', max_moves_checked=4):
    super().__init__(stone)
    self.depth = depth
    self.max_moves_checked = max_moves_checked

  def input(self, game_handler):
    # get the best max_moves_checked moves with depth = 1
    size = game_handler.size
    score_map = np.full((size, size), -np.inf)
    player = game_handler.players[game_handler.current]
    for x in range(size):
      for y in range(size):
        # only do moves that are near current stones
        if not is_there_stones_around(game_handler.board.board, x, y):
          score_map[x][y] = -np.inf
          continue
        # select top max_moves_checked moves with evaluation of depth one
        if game_handler.can_place(x, y, player):
          game_handler.do_move(x, y, player)
          score_map[x][y] = self.minimax(game_handler, self.depth - 2, False)
          game_handler.undo_last_move(player)

    # select the best move using maximum depth = depth
    val_dic = {}
    for _ in range(self.max_moves_checked):
      x_max, y_max = np.unravel_index(np.argmax(score_map, axis=None),                                          score_map.shape)
      if score_map[x_max][y_max] > -np.inf:
        game_handler.do_move(x_max, y_max, player)
        val_dic[(x_max,y_max)] = self.minimax(game_handler, self.depth - 1, False)
        game_handler.undo_last_move(player)
      # erase the max value to take the next max value
      score_map[x_max][y_max] = -np.inf
    print(val_dic)
    input("Press Enter to continue...")
    return max(val_dic, key=val_dic.get)

  def eval(self, node, player, heuristic='simple'):
    """Evaluation function used for estimating the value of a node in minimax

    Parameters
    ----------
    node: GameHandler
      The current node being evaluated (a.k.a. board position)
    player: Player
      The current player that is being evaluated
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

  def minimax(self, node, depth, maximizing_player, alpha=-np.inf, beta=np.inf):
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
    player = node.players[maximizing_player]
    # print(f"=========================================================================\nminmax called with depth={depth} and player={player.stone}vv")
    if depth == 0: #or node.is_done(): # no real need to check if game is over
      return self.eval(node, player)
    if maximizing_player:
      value = -np.inf
      for child in node.child(player):
        value = max(value, self.minimax(child, depth - 1, False, alpha, beta))
        alpha = max(alpha, value)
        if alpha >= beta:
          break
      return value
    else:
      value = np.inf
      for child in node.child(player):
        value = min(value, self.minimax(child, depth - 1, True, alpha, beta))
        beta = min(beta, value)
        if alpha >= beta:
          break
      return value

AGENTS = {
  "minmax": MiniMaxAgent,
  "random": RandomAgent
}
