from anytree import Node, RenderTree  # FIXME Remove this in the future -42
import numpy as np
import time
import copy

from gomoku.agent import Agent, is_node_terminal
from gomoku.heuristics import (capture_heuristic, past_heuristic,
                               simple_heuristic, SCORE)
from gomoku.utils import human_move, is_there_stones_around, opposite
from gomoku.rules import Rules

from termcolor import colored

import builtins

try:
  builtins.profile
except AttributeError:
  # No line profiler, provide a pass-through version
  def profile(func): return func
  builtins.profile = profile

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
  """Class MinMaxAgent. Apply the MiniMax algorithm (cf.
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
  """
  def __init__(self, color=1, depth=2, max_top_moves=5, simple_eval_depth=0):
    super().__init__(color)
    self.depth = depth
    self.max_top_moves = max_top_moves
    self.debug = False
    self.simple_eval_depth = simple_eval_depth
    self.table = {}
    self.undo_table = {}
    self.time_limit = 20
    self.color_scores = np.zeros((19, 19)), np.zeros((19, 19))
    self.undo_scores = np.zeros((19, 19)), np.zeros((19, 19))
    self.color_scores_dict = {}
    self.last_captures = []
    self.count = {'retrievals': 0, 'not retrievals': 0, 'exit': 0}

  def reset(self):
    self.table = {}
    self.undo_table = {}
    self.color_scores = np.zeros((19, 19)), np.zeros((19, 19))
    self.undo_scores = np.zeros((19, 19)), np.zeros((19, 19))
    self.color_scores_dict = {}

  def child(self, gh):
    candidates, _ = self.best_moves(self.simple_evaluation(gh))
    return candidates

  def find_move(self, gh, max_depth=None):
    # If empty, start with the center
    if np.sum(gh.board.board) == 0:
      return gh.size // 2, gh.size // 2

    start = time.time()
    player, _ = self.return_players(gh, True)
    # Retrieve last captures
    self.last_captures = gh.retrieve_captured_stones()
    # Estimate moves using a depth = 1 evaluation
    score_map = self.simple_evaluation(gh)
    print(f"time for simple evaluation: {time.time() - start}s")
    # Find the list of best moves using this score map
    np.set_printoptions(linewidth=np.inf, precision=0)
    # print("\n\n\n\n##################  BEFORE  ##################\n\n\n\n")
    # print(score_map)
    # print(self.color_scores[0])
    # print(self.color_scores[1])
    # print("\n\n\n\n####################################\n\n\n\n")
    actual_candidates, corr_values = self.best_moves(score_map) #FIXME to remove double threes
    # actual_candidates = [move for move in candidates if gh.can_place(*move, player)]
    # print(f"top candidates: {actual_candidates}")
    values = [self.iterative_deepening(gh, coord, corr_values[i]) for (i, coord) in enumerate(actual_candidates)]
    # return the best candidate
    move_to_play = actual_candidates[np.argmax(values)]
    # in case of undo we still want to have the previous scores/tables available
    self.undo_scores, self.undo_table = copy.deepcopy(self.color_scores), copy.deepcopy(self.table)
    # only update color score according to move we're (actually) playing
    # if move_to_play[0] == 3 and move_to_play[1] == 9:
    #   import ipdb; ipdb.set_trace()
    self.color_scores = self.color_scores_dict[move_to_play]
    # print("\n\n\n\n################  AFTER  ##################\n\n\n\n")
    # # print(score_map)
    # print(self.color_scores[0])
    # print(self.color_scores[1])
    # print("\n\n\n\n####################################\n\n\n\n")
    print(colored(self.count ,'yellow'))
    print(f"total time: {time.time() - start}s")
    return move_to_play

  def iterative_deepening(self, game_handler, coord, initial_value=0):
    start = time.time()
    value = initial_value
    for depth in range(1, self.depth):
      # print(f"\n\n[ITERATIVE DEEPENING STEP] move is {coord}, value is: {value}, depth is: {depth}")
      # print(f"at this point child list is: {game_handler.child_list}")
      if time.time() - start >= (self.time_limit / 100):
        # print(f"[EXIT OF ITERATIVE DEEPENING] skipping at depth = {depth}\n\n")
        return value
      value = self.mtdf(game_handler, coord, depth, None, value)
      # value = self.ab_memory(game_handler, coord, depth)
    # print(f"[EXIT OF ITERATIVE DEEPENING] evaluating move {coord} took {time.time()-start}\n\n")
    return value

  @profile
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
    player, opponent = self.return_players(gh, True)
    beginning = time.time()
    tot_ab_mem = 0
    count = 0
    for x in range(size):
      for y in range(size):
        # only do moves that are near current stones
        if (not is_there_stones_around(gh.board.board, x, y) or
           (not gh.can_place(x, y, player))):
          continue
        # only change the score map if close enough to last move played
        # select top max_moves_checked moves with evaluation of depth one
        start = time.time()
        score_map[x][y] = self.ab_memory(gh, (x, y), self.simple_eval_depth)
        dt = time.time() - start
        count += 1
        tot_ab_mem += dt
    # print(f"average time for computing one move: {tot_ab_mem/count} ({count} moves)")
    # print(f"total simple_evaluation time: {time.time()-beginning}")
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
    values: int list
      The corresponding list of values of those moves.
    """
    top_move_list, values = [], []
    # print(score_map)
    for _ in range(self.max_top_moves):
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
    score_simple_heuristic, new_color_scores = simple_heuristic(position, color,my_turn, stones, copy.deepcopy(self.color_scores))
    self.color_scores_dict[player.last_move] = new_color_scores
    return (score_simple_heuristic + capture_heuristic(player, opponent, player.color == self.color)) #+ (1 / 100) * past_heuristic(opponent.last_move, player.last_move)) * 1e-12

  def return_players(self, node, max_player):
    # current player depends on if we're maximizing
    move_color = self.color if max_player else opposite(self.color)
    return node.players[move_color - 1], node.players[opposite(move_color) - 1]

  def minimax(self, node, move, depth, max_player=True, tree=None,alpha=-np.inf,
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
    node.do_move(move, player)
    if depth == 0:
      # after putting my stone, let's see what's the situation when not my turn
      val = self.evaluation(node.board.board, self.color, 1 - max_player,
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
    node.undo_move()
    return val

  @profile
  def ab_memory(self, node, move, depth, max_player=True, tree=None,
                             alpha=-np.inf, beta=np.inf):
    """Same as alpha beta pruning but uses hash to retrieve values for things
    it saw before.

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
      self.color_scores_dict[move] = self.color_scores  # FIXME
      node.undo_move()
      return SCORE['XXXXX'] if player.color == self.color else -SCORE['XXXXX']

    # tests if already seen node (that's why it's called "with memory")
    # cf. https://people.csail.mit.edu/plaat/mtdf.html#abmem
    node_id = hash(node.board.board.tostring())
    n = self.table[node_id] if node_id in self.table else None
    # only retrieve nodes if they were explored with higher depth
    # if n:
    #   print(f"for node_id = {node_id}, n.lowerbound={n.lowerbound} < {n.upperbound}=n.upperbound")
    # print(f"move = {move}")
    if n and depth <= n.depth: #and (depth - n.depth) % 2 == 0 and depth <= n.depth:
      # print(f"retrieving node_id {node_id}")
      self.count['retrievals'] += 1
      # print(f"depth={depth} and n.depth={n.depth}")
      if n.lowerbound >= beta:
        node.undo_move()
        # print(colored(f"and exiting because >= beta={beta}", 'green'))
        self.count['exit'] += 1
        return n.lowerbound
      if n.upperbound <= alpha:
        node.undo_move()
        # print(colored(f"and exiting because <= alpha={alpha}", 'green'))
        self.count['exit'] += 1
        return n.upperbound
      # print(colored("no-exit retrieval", 'red'))
      alpha = max(alpha, n.lowerbound)
      beta = min(beta, n.upperbound)
    else:
      self.count['not retrievals'] += 1
      # print(colored("not retrieving", 'blue'))
    if depth == 0:
      # after putting my stone, let's see what's the situation when not my turn
      # print(f"evaluation for move = {move}")
      val = self.evaluation(node.board.board, self.color, 1 - max_player, player, opponent, node.retrieve_captured_stones())
    else:
      # using a sign to avoid two conditions in minimax
      sign = 1 if max_player else -1
      val = sign * np.inf
      lim = [alpha, beta]
      # for new_move in node.child(player):
      # print(f"testing move = {move}, child list: {node.child_list}")
      for new_move in node.child_list:#self.child(node):
        # print(f"for loop: child={new_move}")
        val = sign * min(sign * val,
                         sign * self.ab_memory(node, new_move, depth - 1,
                                             1 - max_player, None, lim[0],
                                             lim[1]))
        if sign * (lim[1 - max_player] - val) >= 0:
          # print("breaking")
          break
        lim[max_player] = sign * min(sign * lim[max_player], sign * val)
    node.undo_move()
    # print(f"after undo_move, child list was: {node.child_list}")

    new_n = type('obj', (object,), {'lowerbound': -np.inf, 'upperbound': np.inf, 'depth': depth})()
    if n is None or new_n.depth > n.depth:
      # print(f"when storing {move}, node_id is {node_id}, alpha={alpha} val={val} beta={beta}")
      if val <= alpha:
        new_n.upperbound = val
      if val > alpha and val < beta:
        new_n.lowerbound = val
        new_n.upperbound = val
      if val >= beta:
        new_n.lowerbound = val
      self.table[node_id] = new_n
    return val

  def fail_hard(self, value, alpha, beta):
    """ab_memory wrapper so calls return values in the correct range"""
    if value < alpha:
      return alpha
    elif value > beta:
      return beta
    else:
      return value

  def mtdf(self, node, move, depth, tree=None, f=0):
    """cf. https://en.wikipedia.org/wiki/MTD-f"""
    g, lower_bound, upper_bound = f, -np.inf, np.inf
    counter = 0
    # print(f"[ENTERING MTDF LOOP FOR MOVE {move} (depth = {depth})]")
    while lower_bound < upper_bound:
      beta = (g + 1) if g == lower_bound else g
      counter += 1
      # print("[CALLING AB_MEMORY]")
      # print(f"counter = {counter} g={g:2E}, beta={beta}, lower_bound={lower_bound} < {upper_bound}=upper_bound")
      # g = self.fail_hard(self.ab_memory(node, move, depth, True, tree, beta - 1, beta), beta - 1, beta)
      g = self.ab_memory(node, move, depth, True, tree, beta - 1, beta)
      # print(colored(self.count ,'yellow'))
      # self.count = {'retrievals': 0, 'not retrievals': 0, 'exit': 0}
      if g < beta:
        upper_bound = g
      else:
        lower_bound = g
    # print(f"final g is: {g}")
    return g
