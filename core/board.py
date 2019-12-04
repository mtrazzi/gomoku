import numpy as np
import sys
import os

import copy

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

FIVE_LIST = [[1, 0], [-1, 1], [0, 1], [1, 1]]

class Board(object):
  def __init__(self, size=19):
    self.map = self.empty_map(size)
    self.size = size
    self.capture_counter = [0, 0]
    self.color = 1 # color of the player to move
    self.dic = {0: ".", 1: "X", 2: "O", 3: "*"}

  def print_map(self):
    self.change_hoshi()
    sys.stdout.write("ₓ\\ʸ")
    for j in range(self.size):
      sys.stdout.write("%2d " % (j + 1))
    print()
    for i in range(self.size):
      sys.stdout.write("%2d " % (i + 1))
      for x in self.map[i]:
        sys.stdout.write("%2c " % self.dic[x])
      print()
    print(f'X: {self.capture_counter[0]} captured')
    print(f'O: {self.capture_counter[1]} captured')
    self.change_hoshi()

  def	change_hoshi(self):
    size = self.size
    for i in (range(size)):
      for j in (range(size)):
        if i in [3,9,15] and j in [3,9,15] and self.map[i][j] in [0, 3]:
          self.map[i][j] = 3 - self.map[i][j]
    return map

  def	empty_map(self, size):
      return np.zeros((size, size))

  def	add_point(self, color, x, y):
    self.map[x][y] = color
    
  def do_move(self, x, y):
    self.add_point(self.color, x, y)
    # kill stones of opposite colors
    self.kill_dead_stones(3 - self.color, (x,y))
    done = self.is_done()
    self.color = 3 - self.color
    self.print_map()
    return done

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
    return ((x > 0 and x <= self.size) and (y > 0 and y <= self.size) \
    and (self.map[x - 1][y - 1] == 0))
    
  def respect_rules(self, x, y):
    # intersection must be empty
    if (self.map[x][y] > 0):
      return False

    # test adding x,y and see if it breaks the two two rule
    self.add_point(self.color, x, y)

    # if it kills stones, it's ok to have free threes
    result = self.list_of_dead(self.color, (x,y)) or not self.two_free_threes(x, y)

    # put back the blank
    self.add_point(0, x, y)
    return result
  
  def coordinates(self, x, y, dx, dy):
    return [(x, y), (x + dx, y + dy), (x + 2 * dx, y + 2 * dy), (x + 3 * dx, y + 3 * dy), (x + 4 * dx, y + 4 * dy)]

  def aux(self, x, y, dx, dy, blank=0):
    m = self.map
    (x_0, y_0), (x_1, y_1), (x_2, y_2), (x_3, y_3), (x_4, y_4) = self.coordinates(x, y, dx, dy)
    x_min, x_max, y_min, y_max = min(x_0, x_4), max(x_0, x_4), min(y_0, y_4), max(y_0, y_4)
    return (x_min >= 0 and x_max <= len(m) - 1 and
            y_min >= 0 and y_max <= len(m) - 1 and
            m[x_1][y_1] == m[x_2][y_2] == m[x_3][y_3] and
            m[x_0][y_0] == m[x_4][y_4] == (0 if blank == 0 else m[x_1][y_1]))

  def two_free_threes(self, x, y):
    count = 0
    for comb in COMB_LIST:
      count += self.aux(x + comb[0], y + comb[1], comb[2], comb[3])
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
    return (int(user_input.split(None)[0]) - 1, int(user_input.split(None)[1]) - 1)
    
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
    elif x < self.size - 1 and self.is_dead(x + 1, y, color):
      l += [(x + 1, y), (x + 2, y)]
    elif y > 1 and self.is_dead(x, y - 1, color):
      l += [(x, y - 1), (x, y - 2)]
    elif y < self.size - 1 and self.is_dead(x, y + 1, color):
      l += [(x, y + 1), (x, y + 2)]
    return l

  def	kill_dead_stones(self, color, last_move):
    l = self.list_of_dead(color, last_move)
    self.capture_counter[(3 - color) - 1] += len(l)
    for p in l:
      self.map[p[0]][p[1]] = 0

  def is_done(self):
    # if someone reached 10 captures, game is done
    if self.capture_counter[0] >= 10 or self.capture_counter[1] >= 10:
      return True
    coord = self.five_aligned()
    # if five aligned were found, it only counts if opponent cannot do anything
    if coord:
      return not self.can_capture_five(coord) and not self.can_reach_ten(3 - self.color)
  
  #TODO: possible to optimize x600 if check only for last move + specific color
  def five_aligned(self):
    for x in range(self.size):
      for y in range(self.size):
        for (dx, dy) in FIVE_LIST:
          if self.map[x][y] > 0 and self.aux(x, y, dx, dy, self.map[x][y]):
            return self.coordinates(x, y, dx, dy)
    return None
  
  def can_capture_five(self, coord):
    to_capture_col = self.map[coord[0][0]][coord[0][1]]
    for x in range(self.size):
      for y in range(self.size):
        if self.map[x][y] == 0:
          self.add_point(3 - to_capture_col, x, y)
          dead_list = self.list_of_dead(to_capture_col, (x,y))
          for dead in dead_list:
            if dead in coord:
              return True
          self.add_point(0, x, y)
    return False

  def can_reach_ten(self, color):
    if self.capture_counter[color - 1] < 8:
      return False
    for x in range(self.size):
      for y in range(self.size):
        if self.map[x][y] == 0:
          self.add_point(color, x, y)
          l = self.list_of_dead(3 - color, (x,y))
          self.add_point(0, x, y)
          if l:
            return True
    return False

  def child(self):
    """Returns list of valid moves from current position for player self.color."""
    l = []
    for x in range(self.size):
      for y in range(self.size):
        if self.respect_rules(x, y):
          new_board = copy.deepcopy(self) # ugly now, maybe there is more optimized way to do it
          new_board.do_move(x, y)
          l.append(new_board)
    return l