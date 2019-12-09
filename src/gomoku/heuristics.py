import numpy as np

from gomoku.utils import all_equal, coordinates, opposite

SLOPES = [[1, 0], [-1, 1], [0, 1], [1, 1]]


def nb_consecutives(x, y, dx, dy, m, color):
  if m[x][y] != color:
    return 0
  # don't start counting if you're not the first stone of a series
  if ((0 <= x - dx < len(m)) and (0 <= y - dy < len(m))
      and m[x - dx][y - dy] == color):
    return 0
  # check what is the biggest nb_coordinates that you can fit in direction dx/dy
  nb_consec = 1
  while True:
    nb_consec += 1
    coord = coordinates(x, y, dx, dy, nb_consec)
    if not all_equal(coord, m, color):
      return nb_consec - 1


def nb_open_ends(x, y, dx, dy, nb_consec, position):
  """Check if the extreme ends are empty or not."""
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
  """Score according to consecutives and open ends, for given stones' color."""
  tot = 0
  for x in range(len(position)):
    for y in range(len(position)):
      if not position[x][y]:
        continue
      for (dx, dy) in SLOPES:
        nb_cons = nb_consecutives(x, y, dx, dy, position, stones_color)
        if nb_cons > 0:
          op_ends = nb_open_ends(x, y, dx, dy, nb_cons, position)
          tot += score(nb_cons, op_ends, my_turn)
  return tot


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


def score(consecutive, open_ends, my_turn):
  """
  Returns the score corresponding to a sequence of `consecutive` consecutive
  stones with `open_ends` open ends. Will give higher score if the color of
  the stones are the same as the color of the player playing for the current
  turn.
  """
  if consecutive >= 5:
    return 1e16
  elif consecutive == 4:
    if open_ends == 1:
      return 1e10 if my_turn else 5e1
    elif open_ends == 2:
      return 1e12
  elif consecutive == 3:
    if open_ends == 1:
      return 1e4 if my_turn else 5e1
    elif open_ends == 2:  # later, deal with spaces outside open ends
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
