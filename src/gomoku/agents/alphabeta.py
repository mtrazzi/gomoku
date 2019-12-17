import time

import numpy as np

from gomoku.agent import Agent, is_node_terminal
from gomoku.heuristic import heuristic
from gomoku.utils import generate_moves, get_player


class AlphaBetaAgent(Agent):
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
      _, move = self.alphabetaRoot(depth, -np.Inf, np.Inf)
      if time.time() - begin >= 1:
        break
    return move

  def alphabetaRoot(self, depth, α, β):
    newGameMoves = generate_moves(self, depth, True)
    bestMove = -np.Inf
    bestMoveFound = ()

    value = -np.Inf
    for move in newGameMoves:
      self.gameHandler.do_move(move, self)
      value = max(value, self.alphabeta(depth - 1, α, β, False))
      self.gameHandler.undo_move()
      if value >= bestMove:
        bestMove = value
        bestMoveFound = move
      α = max(α, value)
      if α >= β:
        break

    return value, bestMoveFound

  def alphabeta(self, depth, α, β, maximizing):
    if depth == 0 or is_node_terminal(self.gameHandler):
      return heuristic(self.gameHandler, self.color, maximizing)
    newGameMoves = generate_moves(self, depth, maximizing)
    if maximizing:
      value = -np.Inf
      for move in newGameMoves:
        self.gameHandler.do_move(move, self)
        value = max(value, self.alphabeta(depth - 1, α, β, False))
        self.gameHandler.undo_move()
        α = max(α, value)
        if α >= β:
          break
      return value
    else:
      value = np.Inf
      for move in newGameMoves:
        self.gameHandler.do_move(move, self.opponent)
        value = min(value, self.alphabeta(depth - 1, α, β, True))
        self.gameHandler.undo_move()
        β = min(β, value)
        if α >= β:
          break
      return value
