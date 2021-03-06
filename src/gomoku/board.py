import sys

import numpy as np


class Board(object):
  """Class Board

  Args:
    filename: str (Default: None)
      If filename is specify, load board state
    size: int (Default: 19)
      Size of the map
    cmap: dict (Default: {0: '.', 1: 'X', 2: 'O'})
      Map board value with symbol

  Attributes
  ----------
  board: 2D array
    The board
  """
  def __init__(self, filename=None, size=19, cmap={0: '.', 1: 'X', 2: 'O'}):
    self.board = np.zeros((size, size))
    self.filename = filename
    self.size = size
    self.cmap = cmap

    if filename:
      self.parse(filename)

  def __str__(self):
    representation = f"ₓ\\ʸ"
    for i in range(self.size):
      representation += f"{(i + 1):2} "
    representation += "\n"
    for i in range(self.size):
      representation += f"{(i + 1):2} "
      for j in range(self.size):
        x = self.board[i][j]
        if j in [3, 9, 15] and i in [3, 9, 15] and x == 0:
          representation += f"{'*':>2} "
        else:
          representation += f"{self.cmap[x]:>2} "
      representation += "\n"
    return representation

  def restart(self):
    """Reset board to it's initial state."""
    self.board = np.zeros((self.size, self.size))
    if self.filename:
      self.parse(self.filename)

  def is_empty(self, x, y):
    """Return if the intersection (x, y) is empty."""
    return self.board[x][y] == 0

  def is_stone(self, x, y, color):
    """Return if the stone at intersection (x, y) belongs to player."""
    return self.board[x][y] == color

  def place(self, x, y, color):
    """Place the player stone at intersection (x, y)."""
    self.board[x][y] = color
    return self

  def remove(self, x, y):
    """Remove stone at intersection (x, y)."""
    self.board[x][y] = 0
    return self

  def empty_board(self):
    """Returns true if the board is empty."""
    return np.sum(self.board) == 0

  def center(self):
    """Returns the coordinates of the center of the board."""
    return self.size // 2, self.size // 2

  def is_full(self):
    """Returns True if the entire board is full."""
    return not (0 in self.board)

  def parse(self, file):
    try:
      inv_cmap = {v: k for k, v in self.cmap.items()}
      inv_cmap['*'] = 0
      if file == "custom":
        raw = [line.rstrip().split() for line in sys.stdin]
      else:
        f = open(file, 'r')
        raw = [line.strip().split() for line in f]
      board = [l[1:] for l in raw[1:]]
      for i in range(self.size):
        for j in range(self.size):
          self.board[i][j] = inv_cmap[board[i][j]]
    except Exception:
      print("Error encountered while parsing board, starting with empty board.")
      self.board = np.zeros((self.size, self.size))
