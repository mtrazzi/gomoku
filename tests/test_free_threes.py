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
                     players=[Player(1), Player(2)])


BLACK = 0
NO_DOUBLE_FREE_THREES = {
  'legal_1': [(5, 8), True],
  'legal_2': [(1, 4), True],
  'legal_3': [(4, 19), True],
  'legal_4': [(6, 9), True],
  'illegal_1': [(5, 8), False],
  'illegal_2': [(4, 4), False],
}
FILES = NO_DOUBLE_FREE_THREES.keys()
BOARDS = {path: Board(eval_path(path)).board for path in FILES}
NODES = {path: game_handler(path) for path in FILES}


@pytest.mark.parametrize("problem", NO_DOUBLE_FREE_THREES.items())
def test_double_threes(problem):
  board_name, (move, label) = problem
  game_handler = NODES[board_name]
  board, player = game_handler.board, game_handler.players[BLACK]
  move = [move[0] - 1, move[1] - 1]
  game_handler.do_move(*move, player)
  assert Rules.no_double_threes(board, player) == label
