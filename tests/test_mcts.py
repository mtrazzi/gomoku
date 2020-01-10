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


BLACK = 0
MCTS_EVAL = {
  'four': [(12, 8), (7, 3)],
}
FILES = MCTS_EVAL.keys()
NODES = {path: get_gh_from_script(path) for path in FILES}


@pytest.mark.parametrize("problem", MCTS_EVAL.items())
def test_mcts(problem):
  board_name, best_moves = problem
  game_handler = NODES[board_name]
  black_mcts_agent = MCTSAgent(BLACK, depth=1)
  best_move = black_mcts_agent.find_move(game_handler)
  assert best_move in best_moves
