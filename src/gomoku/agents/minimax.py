import time

import numpy as np

from gomoku.agent import Agent, is_node_terminal
from gomoku.heuristic import heuristic
from gomoku.utils import generate_moves, get_player


class MiniMaxAgent(Agent):
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
      _, move = self.minimaxRoot(depth)
      if time.time() - begin >= 0.5:
        break
    return move

  def minimaxRoot(self, depth):
    newGameMoves = generate_moves(self, depth, True)
    bestMove = -np.Inf
    bestMoveFound = ()

    for move in newGameMoves:
      self.gameHandler.do_move(move, self)
      value = self.minimax(depth - 1, False)
      self.gameHandler.undo_move()
      if value >= bestMove:
        bestMove = value
        bestMoveFound = move
    return value, bestMoveFound

  def minimax(self, depth, maximizing):
    winner = is_node_terminal(self.gameHandler)
    if depth == 0 or winner is not None:
      if winner is None:
        return heuristic(self.gameHandler, self.color, maximizing)
      return np.Inf if winner == self else -np.Inf
    newGameMoves = generate_moves(self, depth, maximizing)
    if maximizing:
      value = -np.Inf
      for move in newGameMoves:
        self.gameHandler.do_move(move, self)
        value = max(value, self.minimax(depth - 1, False))
        self.gameHandler.undo_move()
      return value
    else:
      value = np.Inf
      for move in newGameMoves:
        self.gameHandler.do_move(move, self.opponent)
        value = min(value, self.minimax(depth - 1, True))
        self.gameHandler.undo_move()
      return value
