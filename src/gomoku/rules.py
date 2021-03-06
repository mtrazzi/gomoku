import numpy as np

from gomoku.utils import SLOPES, all_equal, coordinates, indefensible_four


class Rules(object):
  """Class Rules
  """
  def __init__(self):
    return

  @staticmethod
  def can_capture(board, x, y, player):
    player.last_move = (x, y)
    return len(Rules.capture(board, player, remove=False)) > 0

  @staticmethod
  def capture(board, player, remove=True):
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

    Return
    ------
    captures: list
      List of coordinates for the captured stones
    """
    coords = np.append(SLOPES, SLOPES * -1, axis=0)
    (x, y), size = player.last_move, board.size
    captures = []
    for dx, dy in coords:
      bounds = x + 3 * dx, y + 3 * dy
      if not (0 <= bounds[0] < size and 0 <= bounds[1] < size):
        continue
      if board.board[bounds[0]][bounds[1]] != player.color:
        continue
      stone1 = ((x + dx), (y + dy))
      stone2 = ((x + dx * 2), (y + dy * 2))
      if not board.is_stone(*stone1, player.color)     \
         and not board.is_stone(*stone2, player.color) \
         and not board.is_empty(*stone1)         \
         and not board.is_empty(*stone2):
        captures += [stone1, stone2]
    if remove:
      for stone in captures:
        board.remove(*stone)
        player.captures += 1
    return captures

  @staticmethod
  def aligned_win(board, player):
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
    for dx, dy in SLOPES:
      for _x, _y in coordinates(x, y, -dx, -dy, 5):
        if all_equal(coordinates(_x, _y, dx, dy, 5), board.board, player.color):
          return True
    return False

  @staticmethod
  def aligned_coords(board, player):
    x, y = player.last_move
    for dx, dy in SLOPES:
      for _x, _y in coordinates(x, y, -dx, -dy, 5):
        coords = coordinates(_x, _y, dx, dy, 5)
        if all_equal(coords, board.board, player.color):
          return coords
    return []

  @staticmethod
  def check_double_threes(board, threes_dict, color):
    threes = 0
    for lst in threes_dict.values():
      for i in range(len(lst)):
        l = lst[i]
        offset = l[0] - l[1]
        new_lst = np.append([l[0] + offset], l, axis=0)
        new_lst = np.append(new_lst, [l[-1] - offset], axis=0)
        if (new_lst >= [board.size, board.size]).any():
          continue
        if (new_lst < [0, 0]).any():
          continue
        indefensibles = indefensible_four(board, new_lst, color)
        if indefensibles > 0:
          threes += indefensibles
          if i == 0 and len(lst) == 5:
            i = 3
          else:
            break
    return threes

  @staticmethod
  def no_double_threes(board, player):
    """Manage the No Double Free Threes Rule
    The player must not play a move that introduces two free-three alignments

    Parameters
    ----------
    board: Board
      The current board
    player: Player
      The current player
    """
    (x, y), threes, size = player.last_move, {}, board.size
    for idx, (dx, dy) in enumerate(SLOPES):
      i = 0
      threes[idx] = []
      while i != 5:
        _x, _y = (x - i * dx), (y - i * dy)
        bound_x, bound_y = (_x + dx * 4), (_y + dy * 4)
        if (_x < 0 or _x >= size or _y < 0 or _y >= size or
            bound_x < 0 or bound_x >= size or bound_y < 0 or bound_y >= size):
          i += 1
          continue
        free = same = 0
        coords = coordinates(_x, _y, dx, dy)
        for j in range(5):
          v, w = coords[j]
          same += board.is_stone(v, w, player.color)
          free += board.is_empty(v, w)
        if free == 2 and same == 3:
          threes[idx].append(np.array(coords))
        i += 1
    return Rules.check_double_threes(board, threes, player.color) <= 1

  @staticmethod
  def check_captures(board, player):
    for x in range(board.size):
      for y in range(board.size):
        if Rules.can_capture(board, x, y, player):
          return True
    return False

  @staticmethod
  def can_break_five(board, player, opponent):
    """Assuming that there are five aligned, returns True if player can break
    all the five alignments from his opponent."""
    aligned = Rules.aligned_coords(board, opponent)
    for x in range(board.size):
      for y in range(board.size):
        if board.is_empty(x, y):
          player.last_move = (x, y)
          captures = Rules.capture(board, player, remove=False)
          if len(set(captures) & set(aligned)):
            return True
    return False

  @staticmethod
  def can_reach_ten(board, player):
    return player.captures >= 8 and Rules.check_captures(board, player)

  @staticmethod
  def check_winner(board, players):
    for player in players:
      if Rules.aligned_win(board, player) and player.aligned_five_prev:
        return player
    for (player, opponent) in [players, players[::-1]]:
      if player.captures >= 10:
        return player

      if Rules.aligned_win(board, player):
        if (player.aligned_five_prev or
           not (Rules.can_reach_ten(board, opponent) or
                Rules.can_break_five(board, opponent, player))):
          return player
        player.aligned_five_prev = True
      else:
        player.aligned_five_prev = False
    return None

  @staticmethod
  def check_winner_basic(board, players):
    for player in players:
      if Rules.aligned_win(board, player):
        return player
    return None
