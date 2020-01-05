import copy
import time

import numpy as np

from gomoku.agent import Agent
from gomoku.heuristics import (SCORE, capture_heuristic, past_heuristic,
                               simple_heuristic)
from gomoku.rules import Rules
from gomoku.utils import is_there_stones_around, opposite

CHILD_HYPERPARAM = 10


def minimax_agent_wrapper(algorithm_name):
  def minimax_agent(color=1, depth=2, max_top_moves=5, simple_eval_depth=0):
    return MiniMaxAgent(color, depth, max_top_moves, simple_eval_depth,
                        algorithm_name)
  return minimax_agent


class RandomAgent(Agent):
  """Class RandomAgent. Plays valid random moves.

  Parameters
  ----------
  color: int
    The color of the stone of the Agent
  """
  def __init__(self, color):
    super().__init__(color)

  def find_move(self, game_handler):
    player = game_handler.players[game_handler.current]
    while True:
      size = game_handler.size
      x, y = np.random.randint(size), np.random.randint(size)
      if game_handler.can_place(x, y, player):
        break
    return x, y


class MiniMaxAgent(Agent):
  """Applies a variation of the MiniMax algorithm (cf.
  https://en.wikipedia.org/wiki/Minimax#Pseudocode.)

  Parameters
  ----------
  color: int
    The color of the stone of the Agent.
  depth: int
    The maximum depth of the tree for lookahead in the minimax algorithm.
  heuristic: string
    The heuristic used to evaluate nodes.
  max_top_moves: int
    Maximum number of moves checked with maximum depth.
  simple_eval_depth: int
    Depth used in simple evaluation for the first evaluation of moves.
  algorithm_name: string
    The name of the special minimax flavor.
  """
  def __init__(self, color=1, depth=2, max_top_moves=5, simple_eval_depth=0,
               algorithm_name='alpha_beta_memory'):
    super().__init__(color)
    self.depth = depth
    self.max_top_moves = max_top_moves
    self.debug = False
    self.simple_eval_depth = simple_eval_depth
    self.table = {}
    self.undo_table = {}
    self.time_limit = 1
    self.color_scores = np.zeros((19, 19)), np.zeros((19, 19))
    self.undo_scores = np.zeros((19, 19)), np.zeros((19, 19))
    self.color_scores_dict = {}
    self.last_captures = []
    self.algorithm_name = algorithm_name
    self.minimaximizer = self.get_algorithm(algorithm_name)

  def get_algorithm(self, algorithm_name):
    return getattr(self, algorithm_name)

  def reset(self):
    self.table = {}
    self.undo_table = {}
    self.color_scores = np.zeros((19, 19)), np.zeros((19, 19))
    self.undo_scores = np.zeros((19, 19)), np.zeros((19, 19))
    self.color_scores_dict = {}

  def optimum_child_nb(self, gh):
    return max(1, int((CHILD_HYPERPARAM * self.max_top_moves) //
               (np.log(gh.total_moves_played + 1) * self.depth)))

  def child(self, gh):
    candidates, _ = self.best_moves(self.simple_evaluation(gh),
                                    self.optimum_child_nb(gh))
    return candidates

  def update(self, move_to_play):
    # in case of undo we still want to have the previous scores/tables available
    self.undo_scores = copy.deepcopy(self.color_scores)
    self.undo_table = copy.deepcopy(self.table)
    # only update color score according to move we're (actually) playing
    if move_to_play in self.color_scores_dict:
      self.color_scores = self.color_scores_dict[move_to_play]

  def find_move(self, gh, max_depth=None):
    # if first move, play in the center
    if gh.board.empty_board():
      return gh.board.center()
    player, _ = self.return_players(gh, True)
    # Retrieve last captures (used in heuristics)
    self.last_captures = gh.retrieve_captured_stones()
    # Estimate moves using a depth = 0 evaluation on each of them
    start = time.time()
    score_map = self.simple_evaluation(gh)
    print(f"simple evaluation took {time.time() - start}")
    # Find the list of best moves using this score map
    candidates, raw_val = self.best_moves(score_map, self.max_top_moves)
    # remove double threes
    candidates, raw_val = zip(*[(move, val)
                                for (move, val) in zip(candidates, raw_val)
                                if gh.can_place(*move, player)])
    # find best candidates with iterative deepening
    self.begin, self.moves_left = time.time(), self.max_top_moves
    values = [self.iterative_deepening(gh, coord, raw_val[i])
              for (i, coord) in enumerate(candidates)]
    # compute the best move
    move_to_play = candidates[np.argmax(values)]
    # save scores and transposition table
    self.update(move_to_play)
    return move_to_play

  def iterative_deepening(self, game_handler, coord, initial_value=0):
    self.moves_left -= 1
    start, value = time.time(), initial_value
    for depth in range(0, self.depth):
      remaining_time = self.time_limit - (time.time() - self.begin) - 0.2
      if time.time() - start >= (remaining_time / (self.moves_left + 1)):
        print(f"skipping with depth = {depth}")
        return value
      print(f"entering depth = {depth}")
      if self.algorithm_name == 'mtdf':
        value = self.minimaximizer(game_handler, coord, depth, value)
      else:
        value = self.minimaximizer(game_handler, coord, depth)
    return value

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
    player, opponent = self.return_players(gh, True)
    score_map = np.full((size, size), -np.inf)
    player, _ = self.return_players(gh, True)
    for x in range(size):
      for y in range(size):
        if (not is_there_stones_around(gh.board.board, x, y) or
           (not gh.can_place(x, y, player))):
          continue
        game_handler.do_move((x, y), player)
        score_map[x][y] = self.evaluation(game_handler.board.board, self.color,
                                          False, player, opponent,
                                          game_handler.retrieve_captured_stones
                                          ())
        game_handler.undo_move()
    return score_map

  def best_moves(self, score_map, max_top_moves=5):
    """Returns the top `max_top_moves` moves according to the score map.

    Parameters
    ----------
    score_map: numpy.ndarray
      For each coordinate, its depth = 1 evaluation.

    Return
    ------
    top_move_list: (int, int) list
      The list of coordinates of the best `max_top_moves` moves.
    values: int list
      The corresponding list of values of those moves.
    """
    top_move_list, values = [], []
    for _ in range(max_top_moves):
      x_max, y_max = np.unravel_index(np.argmax(score_map, axis=None),
                                      score_map.shape)
      top_move_list.append((x_max, y_max))
      values.append(score_map[x_max][y_max])
      score_map[x_max][y_max] = -np.inf
    return top_move_list, values

  def evaluation(self, position, color, my_turn, player, opponent, captures=[]):
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
    captures: (int, int) list
      List of last captured stones (for heuristic).

    Return
    ------
    value: int
      The estimated value of the current node (position) being evaluated.
    """
    stones = [player.last_move, opponent.last_move] + captures
    h_score, c_score = simple_heuristic(position, color, my_turn, stones,
                                        copy.deepcopy(self.color_scores))
    self.color_scores_dict[player.last_move] = c_score
    h_past = past_heuristic(opponent.last_move, player.last_move)
    return ((h_score + capture_heuristic(player, opponent,
                                         player.color == self.color) + h_past))

  def return_players(self, node, max_player):
    # current player depends on if we're maximizing
    move_color = self.color if max_player else opposite(self.color)
    return node.players[move_color - 1], node.players[opposite(move_color) - 1]

  def minimax(self, node, move, depth, max_player=True):
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
    node.do_move(move, player)

    # hardcoding forcing moves here to stop three exploring
    if Rules.aligned_win(node.board, player):
      self.color_scores_dict[move] = self.color_scores
      node.undo_move()
      return SCORE['XXXXX'] if player.color == self.color else -SCORE['XXXXX']

    if depth == 0:
      val = self.evaluation(node.board.board, self.color, 1 - max_player,
                            player, opponent, node.retrieve_captured_stones())
    else:
      sign = 1 if max_player else -1
      val = sign * np.inf
      for new_move in node.child_list:
        val = sign * min(sign * val,
                         sign * self.minimax(node, new_move, depth - 1,
                                             1 - max_player))
    node.undo_move()
    return val

  def alpha_beta(self, node, move, depth, max_player=True, alpha=-np.inf,
                 beta=np.inf):
    """Same as minimax but with alpha beta pruning.

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
    alpha: int
      The current lower bound for the cutoff.
    beta: int
      The current upper bound for the cutoff.

    Return
    ------
    value: int
      The estimated value of the current node (position) being evaluated.
    """
    player, opponent = self.return_players(node, max_player)
    node.do_move(move, player)

    # hardcoding forcing moves here to stop three exploring
    if Rules.aligned_win(node.board, player):
      self.color_scores_dict[move] = self.color_scores
      node.undo_move()
      return SCORE['XXXXX'] if player.color == self.color else -SCORE['XXXXX']

    if depth == 0:
      val = self.evaluation(node.board.board, self.color, 1 - max_player,
                            player, opponent, node.retrieve_captured_stones())
    else:
      sign = 1 if max_player else -1
      val = sign * np.inf
      lim = [alpha, beta]
      for new_move in node.child(player):
        val = sign * min(sign * val,
                         sign * self.alpha_beta(node, new_move, depth - 1,
                                                1 - max_player, lim[0],
                                                lim[1]))
        if sign * (lim[1 - max_player] - val) >= 0:
          break
        lim[max_player] = sign * min(sign * lim[max_player], sign * val)
    node.undo_move()
    return val

  def alpha_beta_memory(self, node, move, depth, max_player=True, alpha=-np.inf,
                        beta=np.inf):
    """Same as alpha beta pruning but uses hash to retrieve values for things
    it saw before. Reference: https://people.csail.mit.edu/plaat/mtdf.html#abmem

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
    alpha: int
      The current lower bound for the cutoff.
    beta: int
      The current upper bound for the cutoff.

    Return
    ------
    value: int
      The estimated value of the current node (position) being evaluated.
    """
    player, opponent = self.return_players(node, max_player)
    node.do_move(move, player)

    # hardcoding forcing moves here to stop three exploring
    if Rules.aligned_win(node.board, player):
      self.color_scores_dict[move] = self.color_scores
      node.undo_move()
      return SCORE['XXXXX'] if player.color == self.color else -SCORE['XXXXX']

    # tests if already seen node (that's why it's called "with memory")
    node_id = hash(node.board.board.tostring())
    n = self.table[node_id] if node_id in self.table else None
    if n and depth <= n.depth:
      if n.lowerbound >= beta:
        node.undo_move()
        return n.lowerbound
      if n.upperbound <= alpha:
        node.undo_move()
        return n.upperbound
      alpha = max(alpha, n.lowerbound)
      beta = min(beta, n.upperbound)

    if depth == 0:
      val = self.evaluation(node.board.board, self.color, 1 - max_player,
                            player, opponent, node.retrieve_captured_stones())
    else:
      sign = 1 if max_player else -1
      val = sign * np.inf
      lim = [alpha, beta]
      for new_move in node.child_list:
        val = sign * min(sign * val,
                         sign * self.alpha_beta_memory(node,
                                                       new_move,
                                                       depth - 1,
                                                       1 - max_player,
                                                       lim[0],
                                                       lim[1]))
        if sign * (lim[1 - max_player] - val) >= 0:
          break
        lim[max_player] = sign * min(sign * lim[max_player], sign * val)
    node.undo_move()

    new_n = type('obj', (object,), {'lowerbound': -np.inf,
                 'upperbound': np.inf, 'depth': depth})()
    if n is None or new_n.depth > n.depth:
      if val <= alpha:
        new_n.upperbound = val
      if val > alpha and val < beta:
        new_n.lowerbound = val
        new_n.upperbound = val
      if val >= beta:
        new_n.lowerbound = val
      self.table[node_id] = new_n
    return val

  def mtdf(self, node, move, depth, f=0):
    """cf. https://en.wikipedia.org/wiki/MTD-f"""
    g, lower_bound, upper_bound = f, -np.inf, np.inf
    counter = 0
    while lower_bound < upper_bound:
      beta = (g + 1) if g == lower_bound else g
      counter += 1
      g = self.alpha_beta_memory(node, move, depth, True, beta - 1, beta)
      if g < beta:
        upper_bound = g
      else:
        lower_bound = g
    return g
