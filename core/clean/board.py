import numpy as np

class Board(object):
  """Class Board

  Parameters
  ----------
  size: int (Default: 19)
    Size of the map

  Attributes
  ----------
  board: 2D array
    The board
  """
  def __init__(self, size=19, cmap={0: '.', 1: 'X', 2: 'O'}):
    self.board = np.zeros((size, size))
    self.size = size
    self.cmap = cmap

  def __str__(self):
    representation = f"ₓ\\ʸ"
    for i in range(self.size):
      representation += f"{(i+1):2} "
    representation += "\n"

    for i in range(self.size):
      representation += f"{(i+1):2} "
      for j in range(self.size):
        x = self.board[i][j]
        if j in [3, 9, 15] and i in [3, 9, 15] and x == 0:
          representation += f"{'*':>2} "
        else:
          representation += f"{self.cmap[x]:>2} "
      representation += "\n"

    return representation

  def is_empty(self, x, y):
    """Return if the intersection (x, y) is empty"""
    return self.board[x][y] == 0

  def is_stone(self, x, y, player):
    """Return if the stone at intersection (x, y) belongs to player"""
    return self.board[x][y] == player.stone

  def place(self, x, y, player):
    """Place the player stone at intersection (x, y)"""
    self.board[x][y] = player.stone
    return self

  def remove(self, x, y):
    """Remove stone at intersection (x, y)"""
    self.board[x][y] = 0
    return self
