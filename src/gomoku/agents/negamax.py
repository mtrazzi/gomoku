import time

import numpy as np

from gomoku.agent import Agent, is_node_terminal
from gomoku.heuristic import heuristic
from gomoku.utils import generate_moves, get_player


class NegaMaxAgent(Agent):
  def __init__(self, color=1, depth=10):
    super().__init__(color)
    self.last_move = (9, 9)
    self.depth = depth
    self.gameHandler = None
    self.opponent = None
    self.nodes = {}

  def find_move(self, gameHandler):
    begin = time.time()
    self.gameHandler = gameHandler
    self.opponent = get_player(gameHandler, self.color, False)

    move = None
    for depth in range(1, self.depth):
      _, move = self.negamaxRoot(depth, -np.Inf, np.Inf)
      if time.time() - begin >= 1:
        break
    return move

  def negamaxRoot(self, depth, α, β):
    newGameMoves = generate_moves(self, depth, True)
    bestMove = -np.Inf
    bestMoveFound = ()

    value = -np.Inf
    for move in newGameMoves:
      self.gameHandler.do_move(move, self)
      value = max(value, -self.negamax(depth - 1, -β, -α, -1))
      self.gameHandler.undo_move()
      if value >= bestMove:
        bestMove = value
        bestMoveFound = move
      α = max(α, value)
      if α >= β:
        break

    return value, bestMoveFound

  def negamax(self, depth, α, β, color):
    if depth == 0 or is_node_terminal(self.gameHandler):
      return color * heuristic(self.gameHandler, self.color, color > 0)
    newGameMoves = generate_moves(self, depth, color > 0)
    value = -np.Inf
    for move in newGameMoves:
      self.gameHandler.do_move(move, self if color > 0 else self.opponent)
      value = max(value, -self.negamax(depth - 1, -β, -α, -color))
      self.gameHandler.undo_move()
      α = max(α, value)
      if α >= β:
        break
    return value
