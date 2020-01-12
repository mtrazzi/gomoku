import copy
import time

import numpy as np

from gomoku.minimax import MiniMaxAgent
from gomoku.rules import Rules

from anytree import Node, RenderTree

TIME_LIMIT = 0.5
BREAKING_TIME = 0.1 * TIME_LIMIT
UCB_CONSTANT = 2
ROLLOUT_TIME = 0.01 * TIME_LIMIT


class MCTSAgent(MiniMaxAgent):
  """Agent using Monte Carlo Tree Search. Inspired from:
  - geeksforgeeks.org/ml-monte-carlo-tree-search-mcts
  - cs.swarthmore.edu/~bryce/cs63/s16/slides/2-15_MCTS.pdf"""
  def __init__(self, color=1, depth=2):
    super().__init__(color)
    self.time_limit = TIME_LIMIT
    self.d_visit = {}
    self.algorithm_name = 'mcts'
    self.depth = depth

  def find_move(self, gh):
    if gh.board.empty_board():
      return gh.board.center()
    self.gh, self.start = gh, time.time()
    move = self.mcts()
    if time.time()-self.start > self.time_limit:
      exit(f"Exit: agent {self.algorithm_name} took too long to find his move")
    self.print_tree()
    return move

  def pick_random(self):
    while True:
      nb_child = len(self.gh.child_list)
      rand_idx = np.random.randint(0, nb_child)
      rand_move = self.gh.child_list[rand_idx]
      player, _ = self.return_players()
      if self.gh.can_place(*rand_move):
        return rand_move

  def rollout_policy(self):
    self.gh.do_move(self.pick_random())

  def is_terminal(self):
    return (Rules.check_winner(self.gh.board, self.gh.players) is not None or
            self.gh.board.is_full())

  def rollout(self, max_depth=np.inf, max_time=ROLLOUT_TIME):
    start, counter = time.time(), 0
    while (not self.is_terminal() and (start - time.time()) < ROLLOUT_TIME and
           counter < max_depth):
      self.rollout_policy()
      counter += 1
    return self.result()

  def result(self):
    player = Rules.check_winner(self.gh.board, self.gh.players)
    if player is None:
      return 0
    elif player.color == self.color:
      return 1
    else:
      return -1

  def get_attr(self, move, attr):
    """Access certain attribute of a child."""
    self.gh.do_move(move)
    result = getattr(self.gh, attr)
    self.gh.undo_move()
    return result

  def best_child(self):
    def get_nb_visit(move): self.get_attr(move, 'visits')
    nb_visits = map(get_nb_visit, self.gh.child_list)
    return self.gh.child_list[np.argmax(nb_visits)]

  def is_root(self):
    return self.get_id() == self.root

  def update_stats(self, result):
    return 0

  def backpropagate(self, result):
    if self.is_root():
      return
    self.gh.stats = self.update_stats(result)
    self.gh.undo_move()
    self.backpropagate(result)

  def resources_left(self):
    return (time.time() - self.start) < BREAKING_TIME

  def fully_expanded(self):
    current_keys = self.d_visit.keys()
    for move in self.gh.child_list:
      move_id = self.get_action_value_id(move)
      if move_id not in current_keys:
        return False
    return True

  def pick_unvisited(self):
    if not self.resources_left():
      self.gh.do_move(self.pick_random())
    else:
      for move in self.gh.child_list:
        if not self.is_visited(move):
          self.gh.do_move(move)
          self.update_visits(move)
          break

  def ucb_valid(self, parent_visits):
    """Return valid move sampled via ucb."""
    while True:
      move, parent_visits = self.ucb_sample(parent_visits)
      if self.gh.can_place(*move):
        return move, parent_visits

  def get_action_value_id(self, move):
    node_id = self.get_id()
    return str(node_id) + str(move)

  def is_visited(self, move):
    move_id = self.get_action_value_id(move)
    return move_id in self.d_visit.keys()

  def get_visits(self, move):
    move_id = self.get_action_value_id(move)
    return self.d_visit[move_id] if move_id in self.d_visit.keys() else 1

  def ucb_sample(self, parent_visits):
    """
    Returns a child move using UCB exploration/exploitation tradeoff, and the
    number of visits of the edge from parent to child.
    cf. https://www.cs.swarthmore.edu/~bryce/cs63/s16/slides/2-15_MCTS.pdf
    """
    weights, visits = [], []
    for move in self.gh.child_list:
      self.gh.do_move(move)
      nb_visits = self.get_visits(move)
      w = (self.gh.value +
           UCB_CONSTANT * np.sqrt(np.log(parent_visits) / nb_visits))
      weights.append(w)
      visits.append(nb_visits)
      self.gh.undo_move()
    distribution = np.array([w / sum(weights)
                            if w > 0 else 1e-15 for w in weights])
    distribution = (1 / np.sum(distribution)) * distribution
    idx = np.random.choice(len(self.gh.child_list), p=distribution)
    return self.gh.child_list[idx], visits[idx]

  def update_visits(self, move):
    move_id = self.get_action_value_id(move)
    self.d_visit[move_id] = ((self.d_visit[move_id] + 1) if move_id in
                             self.d_visit.keys() else 1)

  def add_child(self, move, parent):
    
    return Node(str(move), parent=parent, val=0)

  def traverse(self, max_depth=1):
    parent_visits = 1
    depth = 0
    child = None
    while not self.fully_expanded():
      move, parent_visits = self.ucb_valid(parent_visits)
      self.update_visits(move)
      self.gh.do_move(move)
      depth += 1
      parent = self.tree if child is None else child
      child = self.add_child(move, parent)
      if depth >= max_depth:
        return
    self.pick_unvisited()  # different from gfg code

  def print_tree(self):
    for pre, _, node in RenderTree(self.tree):
      print("%s%s (val = %2d)" % (pre, node.name, node.val))

  def mcts(self):
    self.root = self.get_id()
    self.tree = Node("Root", val=0)
    while self.resources_left():
      self.traverse(max_depth=1)
      result = self.rollout(max_depth=1)
      self.backpropagate(result)
    return self.best_child()
