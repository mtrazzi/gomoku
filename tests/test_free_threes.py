import os.path as osp

import pytest

from gomoku.board import Board
from gomoku.player import Player
from gomoku.game_handler import GameHandler
from gomoku.rules import Rules


def eval_path(name):
  return osp.join("boards/double_threes", name + ".txt")


def game_handler(board_name):
  return GameHandler(board=Board(filename=eval_path(board_name)),
                     players=[Player(1), Player(2)],
                     rules=Rules())


BLACK = 0
FILES = [str(i) for i in range(10)]
BOARDS = {path: Board(eval_path(path)).board for path in FILES}
NODES = {path: game_handler(path) for path in FILES}
NO_DOUBLE_FREE_THREES = {"1": [(5, 8), True],
                         "2": [(5, 8), True],
                         "3": [(1, 4), True],
                         "4": [(1, 16), True],
                         "5": [(4, 4), True]}


@pytest.mark.parametrize("problem", NO_DOUBLE_FREE_THREES.items())
def test_double_threes(problem):
  board_name, (move, label) = problem
  game_handler = NODES[board_name]
  board, player = game_handler.board, game_handler.players[BLACK]
  game_handler.do_move(*move, player)
  assert Rules().no_double_threes(board, player) == label
