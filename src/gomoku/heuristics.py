import numpy as np
import time

from gomoku.utils import SLOPES, all_equal, coordinates, opposite, were_impacted_slope

import builtins

try:
    builtins.profile
except AttributeError:
    # No line profiler, provide a pass-through version
    def profile(func): return func
    builtins.profile = profile

SCORE = {
  'XXXXX': 1e16,
  'OXXXX.': 1e14,
  'XXX.X': 1e14,
  'OOO.O': 1e1,
  '.XXXX.': 1e14,
  '.OOOO.': 1e13,
  '.XXX.': 1e10,
  '.OOO.': 5e4,
  'OXXX.': 1e2,
  'XOOOO.': 1e1,
  'XOOO.': 1e1,
  '.XX.': 5,
  '.X.': 1,
  'OX.': 0.5,
  'no open ends': 0,
  'OXX.': -1e4,
  'XOO.': -1e8,
  'multiple_threats': 1e8,
  'stone_captured': 1e12,
}

def nb_consecutives(x, y, dx, dy, position, color):
  """Maximum number of consecutive stones of color `color` in the board position
  `position`,starting from (x,y) and using slope (dx, dy).

  Parameters
  ----------
  x: int
    x-coordinate of the start position
  y: int
    x-coordinate of the start position
  dx: int
    x-coordinate slope
  dy: int
    y-coordinate slope
  position: numpy.ndarray
    position of the board
  color:
    what color we want the consecutive stones to be

  Return
  ------
  max_consec: int
    Max. number of consecutive stones of color starting at x,y, with slope dx/dy
  """
  # don't start counting if you're not the first stone of a series
  if ((0 <= x - dx < len(position)) and (0 <= y - dy < len(position))
      and position[x - dx][y - dy] == color):
    return 0
  # check what is the biggest nb_coordinates that you can fit in direction dx/dy
  nb_consec = 0
  while position[x][y] == color and (0 <= x < len(position)) and (0 <= y < len(position)):
    nb_consec += 1
    x += dx
    y += dy
  return nb_consec


def nb_open_ends(x, y, dx, dy, nb_consec, position):
  """Number of empty intersections (0, 1 or 2) next to the `nb_consec` stones
  (starting from (x,y) and using slope (dx, dy)) in the board position
  `position`.

  Parameters
  ----------
  x: int
    x-coordinate of the start position
  y: int
    x-coordinate of the start position
  dx: int
    x-coordinate slope
  dy: int
    y-coordinate slope
  nb_consec: int
    Maximum number of consecutive stones of color `color` in the board position
    `position`,starting from (x,y) and using slope (dx, dy).
  position: numpy.ndarray
    Position of the board

  Return
  ------
  ends: int
    number of empty intersections next to the consecutive stones
  """
  m = len(position)
  coord = coordinates(x, y, dx, dy, nb_consec)
  # compute coordinates of open ends candidates before and after given points
  p1 = [coord[0][0] - dx, coord[0][1] - dy]
  p2 = [coord[-1][0] + dx, coord[-1][1] + dy]
  ends = 0
  ends += (0 <= p1[0] < m and 0 <= p1[1] < m) and position[p1[0]][p1[1]] == 0
  ends += (0 <= p2[0] < m and 0 <= p2[1] < m) and position[p2[0]][p2[1]] == 0
  return ends

def is_this_a_threat(x, y, dx, dy, position, color):
  if position[x][y] == color:
    return is_this_a_threat_2(x, y, dx, dy, position, color)
  else:
    return is_this_a_threat_1(x - dx, y - dy, dx, dy, position, color) #FIXME: return False directly instead of calling is_this_a_threat_1? Change how this is called in the score_for_color code?


def is_this_a_threat_2(x, y, dx, dy, position, color):
  if not (0 <= x + 4 * dx < len(position) and 0 <= y + 4 * dy < len(position)):
    return False
  c_1, c_2, c_3, c_4, c_5 = position[x][y], position[x + dx][y + dy], position[x + 2 * dx][y + 2 * dy], position[x + 3 * dx][y + 3 * dy], position[x + 4 * dx][y + 4 * dy]
  # case of OOO.O, 0.000 or OO.OO
  return ((c_1 == c_2 == c_3 == c_5 == color and c_4 == 0) or
      (c_1 == c_3 == c_4 == c_5 == color and c_2 == 0) or
      (c_1 == c_2 == c_4 == c_5 == color and c_3 == 0))

def is_this_a_threat_1(x, y, dx, dy, position, color):
  # case of .OO.O. or .O.OO.
  if not (0 <= x + 5 * dx < len(position) and 0 <= y + 5 * dy < len(position)):
    return False
  c_1, c_2, c_3, c_4, c_5, c_6 = position[x][y], position[x + dx][y + dy], position[x + 2 * dx][y + 2 * dy], position[x + 3 * dx][y + 3 * dy], position[x + 4 * dx][y + 4 * dy], position[x + 5 * dx][y + 5 * dy]
  return ((c_1 == 0 and c_6 == 0 and c_2 == color and c_5 == color) and
         (c_3 == color and c_4 == 0) or (c_3 == 0 and c_4 == color))

def threat_score(x, y, dx, dy, position, color, my_turn):
  threat = is_this_a_threat(x, y, dx, dy, position, color)
  return threat * (SCORE['XXX.X'] if my_turn else SCORE['OOO.O'])

def score_for_color(position, color, my_turn, stones, past_scores):
  """Looking only at the stones of color `color`, and knowing that it's
  `my_turn` (or not), decide how good is my `position`.

  Parameters
  ----------
  position: numpy.ndarray
    Position of the board
  color: int
    Color of the stones we're looking at
  my_turn: bool
    Is it my turn or not? Something to take into account when evaluating board.
  stones: int list
    List of stones (last moves, stones captured).

  Return
  ------
  tot_score: int
    How much total score do I get based on another function `score`.
  """
  tot = 0
  # winning_groups = 0
  for x in range(len(position)):
    for y in range(len(position)):
      dtot = 0
      if not position[x][y]:
        tot += past_scores[x][y]
        continue
      for (dx, dy) in SLOPES:
        if not were_impacted_slope(stones, x, y, dx, dy):
          if (x,y) == (8, 8):
            print("continue")
          continue
        nb_cons = nb_consecutives(x, y, dx, dy, position, color)
        dtot += threat_score(x, y, dx, dy, position, color, my_turn)
        if nb_cons > 0:
          op_ends = nb_open_ends(x, y, dx, dy, nb_cons, position)
          # can_five = possible_five(position, x, y, dx, dy, nb_cons,
                                  #  color)
          dtot += score(nb_cons, op_ends, my_turn) # * (10 * can_five + 1)
          # winning_groups += winning_stones(nb_cons, op_ends)
          # if (x, y) == (8, 8):
          #   print(f"nb_cons={nb_cons}, score={score(nb_cons, op_ends, my_turn)}")
      tot += dtot
      past_scores[x][y] = dtot
  # return tot + advantage_combinations(winning_groups), past_scores
  print(f"tot ended up being: {tot}")
  return tot, past_scores


def simple_heuristic(position, color, my_turn, stones, past_scores):
  """Evaluation function used for estimating the value of a node in minimax.

  Parameters
  ----------
  position: numpy.ndarray
    The current board position being evaluated.
  color: int
    The color of of the stones for the first score.
  my_turn: bool
    Is it my turn or not? Something to take into account when evaluating board.
  stones: int list
    List of stones (last moves, stones captured).

  Return
  ------
  score: int
    How the situation looks like taking into account the two players.
  """
  first_score, new_past_scores_1 = score_for_color(position, color, my_turn, stones, past_scores[0])
  second_score, new_past_scores_2 = score_for_color(position, opposite(color), not my_turn, stones, past_scores[1])
  print(f"{first_score:2E}-{second_score:2E}={first_score-second_score:2E}")
  return (first_score - second_score), (new_past_scores_1, new_past_scores_2)


def capture_heuristic(player, opponent, our_stones):
  """Takes into account the capture rules, and make capture more likely.

  Parameters
  ----------
  player: Player
    The player that played the last stone.
  opponent: Player
    The player supposed to play now.
  our_stones: bool
    Are we evaluating the situation as if player's stones are our stones?

  Return
  ------
  score: int
    How the situation looks like taking into account the two players's captures.
  """
  if player.captures == 10:
    return np.inf
  sign = 1 if our_stones else -1
  diff = player.captures - opponent.captures
  return sign * diff * SCORE['stone_captured']


def past_heuristic(last_move, current_move):
  """Returns higher score if current move is close to opponent's last move."""
  # heuristic only valid if last move exists
  if last_move == (-1, -1):
    return 0
  return np.linalg.norm(np.array(last_move)-np.array(current_move))


def possible_five(position, x, y, dx, dy, nb_consec, stones_color):
  """Checks if an alignment has enough space to develop into a 5-in-a-row."""
  if nb_consec >= 5:
    return True
  if nb_consec < 2:
    return False
  nb_stones_left = 5 - nb_consec
  for i in range(nb_stones_left + 1):
    # testing if it's possible to have i free intersections, then `nb_consec`
    # stones of color `stones_color` and then 5 - i free interesections
    coord = coordinates(x - i * dx, y - i * dy, dx, dy, 5)
    before = coord[:i]
    after = coord[-(nb_stones_left-i):] if nb_stones_left-i > 0 else []
    if all_equal(before + after, position, 0):
      return True
  return False


def winning_stones(consecutive, open_ends):
  """Check if a series of stones is advantageous."""
  return (consecutive == 3 and open_ends == 2 or
          consecutive == 4 and open_ends >= 1 or
          consecutive >= 5)


def advantage_combinations(winning_groups):
  """High score if multiple threats at once.

  Parameters
  ----------
  winning_groups: int
    Number of group of stones that appear as winning (e.g. free four)
  """
  return (winning_groups >= 2) * SCORE['multiple_threats']


def score(consecutive, open_ends, my_turn):
  """Returns the score corresponding to a sequence of `consecutive` consecutive
  stones with `open_ends` open ends. Will give higher score if the color of
  the stones are the same as the color of the player playing for the current
  turn.

  Parameters
  ----------
  nb_consec: int
    Number of consecutive stones of color
  open_ends: int
    Number of empty intersections (0, 1 or 2) next to the `nb_consec` stones
  my_turn: bool
    Is it my turn or not? Something to take into account when evaluating board.
  """
  if consecutive >= 5:
    return SCORE['XXXXX']
  elif consecutive == 4:
    if open_ends == 1:
      return SCORE['OXXXX.'] if my_turn else SCORE['XOOOO.']
    elif open_ends == 2:
      return SCORE['.XXXX.'] if my_turn else SCORE['.OOOO.']
  elif consecutive == 3:
    if open_ends == 1:
      return SCORE['OXXX.'] if my_turn else SCORE['XOOO.']
    elif open_ends == 2:
      return SCORE['.XXX.'] if my_turn else SCORE['.OOO.']
  elif consecutive == 2:
    if open_ends == 1:
      # having your stones captured is really bad!
      return SCORE['OXX.'] if my_turn else SCORE['XOO.']
    elif open_ends == 2:
      return SCORE['.XX.']
  elif consecutive == 1:
    if open_ends == 1:
      return SCORE['OX.']
    elif open_ends == 2:
      return SCORE['.X.']
  if (open_ends == 0):
    return SCORE['no open ends']
