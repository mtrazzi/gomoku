from anytree import Node, RenderTree
import numpy as np

from gomoku.utils import get_attr, ucb


class Tree(Node):
  def __init__(self, move, n_visits=1, children=None,
               value=0, parent=None):
    super().__init__(name=str(move), parent=parent)
    self.move = move
    self.n_visits = n_visits
    self.value = value
    if children:
        self.children = children

  def traverse_one(self, move, n_visits=1, value=0):
    if not self.is_leaf:
      for child in self.children:
        if child.name == str(move):
          child.n_visits += 1
          return child
    test = Tree(move, n_visits=n_visits, parent=self)
    return test

  def get_ucb(self, move_list, ucb_constant=2):
    children = [self.traverse_one(move) for move in move_list]
    return np.array([ucb(n.value, n.parent.n_visits, n.n_visits, ucb_constant)
                     for n in children])

  # def get_ucb(self, ucb_constant=2):
  #   return np.array([ucb(n.value, n.parent.n_visits, n.n_visits, ucb_constant)
  #                    for n in self.children])


  def attr_list(self, attr_name):
    return list(map(get_attr(attr_name), self.children))

  def most_attr_child(self, attr_name):
    return self.children[np.argmax(self.attr_list(attr_name))].move

  def child_moves(self):
    return None if self.is_leaf else self.attr_list('move')

  def __str__(self):
    s = ''
    for pre, _, node in RenderTree(self):
      # s += f"{'here' if node.parent is not None and node.parent.parent is None else ''}"
      s += f"{pre}{node.name} (val = {node.value}, n_visits={node.n_visits}, "
      s += f"parent={node.parent.name if node.parent is not None else ''})\n"
    return s
