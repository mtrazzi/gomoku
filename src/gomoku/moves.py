import numpy as np

from gomoku.heuristic import move_heuristic

MAX_MOVES = 15


def select_past_moves(move_history, depth):
  selected = 5
  if depth >= 8:
    selected = 1
  elif depth >= 6:
    selected = 2
  elif depth >= 4:
    selected = 3
  elif depth >= 2:
    selected = 4
  return move_history[::-1][:selected]


def generate_adjacents(x, y, depth):
  adjacents = np.array([(-1, -1), (-1, 0), (-1, 1), (0,  1),
                        (1,   1), (1,  0), (1, -1), (0, -1)])
  if depth >= 8:
    adjacents = adjacents[2::4]
  elif depth >= 6:
    adjacents = adjacents[::4]
  elif depth >= 4:
    adjacents = adjacents[1::2]
  elif depth >= 2:
    adjacents = adjacents[::2]
  return adjacents + [x, y]


def generate_moves(player, depth, maximizing):
  adjacent = np.array([(-1, -1), (-1, 0), (-1, 1), (0,  1),
                       (1,   1), (1,  0), (1, -1), (0, -1)])
  current = player if maximizing else player.opponent
  gameHandler = player.gameHandler
  board = gameHandler.board

  children = []
  scores = []
  for x in range(board.size):
    for y in range(board.size):
      if board.is_empty(x, y):
        continue
      coords = adjacent + [x, y]
      for v, w in coords:
        if board.is_empty(v, w) and gameHandler.can_place(v, w):
          board.place(v, w, current.color)
          scores.append(move_heuristic(board, v, w, player, player.opponent))
          board.remove(v, w)
          children.append((v, w))

  if len(children) == 0:
    return [(9, 9)]

  idx = np.array(scores).argsort()
  children = np.array(children)[idx[::-1]]
  children = [(x, y) for x, y in children]  # Because of bot.py
  return children[:MAX_MOVES]
