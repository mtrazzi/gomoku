from gomoku.heuristics import nb_consecutives
from gomoku.utils import coordinates, all_equal


class Rules(object):
  """Class Rules
  """
  def __init__(self):
    return

  def can_capture(self, board, x, y, player):
    for offset_x, offset_y in COORDS_LIST:
      bound_x = x + offset_x * 3
      bound_y = y + offset_y * 3
      if bound_x < 0 or bound_x >= board.size \
         or bound_y < 0 or bound_y >= board.size:
        continue
      if not board.is_stone(bound_x, bound_y, player):
        continue

      stone1_x, stone1_y = x + offset_x,     y + offset_y
      stone2_x, stone2_y = x + offset_x * 2, y + offset_y * 2
      if not board.is_stone(stone1_x, stone1_y, player) \
         and not board.is_stone(stone2_x, stone2_y, player) \
         and not board.is_empty(stone1_x, stone1_y)         \
         and not board.is_empty(stone2_x, stone2_y):
        return True
    return False

  def capture(self, board, player):
    """Manage the Capture Rule
    Only two stone can be "captured" at the same time only if they are
    surrounded by the other player stones.
    Example:
    'X O O X', here 'O O' is captured by X

    Parameters
    ----------
    board: Board
      The current board
    player: Player
      The current player
    """
    dead_list = []
    x, y = player.last_move
    for offset_x, offset_y in COORDS_LIST:
      bound_x = x + offset_x * 3
      bound_y = y + offset_y * 3
      if bound_x < 0 or bound_x >= board.size \
         or bound_y < 0 or bound_y >= board.size:
        continue
      if not board.is_stone(bound_x, bound_y, player):
        continue

      stone1_x, stone1_y = x + offset_x,     y + offset_y
      stone2_x, stone2_y = x + offset_x * 2, y + offset_y * 2
      if not board.is_stone(stone1_x, stone1_y, player) \
         and not board.is_stone(stone2_x, stone2_y, player) \
         and not board.is_empty(stone1_x, stone1_y)         \
         and not board.is_empty(stone2_x, stone2_y):
          board.remove(stone1_x, stone1_y)
          board.remove(stone2_x, stone2_y)
          player.captures += 2
          dead_list += [(stone1_x, stone1_y), (stone2_x, stone2_y)]
    return dead_list

  def aligned_win(self, board, player):
    """Manage the Aligned 5 Rule
    The player wins if he aligns 5 stone of his color

    Parameters
    ----------
    board: Board
      The current board
    player: Player
      The current player
    """
    x, y = player.last_move
    for dx, dy in COORDS_LIST[::2]:
      for _x, _y in coordinates(x, y, -dx, -dy, 5):
        if all_equal(coordinates(_x, _y, dx, dy, 5), board.board, player.stone):
          return True
    return False

  def no_double_threes(self, board, player):
    """Manage the No Double Free Threes Rule
    The player must not play a move that introduces two free-three alignments

    Parameters
    ----------
    board: Board
      The current board
    player: Player
      The current player
    """
    (x, y), threes, size = player.last_move, 0, board.size
    for dx, dy in COORDS_LIST[::2]:
      i = 0
      while i != 5:
        _x, _y = x - i * dx, y - i * dy
        bound_x, bound_y = _x + dx * 4, _y + dy * 4
        if (_x < 0 or _x >= size or _y < 0 or _y >= size or
            bound_x < 0 or bound_x >= size or bound_y < 0 or bound_y >= size):
          i += 1
          continue
        free = same = 0
        coords = coordinates(_x, _y, dx, dy)
        for j in range(5):
          v, w = coords[j]
          same += board.is_stone(v, w, player)
          free += board.is_empty(v, w)
        if free == 2 and same == 3:
          threes += 1
          if i == 0:
            i = 4
          else:
            break
        i += 1
    return threes <= 1

  def check_captures(self, board, player):
    for i in range(board.size):
      for j in range(board.size):
        if self.can_capture(board, i, j, player):
          return True
    return False

  def check_winner(self, board, players):
    for player in players:
      if player.captures >= 10:
        return player

    if self.aligned_win(board, players[0]):
      if not self.check_captures(board, players[1]) and players[1].captures < 8:
        return players[0]
      else:
        return players[1]

    if self.aligned_win(board, players[1]):
      if not self.check_captures(board, players[0]) and players[0].captures < 8:
        return players[1]
      else:
        return players[0]

    return None


COORDS_LIST = [
  (0,  1),
  (0, -1),
  (1,  0),
  (-1,  0),
  (1,  1),
  (-1, -1),
  (1, -1),
  (-1,  1),
]
