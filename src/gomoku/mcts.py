import random
import time

import numpy as np

from gomoku.minimax import MiniMaxAgent
from gomoku.rules import Rules
from gomoku.tree import Tree

TIME_LIMIT = 10
BREAKING_TIME = 0.45 * TIME_LIMIT
ROLLOUT_TIME = 0.45 * TIME_LIMIT
UCB_CONSTANT = np.sqrt(2)
ALIGN_FIVE_VALUE = 1e2


class MCTSAgent(MiniMaxAgent):
  """Agent using Monte Carlo Tree Search. Inspired from:
  - geeksforgeeks.org/ml-monte-carlo-tree-search-mcts
  - cs.swarthmore.edu/~bryce/cs63/s16/slides/2-15_MCTS.pdf"""
  def __init__(self, color=1, depth=1):
    super().__init__(color)
    self.algorithm_name = 'mcts'
    self.tree = None
    self.rollout_depth = depth

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
      self.mcts()
    move = self.best_child()
    if time.time()-self.start > TIME_LIMIT:
      exit(f"Exit: agent {self.algorithm_name} took too long to find his move")
    self.tree = self.tree.traverse_one(move)
    self.current_node = self.tree
    return move

  def pick_random(self):
    while True:
      move = random.choice(self.gh.child_list)
      if self.gh.board.is_empty(*move):
        break
    return move

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
    return self.captures_diff() + ALIGN_FIVE_VALUE * self.align_five_score()
    # return self.align_five_score()

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
    if self.current_node.is_leaf:
      return self.pick_random()
    weights = self.current_node.get_ucb(UCB_CONSTANT)
    weights = weights - np.min(weights)
    distribution = np.array([w / sum(weights)
                            if w > 0 else 1e-15 for w in weights])
    distribution = (1 / np.sum(distribution)) * distribution
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

  def traverse(self):
    depth = 0
    while not self.is_terminal():
      move = self.ucb_sample()
      depth += 1
      self.traverse_one(move)
    if self.current_node.is_leaf:
      self.pick_unvisited()

  def mcts(self, n_iterations=1):
    self.root, self.capt_t0 = self.get_id(), self.gh.get_player_captures()
    self.current_node = self.tree
    for _ in range(n_iterations):
      self.traverse()
      result = self.rollout(max_depth=self.rollout_depth)
      self.backpropagate(result)
