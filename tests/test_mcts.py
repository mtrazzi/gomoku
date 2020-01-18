import os.path as osp

import pytest

from gomoku.board import Board
from gomoku.game_handler import GameHandler
from gomoku.player import Player
from gomoku.rules import Rules
from gomoku.mcts import MCTSAgent
from gomoku.script import Script


def get_gh_from_script(filename):
  gh = GameHandler(Board(), [Player(1), Player(2)])
  base_dir, suffix = 'scripts', '.txt'
  path = osp.join(base_dir, filename + suffix)
  script = Script(path)
  while script.running():
    gh.do_move(script.get_move())
  return gh


BLACK = 1
MCTS_BASIC = {
  'four': [(7, 13), (12, 8)],
}
MCTS_OPPONENT = {
  'four_opponent': [(7, 13)],
}

FILES = list(MCTS_BASIC.keys()) + list(MCTS_OPPONENT.keys())
NODES = {path: get_gh_from_script(path) for path in FILES}


@pytest.mark.parametrize("problem", MCTS_BASIC.items())
def test_basic(problem):
  board_name, best_moves = problem
  game_handler = NODES[board_name]
  print(game_handler)
  black_mcts_agent = MCTSAgent(BLACK, depth=1)
  best_move = black_mcts_agent.find_move(game_handler)
  assert best_move in best_moves

@pytest.mark.parametrize('execution_number', range(10))
@pytest.mark.parametrize("problem", MCTS_OPPONENT.items())
def test_opponent(problem, execution_number):
  board_name, best_moves = problem
  game_handler = NODES[board_name]
  print(game_handler)
  black_mcts_agent = MCTSAgent(BLACK, depth=16)
  best_move = black_mcts_agent.find_move(game_handler)
  assert best_move in best_moves
