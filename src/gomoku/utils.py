import numpy as np

def coordinates(x, y, dx, dy, nb_consecutive=5):
  """Coordinates of consecutive intersections from (x,y) directed by (dx,dy)."""
  return [(x + i * dx, y + i * dy) for i in range(nb_consecutive)]

def boundaries(coord):
  x_0, y_0, x_1, y_1 = coord[0][0], coord[0][1], coord[-1][0], coord[-1][1]
  return min(x_0, x_1), max(x_0, x_1), min(y_0, y_1), max(y_0, y_1)

def all_equal(coord, pos, color):
  """Check if all the given coordinates are equal to color in pos."""
  x_min, x_max, y_min, y_max = boundaries(coord)
  if not (x_min >= 0 and x_max <= len(pos) - 1 and
          y_min >= 0 and y_max <= len(pos) - 1):
    return False
  l = [pos[p[0]][p[1]] for p in coord]
  return (l[1:] == l[:-1] and l[0] == color)

def is_there_stones_around(position, x, y):
  size = position.shape[0]
  return (((x > 0) and 
          ((y > 0 and                position[x - 1][y - 1] > 0) or
                                     position[x - 1][y] > 0 or
          (y < size - 1 and          position[x - 1][y + 1]))) or
          ((y > 0 and                position[x][y - 1] > 0) or
                                    (position[x][y] > 0) or
          (y < size - 1 and          position[x][y + 1])) or
          ((x < size - 1) and
          ((y > 0 and                position[x + 1][y - 1] > 0) or
                                     position[x + 1][y] > 0 or
          (y < size - 1 and position[x + 1][y + 1]))))