from anytree import Node, RenderTree


class Tree(Node):
  def __init__(self, move, n_visits=1, parent=None, children=None,
               value=0):
    self.name = move
    self.n_visits = n_visits
    self.parent = parent
    self.n_wins = 0
    self.value = value
    if children:
        self.children = children

  def increment_visits(self):
    self.n_visits += 1

  def traverse_one(self, move, n_visits=1, value=1):
    if self.children:
      for child in self.children:
        if child.name == str(move):
          child.increment_visits()
          return child
    return Tree(str(move), n_visits=n_visits, parent=self)

  def __str__(self):
    s = ''
    for pre, _, node in RenderTree(self):
      s += f"{pre}{node.name} (val = {node.value}, n_visits={node.n_visits})\n"
    return s
