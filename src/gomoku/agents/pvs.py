import time

import numpy as np

from gomoku.agent import Agent, is_node_terminal
from gomoku.heuristic import heuristic
from gomoku.moves import generate_moves
from gomoku.utils import get_player


class PVSAgent(Agent):
  def __init__(self, color=1, depth=10):
    super().__init__(color, depth)

  def find_move(self, gameHandler):
    begin = time.time()
    self.gameHandler = gameHandler
    self.opponent = get_player(gameHandler, self.color, False)

    move = None
    for depth in range(1, self.depth):
      _, move = self.pvsRoot(depth, -np.Inf, np.Inf)
      if time.time() - begin >= 0.5:
        break
    return move

  def pvsRoot(self, depth, α, β):
    newGameMoves = generate_moves(self, depth, True)
    bestMove = -np.Inf
    bestMoveFound = ()

    for move in newGameMoves:
      self.gameHandler.do_move(move, self)
      if move == newGameMoves[0]:
        score = -self.pvs(depth - 1, -β, -α, -1)
      else:
        score = -self.pvs(depth - 1, -α - 1, -α, -1)
        if α < score and score < β:
          score = -self.pvs(depth - 1, -β, -score, -1)
      self.gameHandler.undo_move()
      if score >= bestMove:
        bestMove = score
        bestMoveFound = move
      α = max(α, score)
      if α >= β:
        break
    return score, bestMoveFound

  def pvs(self, depth, α, β, color):
    winner = is_node_terminal(self.gameHandler)
    if depth == 0 or winner is not None:
      if winner is None:
        return heuristic(self.gameHandler, self.color, color > 0)
      return np.Inf if winner == self else -np.Inf
    newGameMoves = generate_moves(self, depth, color > 0)
    for move in newGameMoves:
      self.gameHandler.do_move(move, self if color > 0 else self.opponent)
      if move == newGameMoves[0]:
        score = -self.pvs(depth - 1, -β, -α, -color)
      else:
        score = -self.pvs(depth - 1, -α - 1, -α, -color)
        if α < score and score < β:
          score = -self.pvs(depth - 1, -β, -score, -color)
      self.gameHandler.undo_move()
      α = max(α, score)
      if α >= β:
        break
    return α
