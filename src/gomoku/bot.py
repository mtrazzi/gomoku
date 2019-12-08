from abc import abstractmethod

import numpy as np

from gomoku.heuristics import capture_heuristic, simple_heuristic
from gomoku.player import Player
from gomoku.utils import is_there_stones_around, opposite


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
  def find_move(self, game_handler) -> (int, int):
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

  def find_move(self, game_handler):
    player = game_handler.players[game_handler.current]
    while True:
      size = game_handler.size
      x, y = np.random.randint(size), np.random.randint(size)
      if game_handler.can_place(x, y, player):
        break
    return x, y


class MiniMaxAgent(Agent):
  """Class MinMaxAgent. Apply the MiniMax algorithm (cf.
  https://en.wikipedia.org/wiki/Minimax#Pseudocode.)

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
  def __init__(self, stone=1, depth=3, max_top_moves=5):
    super().__init__(stone)
    self.depth = depth
    self.max_top_moves = max_top_moves

  def find_move(self, gh):
    # If empty, start with the center
    if np.sum(gh.board.board) == 0:
      return gh.size // 2, gh.size // 2
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
          score_map[x][y] = self.minimax(gh, (x, y), 0, False)
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
      x_max, y_max = np.unravel_index(np.argmax(score_map, axis=None),
                                      score_map.shape)
      top_move_list.append((x_max, y_max))
      score_map[x_max][y_max] = -np.inf
    return top_move_list

  def evaluation(self, position, color_to_move, my_turn, player, opponent):
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
    return (simple_heuristic(position, color_to_move, my_turn) +
            capture_heuristic(player, opponent))

  def return_players(self, node, max_player):
    # current player depends on if we're maximizing
    move_color = self.stone if max_player else opposite(self.stone)
    return node.players[move_color - 1], node.players[opposite(move_color) - 1]

  def minimax(self, node, move, depth, max_player, alpha=-np.inf, beta=np.inf):
    """The minimax function returns a heuristic value for leaf nodes (terminal
    nodes and nodes at the maximum search depth). Non leaf nodes inherit their
    value from a descendant leaf node.

    Parameters
    ----------
    node: GameHandler
      The current node being evaluated (a.k.a. board position)
    move: int, int
      The last move being played in the position to be evaluated
    depth: int
      The maximum depth of the tree for lookahead in the minimax algorithm
    max_player: bool
      True if in recursion we're considering the position according to the
      original player making the move, False if we're considering the opponent.

    Return
    ------
    value: int
      The estimated value of the current node (position) being evaluated.
    """
    player, opponent = self.return_players(node, max_player)
    # start your estimation of the move by doing the move
    node.do_move(move[0], move[1], player)
    if depth == 0:
      # after putting my stone, let's see what's the situation when not my turn
      val = self.evaluation(node.board.board, player.stone, 1 - max_player,
                            player, opponent)
    else:
      # using a sign to avoid two conditions in minimax
      sign = -1 if max_player else 1
      val = sign * np.inf
      lim = [alpha, beta]
      for new_move in node.child(player):
        val = sign * min(sign * val,
                         sign * self.minimax(node, new_move, depth - 1,
                                             1 - max_player, lim[0], lim[1]))
        if sign * (lim[max_player] - val) >= 0:
          break
        lim[1 - max_player] = sign * min(sign * lim[1 - max_player],
                                         sign * val)
    node.undo_last_move(player)
    return val