import numpy as np
import os
import time
import copy

from core.board import Board
from core.heuristics import simple_heuristic

class RandomAgent(object):
  def __init__(self, size=19):
    self.size = size

  def play(self, board):
    """Returns best move given current board position."""
    while True:
      x, y = np.random.randint(self.size), np.random.randint(self.size)
      if board.respect_rules(x, y):
        break
    return x, y

class MinMaxAgent(object):
  def __init__(self, size=5, bot_color=1):
    self.board = Board(size)
    self.size = size
    self.bot_color = bot_color

  def play(self, board, depth=0):
    """Returns best move given current board position."""
    score_map = np.full((self.size, self.size), -np.inf)
    for x in range(self.size):
      for y in range(self.size):
        if board.respect_rules(x, y):
          candidate = copy.deepcopy(board)
          candidate.do_move(x, y)
          score_map[x][y] = self.minimax(candidate, depth, True)
    return np.unravel_index(np.argmax(score_map, axis=None), score_map.shape)

  def eval(self, board, heuristic='simple'):
    """Evaluation function."""
    position = board.map
    if heuristic == 'simple':
      return simple_heuristic(position, self.bot_color)
    return 0
  
  def minimax(self, node, depth, maximizing_player):
    """Cf. https://en.wikipedia.org/wiki/Minimax#Pseudocode."""
    if depth == 0 or node.is_done():
      return self.eval(node)
    if maximizing_player:
      value = -np.inf
      for child in node.child():
        value = max(value, self.minimax(child, depth - 1, False))
        return value
    else:
      value = np.inf
      for child in node.child():
        value = min(value, self.minimax(child, depth - 1, True))
      return value

AGENTS = {
  "minmax": MinMaxAgent,
  "random": RandomAgent
}

def play_agent(agent_type='random'):
  """Script that allows humans to play interactively against the bot."""
  agent = AGENTS[agent_type]()
  board = Board(5)
  counter = 0
  done = False
  while not done:
    x, y = board.get_input() if counter % 2 == 0 else agent.play(board)
    done = board.do_move(x,y)
    counter += 1
  os.system("clear")
  winner = "Bot" if counter % 2 == 0 else "Human"
  print(f'{winner} won!')

def botvsbot(agent_type_1='minmax', agent_type_2='minmax'):
  agent_1 = AGENTS[agent_type_1](bot_color=1)
  agent_2 = AGENTS[agent_type_2](bot_color=2)
  board = Board(5)
  counter = 0
  while True:
    os.system("clear")
    agent = agent_1 if counter % 2 == 0 else agent_2
    x, y = agent.play(board)
    if board.do_move(x,y):
      break
    board.print_map()
    counter += 1
  board.print_map()
  winner = agent_type_1 if counter % 2 == 0 else agent_type_2
  print(f'{winner} won!')