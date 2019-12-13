import time

import numpy as np

from gomoku.bot import Agent
from gomoku.rules import Rules
from gomoku.utils import generate_moves


class Node(object):
  def __init__(self, lowerbound, upperbound):
    self.lowerbound = lowerbound
    self.upperbound = upperbound


def is_node_terminal(gameHandler):
  end = Rules.check_winner(gameHandler.board, gameHandler.players) is not None
  return end


def heuristic(gameHandler, color):
  return 0

class MiniMaxTiny(Agent):
  def __init__(self, color=1, depth=10, algorithm='minimax'):
    super().__init__(color)
    self.last_move = (9, 9)
    self.depth = depth
    self.gameHandler = None
    self.nodes = {}

  def find_move(self, gameHandler):
    begin = time.time()
    self.gameHandler = gameHandler

    value, move = self.minimaxRoot(self.depth)
    # value, move = self.negamaxRoot(self.depth, -np.Inf, np.Inf)
    # value, move = self.alphabetaRoot(self.depth, -np.Inf, np.Inf)
    # value, move = self.pvsRoot(self.depth, -np.Inf, np.Inf)
    # value, move = self.alphabeta_memoryRoot(self.depth, -np.Inf, np.Inf)
    # value, move = self.mtdf(self.depth, 0)
    print(f"Value for move {move}: {value}")
    print(f'Time elapse for find_move(): {time.time() - begin}')
    return move

  def minimaxRoot(self, depth):
    newGameMoves = generate_moves(self.gameHandler, self.color, True)
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
    if depth == 0 or is_node_terminal(self.gameHandler):
      return heuristic(self.gameHandler, self.color)
    newGameMoves = generate_moves(self.gameHandler, self.color, maximizing)
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
        self.gameHandler.do_move(move, self)
        value = min(value, self.minimax(depth - 1, True))
        self.gameHandler.undo_move()
      return value

  def negamaxRoot(self, depth, α, β):
    newGameMoves = generate_moves(self.gameHandler, self.color, True)
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
      return color * heuristic(self.gameHandler, self.color)
    newGameMoves = generate_moves(self.gameHandler, self.color, color > 0)
    value = -np.Inf
    for move in newGameMoves:
      self.gameHandler.do_move(move, self)
      value = max(value, -self.negamax(depth - 1, -β, -α, -color))
      self.gameHandler.undo_move()
      α = max(α, value)
      if α >= β:
        break
    return value

  def pvsRoot(self, depth, α, β):
    newGameMoves = generate_moves(self.gameHandler, self.color, True)
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
    if depth == 0 or is_node_terminal(self.gameHandler):
      return color * heuristic(self.gameHandler, self.color)
    newGameMoves = generate_moves(self.gameHandler, self.color, color > 0)
    for move in newGameMoves:
      self.gameHandler.do_move(move, self)
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

  def alphabetaRoot(self, depth, α, β):
    newGameMoves = generate_moves(self.gameHandler, self.color, True)
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
      return heuristic(self.gameHandler, self.color)
    newGameMoves = generate_moves(self.gameHandler, self.color, maximizing)
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
        self.gameHandler.do_move(move, self)
        value = min(value, self.alphabeta(depth - 1, α, β, True))
        self.gameHandler.undo_move()
        β = min(β, value)
        if α >= β:
          break
      return value

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

  def alphabeta_memoryRoot(self, depth, α, β):
    newGameMoves = generate_moves(self.gameHandler, self.color, True)
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
      g = heuristic(self.gameHandler, self.color)
    elif maximizing:
      g = -np.Inf
      a = α
      newGameMoves = generate_moves(self.gameHandler, self.color, maximizing)
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
      newGameMoves = generate_moves(self.gameHandler, self.color, maximizing)
      for move in newGameMoves:
        if g <= α:
          break
        self.gameHandler.do_move(move, self)
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


# PSEUDO_CODE
# function iterative_deepening(root : node_type) : integer;
#   firstguess := 0;
#   for d = 1 to MAX_SEARCH_DEPTH do
#     firstguess := MTDF(root, firstguess, d);
#     if times_up() then break;
#   return firstguess;
