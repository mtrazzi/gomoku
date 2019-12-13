import numpy as np

from gomoku.utils import SLOPES, all_equal, coordinates, opposite


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
  if position[x][y] != color:
    return 0
  # don't start counting if you're not the first stone of a series
  if ((0 <= x - dx < len(position)) and (0 <= y - dy < len(position))
      and position[x - dx][y - dy] == color):
    return 0
  # check what is the biggest nb_coordinates that you can fit in direction dx/dy
  nb_consec = 1
  while True:
    nb_consec += 1
    coord = coordinates(x, y, dx, dy, nb_consec)
    if not all_equal(coord, position, color):
      return nb_consec - 1


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


def score_for_color(position, stones_color, my_turn):
  """Looking only at the stones of color `stones_color`, and knowing that it's
  `my_turn` (or not), decide how good is my `position`.

  Parameters
  ----------
  position: numpy.ndarray
    Position of the board
  stones_color: int
    Color of the stones we're looking at
  my_turn: bool
    Is it my turn or not? Something to take into account when evaluating board.

  Return
  ------
  tot_score: int
    How much total score do I get based on another function `score`.
  """
  tot = 0
  winning_groups = 0
  for x in range(len(position)):
    for y in range(len(position)):
      if not position[x][y]:
        continue
      for (dx, dy) in SLOPES:
        nb_cons = nb_consecutives(x, y, dx, dy, position, stones_color)
        if nb_cons > 0:
          op_ends = nb_open_ends(x, y, dx, dy, nb_cons, position)
          can_five = possible_five(position, x, y, dx, dy, nb_cons,
                                   stones_color)
          tot += score(nb_cons, op_ends, my_turn) * (10 * can_five + 1)
          winning_groups += winning_stones(nb_cons, op_ends)
  return tot + advantage_combinations(winning_groups)


def simple_heuristic(position, color, my_turn):
  """Evaluation function used for estimating the value of a node in minimax.

  Parameters
  ----------
  position: numpy.ndarray
    The current board position being evaluated.
  color: int
    The color of of the stones for the first score.
  my_turn: bool
    Is it my turn or not? Something to take into account when evaluating board.

  Return
  ------
  score: int
    How the situation looks like taking into account the two players.
  """
  first_score = score_for_color(position, color, my_turn)
  second_score = score_for_color(position, opposite(color), not my_turn)
  return (first_score - second_score)


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
  return sign * diff * 1e8


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
  return (winning_groups >= 2) * 1e8


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
    return 1e16
  elif consecutive == 4:
    if open_ends == 1:
      return 1e10 if my_turn else 5e1
    elif open_ends == 2:
      return 1e12 if my_turn else 1e11
  elif consecutive == 3:
    if open_ends == 1:
      return 1e2 if my_turn else 5e1
    elif open_ends == 2:  # FIXME: later, deal with spaces outside open ends
      return 1e5 if my_turn else 5e4
  elif consecutive == 2:
    if open_ends == 1:
      # having your stones captured is really bad!
      return -1e4 if my_turn else -1e8
    elif open_ends == 2:
      return 5
  elif consecutive == 1:
    if open_ends == 1:
      return 0.5
    elif open_ends == 2:
      return 1
  if (open_ends == 0):
    return 0
