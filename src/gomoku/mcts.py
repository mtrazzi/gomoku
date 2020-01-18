import random
import time

import numpy as np

from gomoku.minimax import MiniMaxAgent
from gomoku.rules import Rules
from gomoku.tree import Tree
from gomoku.utils import SLOPES, were_impacted_slope, dist_sort

TIME_LIMIT = 20
BREAKING_TIME = 0.45 * TIME_LIMIT
ROLLOUT_TIME = 0.45 * TIME_LIMIT
UCB_CONSTANT = np.sqrt(2)
ALIGN_FIVE_VALUE = 1e2
MAX_IMP, MAX_CHILD, MAX_RANDOM = 1e1, 1e2, 1e3
# MAX_LIST = [MAX_IMP, MAX_CHILD, MAX_RANDOM]
MAX_LIST = [MAX_CHILD, MAX_RANDOM]
MAX_MOVES = 10
MAX_DEPTH = 2

class MCTSAgent(MiniMaxAgent):
  """Agent using Monte Carlo Tree Search. Inspired from:
  - geeksforgeeks.org/ml-monte-carlo-tree-search-mcts
  - cs.swarthmore.edu/~bryce/cs63/s16/slides/2-15_MCTS.pdf"""
  def __init__(self, color=1, depth=1):
    super().__init__(color)
    self.algorithm_name = 'mcts'
    self.tree = None
    self.rollout_depth = depth

  def relevant_moves(self):
    relev_mov, idx = [], 0
    while (idx < len(self.gh.move_history)
           and len(relev_mov) < MAX_MOVES):
      x, y = self.gh.move_history[-idx-1]
      for move in reversed(self.gh.child_list):
        if len(relev_mov) >= MAX_MOVES:
          break
        for (dx, dy) in SLOPES:
          if were_impacted_slope([move], x, y, dx, dy):
            relev_mov.append(move)
            break
      idx += 1
    return relev_mov

  def update_tree(self):
    last_move_played = tuple(self.gh.last_move())
    if self.tree is None:
      self.tree = Tree(last_move_played)
    else:
      self.tree = self.tree.traverse_one(last_move_played)
    self.current_node = self.tree

  def find_move(self, gh):
    if gh.board.empty_board():
      return gh.board.center()
    self.gh, self.start = gh, time.time()
    self.update_tree()
    while self.resources_left():
      self.mcts(n_iterations=1)
    move = self.best_child()
    if time.time()-self.start > TIME_LIMIT:
      exit(f"Exit: agent {self.algorithm_name} took too long to find his move")
    # print(self.tree)
    self.tree.print_values()
    # import ipdb; ipdb.set_trace()
    self.tree = self.tree.traverse_one(move)
    self.current_node = self.tree
    return move

  def pick_random_list(self, move_list, max_counter):
    counter = 0
    while True and counter < max_counter:
      move = random.choice(move_list)
      if self.gh.board.is_empty(*move):
        return move
      counter += 1
    return None

  def pick_random(self):
    size = self.gh.size
    random_list = [(i, j) for i in range(size) for j in range(size)]
    # move_lists = [self.imp_moves, self.gh.child_list, random_list]
    move_lists = [self.gh.child_list, random_list]
    for (move_list, max_counter) in zip(move_lists, MAX_LIST):
      move = self.pick_random_list(move_list, max_counter)
      if move is not None:
        return move
    return None

  def rollout_policy(self):
    random_move = self.pick_random()
    self.gh.basic_move(random_move)

  def rollout(self, max_depth=np.inf, max_time=ROLLOUT_TIME):
    start, counter = time.time(), 0
    while ((start - time.time()) < ROLLOUT_TIME and counter < max_depth):
      self.rollout_policy()
      counter += 1
    result = self.result()
    for _ in range(counter):
      self.gh.basic_undo()
    return result

  def result(self):
    #return self.captures_diff() + ALIGN_FIVE_VALUE * self.align_five_score()
    return self.align_five_score()

  def align_five_score(self):
    player = Rules.check_winner_basic(self.gh.board, self.gh.players)
    if player is None:
      return 0
    elif player.color == self.color:
      return 1
    else:
      return -1

  def best_child(self):
    return self.tree.most_attr_child('value')

  def is_root(self):
    return self.get_id() == self.root

  def update_stats(self, result):
    self.current_node.value += result

  def backpropagate_one(self, result=0):
    self.update_stats(result)
    self.current_node = self.current_node.parent
    self.gh.undo_move()

  def backpropagate(self, result):
    while not self.is_root():
      self.backpropagate_one(result)

  def resources_left(self):
    return (time.time() - self.start) < BREAKING_TIME

  def fully_expanded(self):
    return len(self.gh.child_list) == len(self.current_node.children)

  def unvisited_move(self):
    visited = self.current_node.child_moves()
    if visited is None:
      return self.pick_random()
    unvisited = list(set(self.gh.child_list) - set(visited))
    return random.choice(unvisited)

  def pick_unvisited(self):
    self.traverse_one(self.unvisited_move())

  def ucb_sample(self):
    """
    Returns a child move using UCB exploration/exploitation tradeoff, and the
    number of visits of the edge from parent to child.
    cf. https://www.cs.swarthmore.edu/~bryce/cs63/s16/slides/2-15_MCTS.pdf
    """
    # if self.current_node.is_leaf:
      # return self.pick_random()
    # print(self.imp_moves)
    # weights = self.current_node.get_ucb(self.imp_moves, UCB_CONSTANT)
    # print(weights)
    self.imp_moves = dist_sort(self.gh.last_move(), self.relevant_moves())[:MAX_MOVES]
    weights = self.current_node.get_ucb(self.gh.child_list, UCB_CONSTANT)
    # print(weights)
    weights = weights - np.min(weights) + 1e-15
    distribution = (1 / np.sum(weights)) * weights
    idx = np.random.choice(len(weights), p=distribution)
    return self.gh.child_list[idx]

  def traverse_one(self, move):
    self.gh.do_move(move)
    self.current_node = self.current_node.traverse_one(move)

  def captures_diff(self):
    capt_t = self.gh.get_player_captures()
    idx_mcts, idx_opp = self.color - 1, 1 - (self.color - 1)
    agent_capt = capt_t[idx_mcts] - self.capt_t0[idx_mcts]
    opp_capt = capt_t[idx_opp] - self.capt_t0[idx_opp]
    return agent_capt - opp_capt

  def is_end_state(self):
    return self.result() != 0 or self.captures_diff() != 0

  def is_terminal(self):
    return self.is_end_state() or self.current_node.is_leaf

  def traverse(self, max_depth=1):
    depth = 0
    while not self.is_terminal():# and depth <= max_depth:
      move = self.ucb_sample()
      depth += 1
      self.traverse_one(move)
    if not self.fully_expanded() and not self.is_end_state():
      self.pick_unvisited()

  def mcts(self, n_iterations=1):
    self.root, self.capt_t0 = self.get_id(), self.gh.get_player_captures()
    self.current_node, last_move = self.tree, self.gh.last_move()
    # self.imp_moves = dist_sort(last_move, self.relevant_moves())[:MAX_MOVES]
    # print(f"(1) {self.relevant_moves()}")
    # print(last_move)
    # print(self.imp_moves)
    for _ in range(n_iterations):
      self.traverse(max_depth=MAX_DEPTH)
      result = self.rollout(max_depth=self.rollout_depth)
      self.backpropagate(result)
