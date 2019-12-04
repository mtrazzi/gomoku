from core.utils import all_equal, coordinates

SLOPES = [[1, 0], [-1, 1], [0, 1], [1, 1]]

def nb_consecutives(x, y, dx, dy, m, color):
  if m[x][y] != color:
    return 0
  nb_consec = 1
  while True:
    nb_consec += 1
    coord = coordinates(x, y, dx, dy, nb_consec)
    if not all_equal(coord, m, color):
      return nb_consec - 1

def nb_open_ends(x, y, dx, dy, nb_consec, map):
  """Check if all the given coordinates are equal to color in map."""
  m = len(map)
  coord = coordinates(x, y, dx, dy, nb_consec)
  # compute coordinates of open ends candidates before and after given points
  p1 = [coord[0][0] - dx, coord[0][1] - dy]
  p2 = [coord[-1][0] + dx, coord[-1][1] + dy]
  ends = 0
  ends += (0 <= p1[0] < m and 0 <= p1[1] < m) and map[p1[0]][p1[1]] == 0
  ends += (0 <= p2[0] < m and 0 <= p2[1] < m) and map[p2[0]][p2[1]] == 0
  return ends

def score_for_color(position, stones_color, to_move_color):
  """Score according to consecutives and open ends, for given stones' color."""
  tot = 0
  for x in range(len(position)):  
    for y in range(len(position)):
      for (dx, dy) in SLOPES:
        nb_cons = nb_consecutives(x, y, dx, dy, position, stones_color)
        if nb_cons > 0:
          op_ends = nb_open_ends(x, y, dx, dy, nb_cons, position)
          tot += score(nb_cons, op_ends, stones_color == to_move_color)
  return tot

def simple_heuristic(position, to_move_color):
  """Returns score for given position, for player `to_move_color`."""
  return score_for_color(position, to_move_color, to_move_color) - \
         score_for_color(position, to_move_color, 3 - to_move_color)

def score(consecutive, open_ends, current_turn):
  """
  Returns the score corresponding to a sequence of `consecutive` consecutive 
  stones with `open_ends` open ends. Will give higher score if the color of 
  the stones are the same as the color of the player playing for the current
  turn.
  """
  if (open_ends == 0 and consecutive < 5):
    return 0
  if consecutive == 4:
    if open_ends == 1:
      return 100000000 if current_turn else 50
    elif open_ends == 2:
      return 100000000 if current_turn else 500000
  if consecutive == 3:
    if open_ends == 1:
      return 100000000 if current_turn else 50
    elif open_ends == 2:
      return 100000000 if current_turn else 500000
  if consecutive == 2:
    if open_ends == 1:
      return 2
    elif open_ends == 2:
      return 5
  if consecutive == 1:
    if open_ends == 1:
      return 0.5
    elif open_ends == 2:
      return 1
  return 200000000 # if consecutive == 5