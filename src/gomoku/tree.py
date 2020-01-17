from anytree import Node, RenderTree
import numpy as np

from gomoku.utils import get_attr, ucb


class Tree(Node):
  def __init__(self, move, n_visits=1, children=None,
               value=1, parent=None):
    super().__init__(name=str(move), parent=parent)
    self.move = move
    self.n_visits = n_visits
    self.n_wins = 0
    self.value = value
    if children:
        self.children = children

  def traverse_one(self, move, n_visits=1, value=1):
    if not self.is_leaf:
      for child in self.children:
        if child.name == str(move):
          self.n_visits += 1
          return child
    test = Tree(move, n_visits=n_visits, parent=self)
    return test

  def get_ucb(self, ucb_constant=2):
    return [ucb(n.value, n.parent.n_visits, n.n_visits, ucb_constant) for n in
            self.children]

  def attr_list(self, attr_name):
    return list(map(get_attr(attr_name), self.children))

  def most_attr_child(self, attr_name):
    return self.children[np.argmax(self.attr_list(attr_name))].move

  def child_moves(self):
    return None if self.is_leaf else self.attr_list('move')

  def __str__(self):
    s = ''
    for pre, _, node in RenderTree(self):
      s += f"{pre}{node.name} (val = {node.value}, n_visits={node.n_visits},"
      s += "parent={node.parent.name if node.parent is not None else ''})\n"
    return s
