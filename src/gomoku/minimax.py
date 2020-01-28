import copy
import time

import numpy as np

from gomoku.agent import Agent
from gomoku.heuristics import (SCORE, capture_heuristic, heuristic,
                               past_heuristic)
from gomoku.rules import Rules
from gomoku.utils import best_values, opposite

TIME_LIMIT = 0.5
MTDF_BREAKING_TIME = 0.5 * TIME_LIMIT
ITE_BREAKING_TIME = 0.5 * TIME_LIMIT
SIMPLE_EVAL_MAX_TIME = 0.35 * TIME_LIMIT
MAX_CHILD = 32


def minimax_agent_wrapper(algorithm_name):
  def minimax_agent(color=1, depth=2, max_top_moves=5):
    return MiniMaxAgent(color, depth, max_top_moves, algorithm_name)
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
    while True:
      size = game_handler.size
      x, y = np.random.randint(size), np.random.randint(size)
      if game_handler.can_place(x, y):
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
  max_top_moves: int
    Maximum number of moves checked with maximum depth.
  algorithm_name: string
    The name of the special minimax flavor.
  """
  def __init__(self, color=1, depth=2, max_top_moves=5, algorithm_name='mtdf'):
    super().__init__(color)
    self.depth = depth
    self.max_top_moves = max_top_moves
    self.debug = False
    self.table = {}
    self.undo_table = {}
    self.time_limit = 0.5
    self.color_scores = np.zeros((19, 19)), np.zeros((19, 19))
    self.undo_scores = np.zeros((19, 19)), np.zeros((19, 19))
    self.color_scores_dict = {}
    self.last_captures = []
    self.algorithm_name = algorithm_name
    self.minimaximizer = self.get_algorithm(algorithm_name)
    self.gh = None
    self.ite_deep_depth = 0

  def get_algorithm(self, algorithm_name):
    return getattr(self, algorithm_name)

  def reset(self):
    self.table = {}
    self.undo_table = {}
    self.color_scores = np.zeros((19, 19)), np.zeros((19, 19))
    self.undo_scores = np.zeros((19, 19)), np.zeros((19, 19))
    self.color_scores_dict = {}

  def get_id(self):
    return hash(self.gh.board.board.tostring())

  def update(self, move_to_play):
    # in case of undo we still want to have the previous scores/tables available
    self.undo_scores = copy.deepcopy(self.color_scores)
    self.undo_table = copy.deepcopy(self.table)
    # only update color score according to move we're (actually) playing
    if move_to_play in self.color_scores_dict:
      self.color_scores = self.color_scores_dict[move_to_play]

  def update_because_opponent_played(self):
    player, opponent = self.return_players()
    self.evaluation(self.color, True, opponent, player)
    self.color_scores = self.color_scores_dict[opponent.last_move]

  def find_move(self, gh):
    self.start = time.time()
    # if first move, play in the center
    if gh.board.empty_board():
      return gh.board.center()
    self.gh = gh
    player, opponent = self.return_players()
    # need to update color scores accordingly to opponent's last move
    self.update_because_opponent_played()
    # Retrieve last captures (used in heuristics)
    self.last_captures = gh.retrieve_captured_stones()
    # Estimate moves using a depth = 0 evaluation on each of them
    score_map = self.simple_evaluation()
    # Find the list of best moves using this score map
    candidates, raw_val = self.best_moves(score_map, self.max_top_moves)
    # remove double threes
    candidates, raw_val = zip(*[(move, val)
                                for (move, val) in zip(candidates, raw_val)
                                if gh.can_place(*move)])
    # find best candidates with iterative deepening
    values = self.iterative_deepening(candidates, raw_val)
    # compute the best move
    move_to_play = candidates[np.argmax(values)]
    # save scores and transposition table
    self.update(move_to_play)
    if time.time()-self.start > self.time_limit:
      print(f"Agent {self.algorithm_name} lost because took >"
            f"{self.time_limit:.1}s to find his move.")
      self.gh.winner = opponent
    return move_to_play

  def iterative_deepening(self, moves, initial_values):
    values = ([list(initial_values)] +
              [[0 for _ in range(len(moves))] for _ in range(self.depth - 1)])
    depth, i = 0, len(moves)
    for depth in range(1, self.depth):
      if self.debug:
        print(f"depth {depth + 1}")
      for i in range(len(moves)):
        if time.time() - self.start >= ITE_BREAKING_TIME:
          if self.debug:
            print(f"break at iteration {i}")
          return best_values(values, depth, i)
        if self.algorithm_name == 'mtdf':
          values[depth][i] = self.minimaximizer(moves[i], depth,
                                                values[depth - 1][i])
        else:
          values[depth][i] = self.minimaximizer(moves[i], depth)
    return best_values(values, depth, i)

  def simple_evaluation(self):
    """Returns a score map for possible moves using a depth = 1 evaluation.

    Return
    ------
    score_map: numpy.ndarray
      For each coordinate, its depth = 1 evaluation.
    """
    gh, size = self.gh, self.gh.size
    player, opponent = self.return_players()
    score_map = np.full((size, size), -np.inf)
    for (x, y) in reversed(gh.child_list):
      if time.time() - self.start >= SIMPLE_EVAL_MAX_TIME:
        break
      gh.do_move((x, y))
      score_map[x][y] = self.evaluation(self.color, False, player, opponent)
      gh.undo_move()
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

  def evaluation(self, color, my_turn, player, opponent):
    """Evaluation function used for estimating the value of a node in minimax.

    Parameters
    ----------
    color: int
      The color for the first score in heuristic.
    player: Player
      The player that just placed a stone.
    opponent: Player
      The other player.

    Return
    ------
    value: int
      The estimated value of the current node (position) being evaluated.
    """
    captures = self.gh.retrieve_captured_stones()
    position = self.gh.board.board
    stones = [player.last_move, opponent.last_move] + captures
    h_score, c_score = heuristic(position, color, my_turn, stones,
                                 copy.deepcopy(self.color_scores))
    self.color_scores_dict[player.last_move] = c_score
    h_past = past_heuristic(opponent.last_move, player.last_move)
    return ((h_score + capture_heuristic(player, opponent,
                                         player.color == self.color) + h_past))

  def return_players(self, max_player=True):
    # current player depends on if we're maximizing
    move_color = self.color if max_player else opposite(self.color)
    players = self.gh.players
    return players[move_color - 1], players[opposite(move_color) - 1]

  def minimax(self, move, depth, max_player=True):
    """The minimax function returns a heuristic value for leaf nodes (terminal
    nodes and nodes at the maximum search depth). Non leaf nodes inherit their
    value from a descendant leaf node.

    Parameters
    ----------
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
    player, opponent = self.return_players(max_player)
    self.gh.do_move(move)

    # hardcoding forcing moves here to stop three exploring
    if Rules.aligned_win(self.gh.board, player):
      self.color_scores_dict[move] = self.color_scores
      self.gh.undo_move()
      return SCORE['XXXXX'] if player.color == self.color else -SCORE['XXXXX']

    if depth == 0:
      val = self.evaluation(self.color, 1 - max_player, player, opponent)
    else:
      sign = 1 if max_player else -1
      val = sign * np.inf
      for new_move in self.gh.child_list[-MAX_CHILD:]:
        val = sign * min(sign * val,
                         sign * self.minimax(new_move, depth - 1,
                                             1 - max_player))
    self.gh.undo_move()
    return val

  def alpha_beta(self, move, depth, max_player=True, alpha=-np.inf,
                 beta=np.inf):
    """Same as minimax but with alpha beta pruning.

    Parameters
    ----------
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
    player, opponent = self.return_players(max_player)
    self.gh.do_move(move)

    # hardcoding forcing moves here to stop three exploring
    if Rules.aligned_win(self.gh.board, player):
      self.color_scores_dict[move] = self.color_scores
      self.gh.undo_move()
      return SCORE['XXXXX'] if player.color == self.color else -SCORE['XXXXX']

    if depth == 0:
      val = self.evaluation(self.color, 1 - max_player, player, opponent)
    else:
      sign = 1 if max_player else -1
      val = sign * np.inf
      lim = [alpha, beta]
      for new_move in self.gh.child_list[-MAX_CHILD:]:
        val = sign * min(sign * val,
                         sign * self.alpha_beta(new_move, depth - 1,
                                                1 - max_player, lim[0], lim[1]))
        if sign * (lim[1 - max_player] - val) >= 0:
          break
        lim[max_player] = sign * min(sign * lim[max_player], sign * val)
    self.gh.undo_move()
    return val

  def alpha_beta_memory(self, move, depth, max_player=True, alpha=-np.inf,
                        beta=np.inf):
    """Same as alpha beta pruning but uses hash to retrieve values for things
    it saw before. Reference: https://people.csail.mit.edu/plaat/mtdf.html#abmem

    Parameters
    ----------
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
    player, opponent = self.return_players(max_player)
    self.gh.do_move(move)

    # hardcoding forcing moves here to stop three exploring
    if Rules.aligned_win(self.gh.board, player):
      self.color_scores_dict[move] = self.color_scores
      self.gh.undo_move()
      return SCORE['XXXXX'] if player.color == self.color else -SCORE['XXXXX']

    # tests if already seen node (that's why it's called "with memory")
    node_id = self.get_id()
    n = self.table[node_id] if node_id in self.table else None
    if n and depth < n.depth:
      if n.lowerbound >= beta:
        self.gh.undo_move()
        return n.lowerbound
      if n.upperbound <= alpha:
        self.gh.undo_move()
        return n.upperbound
      alpha = max(alpha, n.lowerbound)
      beta = min(beta, n.upperbound)

    if depth == 0:
      val = self.evaluation(self.color, 1 - max_player, player, opponent)
    else:
      sign = 1 if max_player else -1
      val = sign * np.inf
      lim = [alpha, beta]
      for new_move in self.gh.child_list[-MAX_CHILD:]:
        val = sign * min(sign * val,
                         sign * self.alpha_beta_memory(new_move,
                                                       depth - 1,
                                                       1 - max_player,
                                                       lim[0],
                                                       lim[1]))
        if sign * (lim[1 - max_player] - val) >= 0:
          break
        lim[max_player] = sign * min(sign * lim[max_player], sign * val)
    self.gh.undo_move()

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

  def mtdf(self, move, depth, f=0):
    """cf. https://en.wikipedia.org/wiki/MTD-f"""
    g, lower_bound, upper_bound = f, -np.inf, np.inf
    while lower_bound < upper_bound:
      if time.time() - self.start >= MTDF_BREAKING_TIME:
        return g
      beta = (g + 1) if g == lower_bound else g
      g = self.alpha_beta_memory(move, depth, True, beta - 1, beta)
      if g < beta:
        upper_bound = g
      else:
        lower_bound = g
    return g

  def alpha_beta_basic(self, move, depth, max_player=True, alpha=-np.inf,
                       beta=np.inf):
    """Same as alpha_beta, but only caring about aligning five.

    Parameters
    ----------
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
    player, _ = self.return_players(max_player)
    self.gh.basic_move(move)

    val = 0
    if depth == 0:
      if Rules.aligned_win(self.gh.board, player):
        val = SCORE['XXXXX'] if player.color == self.color else -SCORE['XXXXX']
    else:
      sign = 1 if max_player else -1
      val = sign * np.inf
      lim = [alpha, beta]
      for new_move in self.gh.child_list[-8:]:
        val = sign * min(sign * val,
                         sign * self.alpha_beta_basic(new_move, depth - 1,
                                                      1 - max_player, lim[0],
                                                      lim[1]))
        if sign * (lim[1 - max_player] - val) >= 0:
          break
        lim[max_player] = sign * min(sign * lim[max_player], sign * val)
    self.gh.basic_undo()
    return val
