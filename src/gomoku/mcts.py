import copy
import time

from anytree import Node, RenderTree
import numpy as np

from gomoku.minimax import MiniMaxAgent
from gomoku.rules import Rules
from gomoku.tree import Tree

TIME_LIMIT = 5
BREAKING_TIME = 0.45 * TIME_LIMIT
ROLLOUT_TIME = 0.25 * TIME_LIMIT
UCB_CONSTANT = np.sqrt(2)


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
    self.tree = None

  def find_move(self, gh):
    if gh.board.empty_board():
      return gh.board.center()
    self.gh, self.start = gh, time.time()
    move = self.mcts()
    if time.time()-self.start > self.time_limit:
      exit(f"Exit: agent {self.algorithm_name} took too long to find his move")
    print(self.tree)
    self.tree = self.tree.traverse_one(move)
    return move

  def pick_random(self):
    while True:
      nb_child = len(self.gh.child_list)
      rand_idx = np.random.randint(0, nb_child)
      return self.gh.child_list[rand_idx]

  def rollout_policy(self):
    self.gh.do_move(self.pick_random())

  def is_terminal(self):
    return (Rules.check_winner(self.gh.board, self.gh.players) is not None or
            self.gh.board.is_full())

  def rollout(self, max_depth=np.inf, max_time=ROLLOUT_TIME):
    start, counter = time.time(), 0
    while ((start - time.time()) < ROLLOUT_TIME and counter < max_depth):
      self.rollout_policy()
      counter += 1
    result = self.result()
    for _ in range(counter):
      self.gh.undo_move()
    return result

  def result(self):
    player = Rules.check_winner(self.gh.board, self.gh.players)
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
    possible_moves = self.current_node.child_moves()
    if possible_moves is None:
      return self.pick_random()
    return possible_moves[np.random.randint(len(possible_moves))]

  def pick_unvisited(self):
    self.traverse_one(self.unvisited_move())

  def ucb_valid(self):
    """Return valid move sampled via ucb."""
    return self.ucb_sample()

  def ucb_sample(self):
    """
    Returns a child move using UCB exploration/exploitation tradeoff, and the
    number of visits of the edge from parent to child.
    cf. https://www.cs.swarthmore.edu/~bryce/cs63/s16/slides/2-15_MCTS.pdf
    """
    if not self.current_node.is_child():
      return self.pick_random()
    weights = self.current_node.get_ucb(UCB_CONSTANT)
    weights = weights - np.min(weights)  # avoiding negative weigths
    distribution = np.array([w / sum(weights)
                            if w > 0 else 1e-15 for w in weights])
    distribution = (1 / np.sum(distribution)) * distribution
    idx = np.random.choice(len(weights), p=distribution)
    return self.gh.child_list[idx]

  def traverse_one(self, move):
    self.gh.do_move(move)
    self.current_node = self.current_node.traverse_one(move)

  def traverse(self, max_depth=1):
    depth = 0
    while not self.fully_expanded():
      move = self.ucb_valid()
      depth += 1
      self.traverse_one(move)
      if depth >= max_depth:
        break
    self.pick_unvisited()

  def mcts(self):
    last_move_played = self.gh.last_move()
    if self.tree is None:
      self.tree = Tree(last_move_played)
    else:
      self.tree = self.tree.traverse_one(last_move_played)
    self.current_node = self.tree
    self.root = self.get_id()
    while self.resources_left():
      self.traverse(max_depth=2)
      result = self.rollout(max_depth=1)
      self.backpropagate(result)
    return self.best_child()
