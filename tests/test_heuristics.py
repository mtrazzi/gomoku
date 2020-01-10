import os.path as osp

import numpy as np
import pytest

from gomoku.board import Board
from gomoku.minimax import MiniMaxAgent
from gomoku.game_handler import GameHandler
from gomoku.heuristics import (score, score_for_color, heuristic)
from gomoku.utils import human_move, move


def eval_path(name):
  return osp.join("boards/evals/", name + ".txt")


def game_handler(board_name):
  players = [MiniMaxAgent(1), MiniMaxAgent(2)]
  return GameHandler(board=Board(filename=eval_path(board_name)),
                     players=players)


CONSECUTIVE = range(1, 5)
OPEN_ENDS = range(2)
BLACK, WHITE = 1, 2
FILES = ["one_stone", "two_stones", "bad_two", "ok_two", "good_two",
         "bad_three", "ok_three", "good_three", "four", "five", "empty",
         "please_capture", "can_do_four", "strong_move", "cannot_do_five",
         "break_five", "double_three"]
BOARDS = {path: Board(eval_path(path)).board for path in FILES}
NODES = {path: game_handler(path) for path in FILES}
BEST_MOVES = {"please_capture": [(12, 12)], "can_do_four": [(11, 8), (11, 12)],
              "good_three": [(11, 9), (7, 13)], "break_five": [(11, 12)]}
EXPERT_MOVES = {"strong_move": [(11, 10)]}
FORBIDDEN_MOVES = {"double_three": [(9, 9)]}


def print_debug_eval(arr):
  np.set_printoptions(linewidth=np.inf, precision=4)
  tmp = np.array([i for i in range(1, 20)])
  add_up = np.vstack([tmp, arr])
  left_col = np.array([i for i in range(20)])
  big_arr = np.zeros((20, 20))
  big_arr[:, :1] = left_col.reshape(20, 1)
  big_arr[:, 1:] = add_up
  print(big_arr)


def score_board(board_name, color, my_turn):
  return score_for_color(BOARDS[board_name], color, my_turn)[0]


def score_heuristic(board_name, color, my_turn):
  return heuristic(BOARDS[board_name], color, my_turn)[0]


@pytest.mark.parametrize("consecutive", CONSECUTIVE)
@pytest.mark.parametrize("open_ends", OPEN_ENDS)
def test_score(consecutive, open_ends):
  # test that a position where it's our turn is better
  assert (score(consecutive, open_ends, True) >=
          score(consecutive, open_ends, False))
  if open_ends < 2:
    # test that more open_ends is better (if you cannot be captured)
    for current_turn in [False, True]:
      assert ((score(consecutive, open_ends, current_turn) <=
              score(consecutive, open_ends + 1, current_turn)) or
              consecutive == 2 and open_ends == 0)


def test_score_for_color():
  assert score_board("one_stone", WHITE, True) == 0
  assert score_board("one_stone", WHITE, False) == 0
  assert (score_board("one_stone", BLACK, True) >=
          score_board("one_stone", BLACK, False) > 0)

  assert (score_board("two_stones", WHITE, True) >=
          score_board("two_stones", WHITE, False) > 0)
  assert (score_board("two_stones", BLACK, True) >=
          score_board("two_stones", BLACK, False) > 0)
  assert (score_board("bad_two", WHITE, True) >
          score_board("ok_two", WHITE, True) ==
          score_board("good_two", WHITE, True))
  assert (score_board("bad_two", BLACK, False) <
          score_board("ok_two", BLACK, False) <
          score_board("good_two", BLACK, False))
  assert (score_board("bad_three", WHITE, True) <
          score_board("ok_three", WHITE, True) ==
          score_board("good_three", WHITE, True))
  assert (score_board("bad_three", BLACK, False) <
          score_board("ok_three", BLACK, False) <
          score_board("good_three", BLACK, False))
  assert (score_board("good_three", BLACK, False) <
          score_board("four", BLACK, False) <
          score_board("five", BLACK, False))
  assert (score_board("good_three", WHITE, True) <
          score_board("four", WHITE, True) <
          score_board("five", WHITE, True))


def test_simple_heuristic():
  assert score_heuristic("one_stone", WHITE, True) < 0
  assert score_heuristic("one_stone", WHITE, False) < 0
  assert (score_heuristic("one_stone", BLACK, True) >=
          score_heuristic("one_stone", BLACK, False) > 0)
  assert (score_heuristic("two_stones", WHITE, True) ==
          score_heuristic("two_stones", WHITE, False) ==
          score_heuristic("two_stones", BLACK, True) ==
          score_heuristic("two_stones", BLACK, False) == 0)
  assert (score_heuristic("bad_two", WHITE, True) >
          score_heuristic("ok_two", WHITE, True) >
          score_heuristic("good_two", WHITE, True))
  assert (score_heuristic("bad_two", BLACK, False) <
          score_heuristic("ok_two", BLACK, False) <
          score_heuristic("good_two", BLACK, False))
  assert (score_heuristic("good_three", WHITE, True) <
          score_heuristic("bad_three", WHITE, True) <
          score_heuristic("ok_three", WHITE, True))
  assert (score_heuristic("good_three", BLACK, False) >
          score_heuristic("bad_three", BLACK, False) >
          score_heuristic("ok_three", BLACK, False))
  assert (score_heuristic("good_three", BLACK, False) <
          score_heuristic("four", BLACK, False) <
          score_heuristic("five", BLACK, False))
  assert (score_heuristic("good_three", WHITE, True) >
          score_heuristic("four", WHITE, True) >
          score_heuristic("five", WHITE, True))


def test_minimax_depth_0():
  b_ag = MiniMaxAgent(BLACK)
  w_ag = MiniMaxAgent(WHITE)
  assert (w_ag.minimax(NODES["one_stone"], move(9, 10), 0, True) >
          w_ag.minimax(NODES["one_stone"], move(0, 0), 0, True))
  assert (b_ag.minimax(NODES["empty"], move(9, 9), 0, True) >
          b_ag.minimax(NODES["empty"], move(0, 0), 0, True))
  assert (w_ag.minimax(NODES["ok_two"], move(9, 11), 0, True) >
          w_ag.minimax(NODES["ok_two"], move(10, 9), 0, True))
  assert (w_ag.minimax(NODES["good_three"], move(11, 9), 0, True) >
          w_ag.minimax(NODES["good_three"], move(9, 10), 0, True))


def test_simple_evaluation():
  np.set_printoptions(linewidth=np.inf, precision=4)
  for name, best_moves in BEST_MOVES.items():
    w_ag = MiniMaxAgent(WHITE)
    score_map = w_ag.simple_evaluation(NODES[name])
    if name == "break_five":
        print(NODES[name])
        print_debug_eval(score_map)
    candidate = np.unravel_index(np.argmax(score_map, axis=None),
                                 score_map.shape)
    assert (human_move(candidate) in best_moves)


@pytest.mark.parametrize("depth", [2, 3])
@pytest.mark.parametrize("solution", BEST_MOVES.items())
def test_best_move(depth, solution):
  name, best_moves = solution
  w_ag = MiniMaxAgent(WHITE, depth=depth)
  candidate = w_ag.find_move(NODES[name])
  assert (human_move(candidate) in best_moves)


@pytest.mark.parametrize("problem", FORBIDDEN_MOVES.items())
def test_forbidden_move(problem):
  name, best_moves = problem
  w_ag = MiniMaxAgent(WHITE, depth=0)
  candidate = w_ag.find_move(NODES[name])
  assert (human_move(candidate) not in best_moves)
