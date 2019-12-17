import numpy as np

SLOPES = np.array([[1, 0], [-1, 1], [0, 1], [1, 1]])


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
  colors = [pos[p[0]][p[1]] for p in coord]
  return (colors[1:] == colors[:-1] and colors[0] == color)


def is_there_stones_around(position, x, y):
  size = position.shape[0]
  return (((x > 0) and
          ((y > 0 and position[x - 1][y - 1] > 0) or
           position[x - 1][y] > 0 or
          (y < size - 1 and position[x - 1][y + 1]))) or
          ((y > 0 and position[x][y - 1] > 0) or
          (position[x][y] > 0) or
          (y < size - 1 and position[x][y + 1])) or
          ((x < size - 1) and
          ((y > 0 and position[x + 1][y - 1] > 0) or
           position[x + 1][y] > 0 or
           (y < size - 1 and position[x + 1][y + 1]))))


def opposite(color):
  return 3 - color


def move(x, y):
  return x - 1, y - 1


def human_move(move):
  return move[0] + 1, move[1] + 1


def count_stones(position, color):
  unique, counts = np.unique(color, return_counts=True)
  return dict(zip(unique, counts))[color]


def indefensible_four(board, coords, color):
  indefensibles = 0
  for i in range(1, 6):
    v, w = coords[i]
    if not board.is_empty(v, w):
      continue
    board.place(v, w, color)
    same = 0
    empty = 0
    for x, y in coords:
      if board.is_empty(x, y):
        if same == 0:
          empty = 1
          continue
        elif same == 4:
          empty += 1
        break
      elif board.is_stone(x, y, color):
        same += 1
      elif not board.is_stone(x, y, color) and same == 0:
        continue
      else:
        break
    if same >= 4 and empty >= 2:
      indefensibles += 1
    board.remove(v, w)
  return indefensibles


def get_player(gameHandler, color, maximizingPlayer):
  players = gameHandler.players
  player = players[0] if players[0].color == color else players[1]
  opponent = players[1] if players[0].color == color else players[0]
  return player if maximizingPlayer else opponent
