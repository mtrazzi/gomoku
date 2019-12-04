import numpy as np
import os
import time

from core.board import Board

class RandomAgent(object):
  def __init__(self, size=19):
    self.board = Board(size)
    self.size = size

  def play(self):
    """Returns best move given current board position."""
    done = False
    while not done:
      x, y = np.random.randint(self.size), np.random.randint(self.size)
      done = self.board.respect_rules(x, y)
    return x, y

class MinMaxAgent(object):
  def __init__(self, size=19):
    self.board = Board(size)
    self.size = size

  def play(self):
    """Returns best move given current board position."""
    done = False
    while not done:
      x, y = np.random.randint(self.size), np.random.randint(self.size)
      done = self.board.respect_rules(x, y)
    return x, y

  def eval(self, position, heuristic='simple'):
    """Evaluation function."""
    return 0
  
  def minimax(self, node, depth, maximizing_player):
    """Cf. https://en.wikipedia.org/wiki/Minimax#Pseudocode."""
    if depth == 0 or node.is_done():
        return self.eval(node)
    if maximizing_player:
        value = -np.inf
        for child in self.board.child():
            value = max(value, self.minimax(child, depth - 1, False))
        return value
    else:
        value = np.inf
        for child in self.board.child():
            value = min(value, self.minimax(child, depth - 1, True))
        return value

AGENTS = {
  "minmax": MinMaxAgent,
  "random": RandomAgent
}

def play_agent(agent_type='random'):
  """Script that allows humans to play interactively against the bot."""
  agent = AGENTS[agent_type]()
  counter = 0
  done = False
  while not done:
    x, y = agent.board.get_input() if counter % 2 == 0 else agent.play()
    done = agent.board.do_move(x,y)
    counter += 1
  os.system("clear")
  winner = "Bot" if counter % 2 == 0 else "Human"
  print(f'{winner} won!')

def botvsbot(agent_type='random'):
  agent = AGENTS[agent_type]()
  dummy_agent = AGENTS["random"]()
  counter = 0
  done = False
  while not done:
    os.system("clear")
    agent.board.print_map()
    time.sleep(0.5)
    x, y = agent.play() if counter % 2 == 0 else dummy_agent.play()
    done = agent.board.do_move(x,y)
    dummy_agent.board.do_move(x,y)
    counter += 1
  winner = agent_type if counter % 2 == 0 else "dummy_agent"
  print(f'{winner} won!')