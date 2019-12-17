import numpy as np

from gomoku.rules import Rules
from gomoku.utils import SLOPES, boundaries, coordinates, get_player

SCORE_MAP = {
  'potential five': 25,
  'no potential five': 0,

  'aligned <= 0': 0,
  'aligned == 1': 0,
  'aligned == 2': 25,
  'aligned == 3': 250,
  'aligned == 4': 500,
  'aligned >= 5': 10000,

  'free <= 0': 0,
  'free == 1': 1,
  'free == 2': 2,
  'free == 3': 3,
  'free >= 4': 4,

  'potential captures <= 0': 0,
  'potential captures == 1': 250,
  'potential captures >= 2': 500,

  'captures <= 0': 0,
  'captures <= 2': 500,
  'captures <= 4': 1000,
  'captures <= 6': 2500,
  'captures <= 8': 5000,
  'captures >= 10': 10000,

  'indefensibles <= 0': 0,
  'indefensibles >= 1': 1000,
}


def score_potential_alignment_win(board, x, y, color):
  """
  Does the heuristic check whether an alignment has enough space
  to develop into a 5-in-a-row ?
  """
  potential_five = [False, False, False, False]
  for idx, (dx, dy) in enumerate(SLOPES):
    for _x, _y in coordinates(x, y, -dx, -dy, 5):
      potential = True
      for v, w in coordinates(_x, _y, dx, dy, 5):
        if v < 0 or w < 0 or v >= board.size or w >= board.size:
          potential = False
          break
        if board.is_stone(v, w, 3 - color):
          potential = False
          break
      if potential:
        potential_five[idx] = True
        break

  score = 0
  for value in potential_five:
    if not value:
      score += SCORE_MAP['no potential five']
    else:
      score += SCORE_MAP['potential five']
  return score


def score_alignements(board, x, y, color):
  """
  Does the heuristic take current alignments into account ?
  Does the heuristic weigh an alignment according to its freedom
  (Free, half-free, flanked) ?
  """
  aligned = [1, 1, 1, 1]
  free = [0, 0, 0, 0]
  for idx, (dx, dy) in enumerate(SLOPES):
    _x, _y = x + dx, y + dy
    while 0 <= _x < board.size and 0 <= _y < board.size:
      if board.is_stone(_x, _y, color):
        aligned[idx] += 1
      elif board.is_empty(_x, _y):
        free[idx] += 1
      else:
        break
      _x, _y = _x + dx, _y + dy

  for idx, (dx, dy) in enumerate(SLOPES):
    _x, _y = x - dx, y - dy
    while 0 <= _x < board.size and 0 <= _y < board.size:
      if board.is_stone(_x, _y, color):
        aligned[idx] += 1
      elif board.is_empty(_x, _y):
        free[idx] += 1
      else:
        break
      _x, _y = _x - dx, _y - dy

  score = 0
  for value in aligned:
    if value <= 0:
      score += SCORE_MAP['aligned <= 0']
    elif value == 1:
      score += SCORE_MAP['aligned == 1']
    elif value == 2:
      score += SCORE_MAP['aligned == 2']
    elif value == 3:
      score += SCORE_MAP['aligned == 3']
    elif value == 4:
      score += SCORE_MAP['aligned == 4']
    elif value >= 5:
      score += SCORE_MAP['aligned >= 5']

  for value in free:
    if value <= 0:
      score += SCORE_MAP['free <= 0']
    elif value == 1:
      score += SCORE_MAP['free == 1']
    elif value == 2:
      score += SCORE_MAP['free == 2']
    elif value == 3:
      score += SCORE_MAP['free == 3']
    elif value >= 4:
      score += SCORE_MAP['free >= 4']
  return score


def score_potential_captures(board, x, y, color):
  """Does the heuristic take potential captures into account ?"""
  potential_captures = [0, 0, 0, 0]
  for idx, (dx, dy) in enumerate(SLOPES):
    right = coordinates(x, y, dx, dy, 4)
    x_min, x_max, y_min, y_max = boundaries(right)
    if x_min < 0 or x_max >= board.size:
      continue
    if y_min < 0 or y_max >= board.size:
      continue
    if not board.is_empty(*right[3]):
      continue
    if not board.is_stone(*right[2], 3 - color):
      continue
    if not board.is_stone(*right[1], 3 - color):
      continue
    potential_captures[idx] += 1

  for idx, (dx, dy) in enumerate(SLOPES):
    left = coordinates(x, y, -dx, -dy, 4)
    x_min, x_max, y_min, y_max = boundaries(right)
    if x_min < 0 or x_max >= board.size:
      continue
    if y_min < 0 or y_max >= board.size:
      continue
    if not board.is_empty(*left[3]):
      continue
    if not board.is_stone(*left[2], 3 - color):
      continue
    if not board.is_stone(*left[1], 3 - color):
      continue
    potential_captures[idx] += 1

  score = 0
  for value in potential_captures:
    if value <= 0:
      score += SCORE_MAP['potential captures <= 0']
    elif value == 1:
      score += SCORE_MAP['potential captures == 1']
    elif value >= 2:
      score += SCORE_MAP['potential captures >= 2']
  return score


def score_captures(player):
  """Does the heuristic take current captured stones into account ?"""
  score = 0
  if player.captures <= 0:
    score += SCORE_MAP['captures <= 0']
  elif player.captures <= 2:
    score += SCORE_MAP['captures <= 2']
  elif player.captures <= 4:
    score += SCORE_MAP['captures <= 4']
  elif player.captures <= 6:
    score += SCORE_MAP['captures <= 6']
  elif player.captures <= 8:
    score += SCORE_MAP['captures <= 8']
  else:
    score += SCORE_MAP['captures >= 10']
  return score


def score_figures(board, x, y, color):
  """Does the heuristic check for advanteageous combinations ?"""
  threes, size = [], board.size
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
        same += board.is_stone(v, w, color)
        free += board.is_empty(v, w)
      if free == 2 and same == 3:
        threes.append(coords)
        if i == 0:
          i = 3
        else:
          break
      i += 1
  indefensibles = Rules.check_double_threes(board, np.array(threes), color)

  score = 0
  if indefensibles <= 0:
    score += SCORE_MAP['indefensibles <= 0']
  else:
    score += SCORE_MAP['indefensibles >= 1']
  return score


def score_opponent(board, player):
  """Does the heuristic take both players into account ?"""
  score = 0
  score += score_alignements(board, *player.last_move, player.color)
  score += score_potential_alignment_win(board, *player.last_move, player.color)
  score += score_potential_captures(board, *player.last_move, player.color)
  score += score_captures(player)
  score += score_figures(board, *player.last_move, player.color)
  return score


def score_past():
  """
  Does the heuristic take past player actions into account to identify
  patterns and weigh board states accordingly ?
  """
  score = 0
  return score


def heuristic(gameHandler, color, maximizing):
  player = get_player(gameHandler, color, maximizing)
  opponent = get_player(gameHandler, color, not maximizing)
  board = gameHandler.board

  score = 0
  score += score_alignements(board, *player.last_move, player.color)
  score += score_potential_alignment_win(board, *player.last_move, player.color)
  score += score_potential_captures(board, *player.last_move, player.color)
  score += score_captures(player)
  score += score_figures(board, *player.last_move, player.color)
  score -= score_opponent(board, opponent)
  # score += score_past()
  return score


# from gomoku.heuristics import (capture_heuristic, past_heuristic,
#                                simple_heuristic)

# def heuristic(gameHandler, color, maximizing):
#   player = get_player(gameHandler, color, maximizing)
#   opponent = get_player(gameHandler, color, not maximizing)
#   board = gameHandler.board.board

#   return (simple_heuristic(board, color, maximizing) +
#           capture_heuristic(player, opponent, player.color == color) +
#           (1 / 100) * past_heuristic(opponent.last_move, player.last_move))
