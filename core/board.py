import numpy as np
import sys
import os
from core import rules

class Board(object):
  def __init__(self):
    self.map = self.empty_map(19)

  def print_map(self):
    dic = {0: ".", 1: "X", 2: "O", 3: "*"}
    self.change_hoshi()
    sys.stdout.write("   ")
    for j in range(len(self.map)):
      sys.stdout.write("%2d " % (j + 1))
    print()
    for i in range(len(self.map)):
      sys.stdout.write("%2d " % (i + 1))
      for x in self.map[i]:
        sys.stdout.write("%2c " % dic[x])
      print()
    self.change_hoshi()

  def	change_hoshi(self):
      size = len(self.map)
      for i in (range(size)):
          for j in (range(size)):
              if (i == 3 or i == 9 or i == 15):
                  if (j == 3 or j== 9 or j == 15):
                      if (self.map[i][j] == 0 or self.map[i][j] == 3):
                          self.map[i][j] = 3 - self.map[i][j]
      return map

  def	empty_map(self, size):
      return np.zeros((size, size))

  def	add_point(self, type, x, y):
      self.map[x - 1][y - 1] = type

  def RepresentsInt(self, s):
      try:
          int(s)
          return True
      except ValueError:
          return False

  def is_valid_input(self, s):
      if (len(s.split(None)) != 2):
          return False
      if ((not self.RepresentsInt(s.split()[0])) or (not self.RepresentsInt(s.split()[1]))):
          return False
      x = int(s.split()[0])
      y = int(s.split()[1])
      return ((x > 0 and x <= len(self.map)) and (y > 0 and y <= len(self.map)) \
      and (self.map[x - 1][y - 1] == 0))

  def get_input(self):
      user_input = ""
      while (user_input != "exit" and (not self.is_valid_input(user_input))):
          # os.system("clear")
          self.print_map()
          if (user_input != ""):
              print("Move badly formated : must type \"x y\" with x and y integers")
              print("Example : \"2 3\"")
              print("Intersection must be empty (must be \'.\' or *)")
              print("Can capture two stones")
          user_input = input("Your next move (type \"exit\" to quit): $>")
      if (user_input == "exit"):
          sys.exit()
      return (int(user_input.split(None)[0]), int(user_input.split(None)[1]))
    
  def is_dead(self, x ,y, color):
    # check if player "color" managed to kill two stones of the other color, one stone being on x y
    # cannot kill stones of own color
    if self.map[x][y] == color:
      return False
    dead_up = (len(self.map) - 1 > x > 1 and self.map[x - 2][y] == color and self.map[x - 1][y] == (1 - color) and self.map[x + 1][y] == color)
    dead_down = (0 < x < len(self.map) - 2 and self.map[x - 1][y] == color and self.map[x + 1][y] == (1 - color) and self.map[x + 2][y] == color)
    dead_right = (0 < y < len(self.map) - 2 and self.map[x][y - 1] == color and self.map[x][y + 1] == (1 - color) and self.map[x][y + 2] == color)
    dead_left = (len(self.map) - 1 > y > 1 and self.map[x][y - 2] == color and self.map[x][y - 1] == (1 - color) and self.map[x][y + 1] == color)
    return (dead_up or dead_down or dead_right or dead_left)

  def list_of_dead(self, color, last_move):
    x, y = last_move
    l = []
    if x > 1 and self.is_dead(x - 1, y, color):
      l += [(x - 1, y), (x, y)]
    if x < len(self.map) - 1 and self.is_dead(x + 1, y, color):
      l += [(x, y), (x + 1, y)]
    return l

  def	kill_dead_stones(self, color, last_move):
    l = self.list_of_dead(color, last_move)
    for p in l:
      self.map[p[0]][p[1]] = 0