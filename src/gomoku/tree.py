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

  def traverse_one(self, move, n_visits=1, value=0, increment=1):
    if not self.is_leaf:
      for child in self.children:
        if child.name == str(move):
          child.n_visits += increment
          return child
    test = Tree(move, n_visits=n_visits, parent=self)
    return test

  def update_child_names(self):
    self.child_names = ([child.name for child in self.children]
                        if self.children is not None else [])

  def get_ucb(self, move_list, ucb_constant=2):
    self.update_child_names()
    ucb_values = []
    for move in move_list:
      if str(move) in self.child_names:
        n = self.traverse_one(move, increment=0)
        ucb_values.append(ucb(n.value, self.n_visits, n.n_visits, ucb_constant))
      else:
        ucb_values.append(ucb(0, self.n_visits, 0, ucb_constant))
    return np.array(ucb_values)

  def attr_list(self, attr_name):
    return list(map(get_attr(attr_name), self.children))

  def most_attr_child(self, attr_name):
    return self.children[np.argmax(self.attr_list(attr_name))].move

  def child_moves(self):
    return None if self.is_leaf else self.attr_list('move')

  def print_values(self):
    for child in self.children:
      print(f"{child.name} - value = {child.value}")

  def __str__(self):
    s = ''
    for pre, _, node in RenderTree(self):
      s += f"{pre}{node.name} (val = {node.value}, n_visits={node.n_visits}, "
      s += f"parent={node.parent.name if node.parent is not None else ''})\n"
    return s
