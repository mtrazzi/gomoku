import time

import numpy as np

from gomoku.agent import Agent, Node, is_node_terminal
from gomoku.heuristic import heuristic
from gomoku.utils import generate_moves, get_player


class AlphaBetaMemAgent(Agent):
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
      _, move = self.alphabeta_memoryRoot(depth, -np.Inf, np.Inf)
      if time.time() - begin >= 0.5:
        break
    return move

  def alphabeta_memoryRoot(self, depth, α, β):
    newGameMoves = generate_moves(self, depth, True)
    bestMove = -np.Inf
    bestMoveFound = ()

    nid = str(self.gameHandler.board.board)
    g = -np.Inf
    a = α
    for move in newGameMoves:
      if g >= β:
        break
      self.gameHandler.do_move(move, self)
      g = max(g, self.alphabeta_memory(depth - 1, a, β, False))
      self.gameHandler.undo_move()
      if g >= bestMove:
        bestMove = g
        bestMoveFound = move
      a = max(a, g)

    n = Node(-np.Inf, np.Inf)
    if g <= α:
      n.upperbound = g
    if g > α and g < β:
      n.lowerbound = g
      n.upperbound = g
    if g >= β:
      n.lowerbound = g
    self.nodes[nid] = n
    return g, bestMoveFound

  def alphabeta_memory(self, depth, α, β, maximizing):
    nid = str(self.gameHandler.board.board)
    n = None
    if nid in self.nodes:
      n = self.nodes[nid]
      if n.lowerbound >= β:
        return n.lowerbound
      if n.upperbound <= α:
        return n.upperbound
      α = max(α, n.lowerbound)
      β = min(β, n.upperbound)

    if depth == 0 or is_node_terminal(self.gameHandler):
      g = heuristic(self.gameHandler, self.color, True)
    elif maximizing:
      g = -np.Inf
      a = α
      newGameMoves = generate_moves(self, depth, maximizing)
      for move in newGameMoves:
        if g >= β:
          break
        self.gameHandler.do_move(move, self)
        g = max(g, self.alphabeta_memory(depth - 1, a, β, False))
        self.gameHandler.undo_move()
        a = max(a, g)
    else:
      g = np.Inf
      b = β
      newGameMoves = generate_moves(self, depth, maximizing)
      for move in newGameMoves:
        if g <= α:
          break
        self.gameHandler.do_move(move, self.opponent)
        g = min(g, self.alphabeta_memory(depth - 1, α, b, True))
        self.gameHandler.undo_move()
        b = min(b, g)

    if n is None:
      n = Node(-np.Inf, np.Inf)
    if g <= α:
      n.upperbound = g
    if g > α and g < β:
      n.lowerbound = g
      n.upperbound = g
    if g >= β:
      n.lowerbound = g
    self.nodes[nid] = n
    return g


class MTDFAgent(AlphaBetaMemAgent):
  def __init__(self, color=1, depth=10):
    super().__init__(color, depth)

  def find_move(self, gameHandler):
    begin = time.time()
    self.gameHandler = gameHandler
    self.opponent = get_player(gameHandler, self.color, False)

    value, move = 0, None
    for depth in range(1, self.depth):
      value, move = self.mtdf(depth, value)
      if time.time() - begin >= 1:
        break
    return move

  def mtdf(self, depth, f):
    g = f
    upperBound = np.Inf
    lowerBound = -np.Inf
    while lowerBound < upperBound:
      β = max(g, lowerBound + 1)
      g, move = self.alphabeta_memoryRoot(depth, β - 1, β)
      if g < β:
        upperBound = g
      else:
        lowerBound = g
    return g, move
