import numpy as np

from gomoku.heuristics import SLOPES
from gomoku.utils import all_equal, coordinates


class Rules(object):
  """Class Rules
  """
  def __init__(self):
    return

  def can_capture(self, board, x, y, player):
    coords = np.append(SLOPES, SLOPES * -1, axis=0)
    size = board.size
    captures = []
    for dx, dy in coords:
      bounds = np.array([(x + dx * 3), (y + dy * 3)])
      if (bounds < [0, 0]).any() or (bounds >= [size, size]).any():
        continue
      if not board.is_stone(*bounds, player):
        continue

      stone1 = [(x + dx), (y + dy)]
      stone2 = [(x + dx * 2), (y + dy * 2)]
      if not board.is_stone(*stone1, player)     \
         and not board.is_stone(*stone2, player) \
         and not board.is_empty(*stone1)         \
         and not board.is_empty(*stone2):
        captures += [stone1, stone2]
    return captures

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

    Return
    ------
    captures: list
      List of coordinates for the captured stones
    """
    captures = self.can_capture(board, *player.last_move, player)
    for stone in captures:
      board.remove(*stone)
      player.captures += 1
    return captures

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
    for dx, dy in SLOPES:
      for _x, _y in coordinates(x, y, -dx, -dy, 5):
        if all_equal(coordinates(_x, _y, dx, dy, 5), board.board, player.stone):
          return True
    return False

  def check_double_threes(self, board, lst, player):
    threes = 0
    for l in lst:
      offset = l[0] - l[1]
      new_lst = np.append([l[0] + offset], l, axis=0)
      new_lst = np.append(new_lst, [l[-1] - offset], axis=0)
      if (new_lst >= [board.size, board.size]).any():
        continue
      if (new_lst < [0, 0]).any():
        continue

      for i in range(1, 6):
        _x, _y = new_lst[i]
        if not board.is_empty(_x, _y):
          continue
        board.place(_x, _y, player)
        same = 0
        empty = 0
        for x, y in new_lst:
          if board.is_empty(x, y):
            if same == 0:
              empty = 1
              continue
            elif same == 4:
              empty += 1
            break
          elif board.is_stone(x, y, player):
            same += 1
          elif not board.is_stone(x, y, player) and same == 0:
            continue
          else:
            break
        if same >= 4 and empty >= 2:
          threes += 1
        board.remove(_x, _y)
    return threes <= 1

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
    (x, y), threes, size = player.last_move, [], board.size
    for dx, dy in SLOPES:
      i = 0
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
          same += board.is_stone(v, w, player)
          free += board.is_empty(v, w)
        if free == 2 and same == 3:
          threes.append(coords)
          if i == 0:
            i = 3
          else:
            break
        i += 1
    return self.check_double_threes(board, np.array(threes), player)

  def check_captures(self, board, player):
    for x in range(board.size):
      for y in range(board.size):
        if self.can_capture(board, x, y, player):
          return True
    return False

  def can_break_five(self, gh, player, opponent):
    """Assuming that there are five aligned, returns True if player can break
    all the five alignments from his opponent."""
    for x in range(gh.board.size):
      for y in range(gh.board.size):
        if (gh.board.is_empty(x, y) and
            self.can_capture(gh.board, x, y, player)):
          gh.do_move(x, y, player)
          if not self.aligned_win(gh.board, opponent):
            gh.undo_last_move(player)
            return True
          gh.undo_last_move(player)

  def can_reach_ten(self, board, player):
    return player.captures >= 8 and self.check_captures(board, player)

  def check_winner(self, game_handler):
    board, players = game_handler.board, game_handler.players
    for (player, opponent) in [players, players[::-1]]:
      if player.captures >= 10:
        return player

      if self.aligned_win(board, player):
        if (player.aligned_five_prev or
           not (self.can_reach_ten(board, opponent) or
                self.can_break_five(game_handler, opponent, player))):
          return player
        player.aligned_five_prev = True
      else:
        player.aligned_five_prev = False
    return None
