class Rules(object):
  """Class Rules
  """
  def __init__(self):
    return

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
      if  not board.is_stone(stone1_x, stone1_y, player) \
      and not board.is_stone(stone2_x, stone2_y, player) \
      and not board.is_empty(stone1_x, stone1_y)         \
      and not board.is_empty(stone2_x, stone2_y):
          board.remove(stone1_x, stone1_y)
          board.remove(stone2_x, stone2_y)
          player.captures += 2
          dead_list.append([(stone1_x, stone1_y), (stone2_x, stone2_y)])
    return dead_list

  def aligned_win(self, board, player):
    """Manage the Aligned 5 Rule
    The player win if he alignes 5 stone of his color

    Parameters
    ----------
    board: Board
      The current board
    player: Player
      The current player
    """
    x, y = player.last_move
    aligned = False
    for offset_x, offset_y in COORDS_LIST[::2]:
      for i in range(5):
        _x = x - i * offset_x
        _y = y - i * offset_y
        bound_x = _x + offset_x * 4
        bound_y = _y + offset_y * 4
        if _x < 0 or _x >= board.size or _y < 0 or _y >= board.size:
          continue
        if bound_x < 0 or bound_x >= board.size \
        or bound_y < 0 or bound_y >= board.size:
          continue
        aligned = True
        coords = [(_x + offset_x * 0, _y + offset_y * 0),
                  (_x + offset_x * 1, _y + offset_y * 1),
                  (_x + offset_x * 2, _y + offset_y * 2),
                  (_x + offset_x * 3, _y + offset_y * 3),
                  (_x + offset_x * 4, _y + offset_y * 4)]
        for v, w in coords:
          if not board.is_stone(v, w, player):
            aligned = False
            break
        if aligned:
          return True
    return False

  def no_double_threes(self, board, player):
    x, y = player.last_move
    threes = 0
    for offset_x, offset_y in COORDS_LIST:
      for i in range(5):
        _x = x - i * offset_x
        _y = y - i * offset_y
        bound_x = _x + offset_x * 4
        bound_y = _y + offset_y * 4
        if _x < 0 or _x >= board.size or _y < 0 or _y >= board.size:
          continue
        if bound_x < 0 or bound_x >= board.size \
        or bound_y < 0 or bound_y >= board.size:
          continue
        free = 0
        same = 0
        coords = [(_x + offset_x * 0, _y + offset_y * 0),
                  (_x + offset_x * 1, _y + offset_y * 1),
                  (_x + offset_x * 2, _y + offset_y * 2),
                  (_x + offset_x * 3, _y + offset_y * 3),
                  (_x + offset_x * 4, _y + offset_y * 4)]
        for j in range(5):
          v, w = coords[j]
          if board.is_stone(v, w, player):
            same += 1
          elif board.is_empty(v, w):
            free += 1
        # print(f"Free: {free}, Same: {same}")
        if free == 2 and same == 3:
          threes += 1
          break
    # print(f"Threes: {threes}")
    return threes <= 1

  def check_winner(self, board, players):
    for player in players:
      if self.aligned_win(board, player):
        return player
    return None

COORDS_LIST = [
  ( 0,  1),
  ( 0, -1),
  ( 1,  0),
  (-1,  0),
  ( 1,  1),
  (-1, -1),
  ( 1, -1),
  (-1,  1)
]
