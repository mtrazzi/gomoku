from anytree import Node, RenderTree


class Tree(Node):
  def __init__(self, move, n_visits=1, parent=None, children=None):
    self.name = move
    self.n_visits = n_visits
    self.parent = parent
    if children:
        self.children = children

  def add_child(self, move, n_visits=1):
    if self.children:
      for child in self.children:
        if child.name == str(move):
          return child
    return Tree(str(move), n_visits=n_visits, parent=self)
