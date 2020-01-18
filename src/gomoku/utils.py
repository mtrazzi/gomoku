import copy

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


def impact(stone, x, y):
  dx, dy = abs(stone[0] - x), abs(stone[1] - y)
  return (dx < 6 and dy == 0) or (dy < 6 and dx == 0) or (dx == dy and dx < 6)


def were_impacted(stones, x, y):
  return np.any([impact(move, x, y) for move in stones])


def impact_slope(stone, x, y, dx, dy):
  delta_x, delta_y = np.sign(stone[0] - x), np.sign(stone[1] - y)
  return impact(stone, x, y) and dx == delta_x and dy == delta_y


def were_impacted_slope_aux(dx_stone, dy_stone, dx, dy):
  if dx_stone == 0 and dy_stone == 0:
      return True
  if (dx_stone == 0 and not (dx == 0)) or (dy_stone == 0 and not (dy == 0)):
    return False
  if abs(dx) == abs(dy) and not (abs(dx_stone) == abs(dy_stone)):
    return False
  if dx > 0:
    return -4 <= dx_stone <= 4
  elif dx < 0:
    return -4 <= dx_stone <= 4
  else:
    return -4 <= dy_stone <= 4


def were_impacted_slope(stones, x, y, dx, dy):
  for stone in stones:
    dx_stone, dy_stone = x - stone[0], y - stone[1]
    if were_impacted_slope_aux(dx_stone, dy_stone, dx, dy):
      return True
  return False


def nearby_stones(move, board):
  x, y = move
  size = board.size
  nearby = []
  for dx in [-1, 0, 1]:
    for dy in [-1, 0, 1]:
      x_p, y_p = x + dx, y + dy
      if 0 <= x_p < size and 0 <= y_p < size and board.is_empty(x_p, y_p):
        nearby.append((x_p, y_p))
  if (x, y) in nearby:
    nearby.remove((x, y))
  return nearby


def update_child_after_move(game_handler, captures, last_move):
  game_handler.child_list = list(set(game_handler.child_list +
                                 nearby_stones(last_move, game_handler.board)))
  if (last_move[0], last_move[1]) in game_handler.child_list:
    game_handler.child_list.remove((last_move[0], last_move[1]))
  for capture in captures:
    for stone in nearby_stones(capture, game_handler.board):
      if (not is_there_stones_around(game_handler.board.board, *stone) and
          stone in game_handler.child_list):
        game_handler.child_list.remove(stone)
  for capture in captures:
    if capture not in game_handler.child_list:
      game_handler.child_list.append(capture)


def get_player_name(player):
  from gomoku.mcts import MCTSAgent
  from gomoku.minimax import MiniMaxAgent
  from gomoku.agent import Agent
  if isinstance(player, MCTSAgent):
    return "mcts"
  if isinstance(player, MiniMaxAgent):
    return player.algorithm_name
  elif isinstance(player, Agent):
    return "not the best minimax agent"
  else:
    return "human"


def best_values(values, depth, i):
  return values[depth - 1] if i < 2 else values[depth][:i]


def ucb(val, parent_visits, n_visits, ucb_constant=2):
  win_ratio = val / (n_visits + 1)
  exploration = (ucb_constant *
                 np.sqrt(np.log(parent_visits + 1) / (n_visits + 1)))
  # print(f"win_ratio={win_ratio} vs. exploration={exploration}")
  return win_ratio + exploration


def get_attr(attr_name):
  def get_attr_node(node):
    return getattr(node, attr_name)
  return get_attr_node


def dist_sort(move_0, move_list):
  dist = [np.linalg.norm(np.subtract(move_0, move)) for move in move_list]
  return [move for _, move in sorted(zip(dist, move_list))]
