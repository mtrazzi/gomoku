from abc import abstractmethod

from anytree import Node, RenderTree  # FIXME Remove this in the future -42
import numpy as np

from gomoku.heuristics import capture_heuristic, simple_heuristic
from gomoku.player import Player
from gomoku.utils import human_move, is_there_stones_around, opposite


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
    Maximum number of moves checked with maximum depth.
  """
  def __init__(self, stone=1, depth=0, max_top_moves=5, simple_eval_depth=0):
    super().__init__(stone)
    self.depth = depth
    self.max_top_moves = max_top_moves
    self.debug = False
    self.simple_eval_depth = simple_eval_depth

  def find_move(self, gh):
    # If empty, start with the center
    if np.sum(gh.board.board) == 0:
      return gh.size // 2, gh.size // 2
    # Estimate moves using a depth = 1 evaluation
    score_map = self.simple_evaluation(gh)
    # Find the list of best moves using this score map
    candidates = self.best_moves(score_map)
    hcand = [human_move(move) for move in candidates]
    # estimate the value of those candidates using minimax at full depth
    tree_list, values = [], []
    # values = [self.minimax(gh, coord, self.depth - 1, True)
              # for coord in candidates]
    for coord in candidates:
      tree = Node(coord, val=0)
      values.append(self.minimax(gh, coord, self.depth - 1, True, tree))
      tree_list.append(tree)
    if self.debug:
      print(gh.board)
      print(f"hcandidates={hcand}")
      for i, tree in enumerate(tree_list):
        tree.val = values[i]
        for pre, _, node in RenderTree(tree):
          print("%s%s (val = %2d)" % (pre, human_move(node.name), node.val))
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
          score_map[x][y] = self.minimax(gh, (x, y), self.simple_eval_depth, True)
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

  def evaluation(self, position, color, my_turn, player, opponent):
    """Evaluation function used for estimating the value of a node in minimax.

    Parameters
    ----------
    position: numpy.ndarray
      The current board position being evaluated.
    color: int
      The color for the first score in simple_heuristic.
    player: Player
      The player that just placed a stone.
    opponent: Player
      The other player.

    Return
    ------
    value: int
      The estimated value of the current node (position) being evaluated.
    """
    return (simple_heuristic(position, color, my_turn) +
            capture_heuristic(player, opponent, player.stone == self.stone))

  def return_players(self, node, max_player):
    # current player depends on if we're maximizing
    move_color = self.stone if max_player else opposite(self.stone)
    return node.players[move_color - 1], node.players[opposite(move_color) - 1]

  def minimax(self, node, move, depth, max_player, tree=None, alpha=-np.inf,
              beta=np.inf):
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
      Are we maximizing or not?.

    Return
    ------
    value: int
      The estimated value of the current node (position) being evaluated.
    """
    player, opponent = self.return_players(node, max_player)
    # start your estimation of the move by doing the move
    if not node.board.is_empty(*move):
      return -np.Inf
    node.do_move(*move, player)
    if depth == 0:
      # after putting my stone, let's see what's the situation when not my turn
      val = self.evaluation(node.board.board, self.stone, 1 - max_player,
                            player, opponent)
    else:
      # using a sign to avoid two conditions in minimax
      sign = 1 if max_player else -1
      val = sign * np.inf
      lim = [alpha, beta]
      for new_move in node.child(player):
        new_tree = Node(new_move, parent=tree, val=0)
        val = sign * min(sign * val,
                         sign * self.minimax(node, new_move, depth - 1,
                                             1 - max_player, new_tree, lim[0],
                                             lim[1]))
        new_tree.val = val
        if sign * (lim[1 - max_player] - val) >= 0:
          break
        lim[max_player] = sign * min(sign * lim[max_player], sign * val)
    node.undo_last_move(player)
    return val
