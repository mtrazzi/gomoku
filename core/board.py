import numpy as np
import sys
import os

COMB_LIST = [[-1, -1, 1, 1], # distance of 1
            [-1, 0, 1, 0],
            [-1, 1, 1, -1],
            [0, 1, 0, -1],
            [-2, -2, 1, 1], # distance of two starting from top/right
            [-2, 0, 1, 0],
            [-2, 2, 1, -1],
            [0, 2, 0, -1],
            [0, 0, 1, 1], # distance of two starting from , 0
            [0, 0, 1, 0],
            [0, 0, 1, -1],
            [0, 0, 0, -1],
            [0, 0 - 1, 0, 1],
            [1, 0, -1 ,0],
            [1, -1, -1, 1],
            [-1, 0, 1, 0],
            [0, -2, 0, 1]]

class Board(object):
  def __init__(self):
    self.map = self.empty_map(19)
    self.capture_counter = [0, 0]

  def print_map(self):
    dic = {0: ".", 1: "X", 2: "O", 3: "*"}
    self.change_hoshi()
    sys.stdout.write("ₓ\\ʸ")
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
        if i in [3,9,15] and j in [3,9,15] and self.map[i][j] in [0, 3]:
          self.map[i][j] = 3 - self.map[i][j]
    return map

  def	empty_map(self, size):
      return np.zeros((size, size))

  def	add_point(self, color, x, y):
      self.map[x][y] = color

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
    
  def respect_rules(self, color, x, y):
    # test adding x,y and see if it breaks the two two rule
    self.add_point(color, x, y)

    # if it kills stones, it's ok to have free threes
    result = self.list_of_dead(color, (x,y)) or not self.two_free_threes(x, y)

    # put back the blank
    self.add_point(0, x, y)
    return result

  def two_free_threes(self, x, y):
    def aux(x, y, dx, dy):
      m = self.map
      x_0, y_0, x_1, y_1, x_2, y_2, x_3, y_3, x_4, y_4 = x, y, x + dx, y + dy, x + 2 * dx, y + 2 * dy, x + 3 * dx, y + 3 * dy, x + 4 * dx, y + 4 * dy
      x_min, x_max, y_min, y_max = min(x_0, x_4), max(x_0, x_4), min(y_0, y_4), max(y_0, y_4)
      return (x_min >= 0 and x_max <= len(m) - 1 and
             y_min >= 0 and y_max <= len(m) - 1 and
             m[x_1][y_1] == m[x_2][y_2] == m[x_3][y_3] and
             m[x_0][y_0] == m[x_4][y_4] == 0)
    count = 0
    for comb in COMB_LIST:
      count += aux(x + comb[0], y + comb[1], comb[2], comb[3])
    return count >= 2

  def get_input(self):
    user_input = ""
    while (user_input != "exit()" and (not self.is_valid_input(user_input))):
      os.system("clear")
      self.print_map()
      if (user_input != ""):
        print("Move badly formated : must type \"x y\" with x and y integers")
        print("Example : \"2 3\"")
        print("Intersection must be empty (must be \'.\' or *)")
      user_input = input("Your next move (type \"exit()\" to quit): $>")
    if (user_input == "exit()"):
      sys.exit()
    return (int(user_input.split(None)[0]), int(user_input.split(None)[1]))
    
  def is_dead(self, x ,y, c):
    m = self.map
    if not m[x][y] == c:
      return False
    dead_up = (len(m) - 1 > x > 1 and m[x - 2][y] == (3 - c) and m[x - 1][y] == c and m[x + 1][y] == (3 - c))
    dead_down = (0 < x < len(m) - 2 and m[x - 1][y] == (3 - c) and m[x + 1][y] == c and m[x + 2][y] == (3 - c))
    dead_right = (0 < y < len(m) - 2 and m[x][y - 1] == (3 - c) and m[x][y + 1] == c and m[x][y + 2] == (3 - c))
    dead_left = (len(m) - 1 > y > 1 and m[x][y - 2] == (3 - c) and m[x][y - 1] == c and m[x][y + 1] == (3 - c))
    return (dead_up or dead_down or dead_right or dead_left)

  def list_of_dead(self, color, last_move):
    x, y = last_move
    l = []
    if x > 1 and self.is_dead(x - 1, y, color):
      l += [(x - 1, y), (x - 2, y)]
    elif x < len(self.map) - 1 and self.is_dead(x + 1, y, color):
      l += [(x + 1, y), (x + 2, y)]
    elif y > 1 and self.is_dead(x, y - 1, color):
      l += [(x, y - 1), (x, y - 2)]
    elif y < len(self.map) - 1 and self.is_dead(x, y + 1, color):
      l += [(x, y + 1), (x, y + 2)]
    return l

  def	kill_dead_stones(self, color, last_move):
    l = self.list_of_dead(color, last_move)
    #TODO: increment self.capture counter and maybe condition for win
    for p in l:
      self.map[p[0]][p[1]] = 0