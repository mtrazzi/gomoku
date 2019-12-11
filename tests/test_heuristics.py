import os.path as osp

import numpy as np
import pytest

from gomoku.board import Board
from gomoku.bot import MiniMaxAgent
from gomoku.game_handler import GameHandler
from gomoku.heuristics import score, score_for_color, simple_heuristic
from gomoku.rules import Rules
from gomoku.utils import human_move, move


def eval_path(name):
  return osp.join("boards/evals/", name + ".txt")


def game_handler(board_name):
  players = [MiniMaxAgent(1), MiniMaxAgent(2)]
  return GameHandler(board=Board(filename=eval_path(board_name)),
                     players=players,
                     rules=Rules())


CONSECUTIVE = range(1, 5)
OPEN_ENDS = range(2)
BLACK, WHITE = 1, 2
FILES = ["one_stone", "two_stones", "bad_two", "ok_two", "good_two",
         "bad_three", "ok_three", "good_three", "four", "five", "empty",
         "please_capture", "can_do_four", "strong_move"]
BOARDS = {path: Board(eval_path(path)).board for path in FILES}
NODES = {path: game_handler(path) for path in FILES}
BEST_MOVES = {"please_capture": [(12, 12)], "can_do_four": [(11, 8), (11, 12)],
              "good_three": [(11, 9), (7, 13)]}
EXPERT_MOVES = {"strong_move": [(11, 10)]}


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
  assert score_for_color(BOARDS["one_stone"], WHITE, True) == 0
  assert score_for_color(BOARDS["one_stone"], WHITE, False) == 0
  assert (score_for_color(BOARDS["one_stone"], BLACK, True) >=
          score_for_color(BOARDS["one_stone"], BLACK, False) > 0)

  assert (score_for_color(BOARDS["two_stones"], WHITE, True) >=
          score_for_color(BOARDS["two_stones"], WHITE, False) > 0)
  assert (score_for_color(BOARDS["two_stones"], BLACK, True) >=
          score_for_color(BOARDS["two_stones"], BLACK, False) > 0)
  assert (score_for_color(BOARDS["bad_two"], WHITE, True) >
          score_for_color(BOARDS["ok_two"], WHITE, True) ==
          score_for_color(BOARDS["good_two"], WHITE, True))
  assert (score_for_color(BOARDS["bad_two"], BLACK, False) <
          score_for_color(BOARDS["ok_two"], BLACK, False) <
          score_for_color(BOARDS["good_two"], BLACK, False))
  assert (score_for_color(BOARDS["bad_three"], WHITE, True) <
          score_for_color(BOARDS["ok_three"], WHITE, True) ==
          score_for_color(BOARDS["good_three"], WHITE, True))
  assert (score_for_color(BOARDS["bad_three"], BLACK, False) <
          score_for_color(BOARDS["ok_three"], BLACK, False) <
          score_for_color(BOARDS["good_three"], BLACK, False))
  assert (score_for_color(BOARDS["good_three"], BLACK, False) <
          score_for_color(BOARDS["four"], BLACK, False) <
          score_for_color(BOARDS["five"], BLACK, False))
  assert (score_for_color(BOARDS["good_three"], WHITE, True) <
          score_for_color(BOARDS["four"], WHITE, True) <
          score_for_color(BOARDS["five"], WHITE, True))


def test_simple_heuristic():
  assert simple_heuristic(BOARDS["one_stone"], WHITE, True) < 0
  assert simple_heuristic(BOARDS["one_stone"], WHITE, False) < 0
  assert (simple_heuristic(BOARDS["one_stone"], BLACK, True) >=
          simple_heuristic(BOARDS["one_stone"], BLACK, False) > 0)
  assert (simple_heuristic(BOARDS["two_stones"], WHITE, True) ==
          simple_heuristic(BOARDS["two_stones"], WHITE, False) ==
          simple_heuristic(BOARDS["two_stones"], BLACK, True) ==
          simple_heuristic(BOARDS["two_stones"], BLACK, False) == 0)
  assert (simple_heuristic(BOARDS["bad_two"], WHITE, True) >
          simple_heuristic(BOARDS["ok_two"], WHITE, True) >
          simple_heuristic(BOARDS["good_two"], WHITE, True))
  assert (simple_heuristic(BOARDS["bad_two"], BLACK, False) <
          simple_heuristic(BOARDS["ok_two"], BLACK, False) <
          simple_heuristic(BOARDS["good_two"], BLACK, False))
  assert (simple_heuristic(BOARDS["good_three"], WHITE, True) <
          simple_heuristic(BOARDS["bad_three"], WHITE, True) <
          simple_heuristic(BOARDS["ok_three"], WHITE, True))
  assert (simple_heuristic(BOARDS["good_three"], BLACK, False) >
          simple_heuristic(BOARDS["bad_three"], BLACK, False) >
          simple_heuristic(BOARDS["ok_three"], BLACK, False))
  assert (simple_heuristic(BOARDS["good_three"], BLACK, False) <
          simple_heuristic(BOARDS["four"], BLACK, False) <
          simple_heuristic(BOARDS["five"], BLACK, False))
  assert (simple_heuristic(BOARDS["good_three"], WHITE, True) >
          simple_heuristic(BOARDS["four"], WHITE, True) >
          simple_heuristic(BOARDS["five"], WHITE, True))


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
    candidate = np.unravel_index(np.argmax(score_map, axis=None),
                                 score_map.shape)
    # print(NODES[name])
    # print(f"for above board, candidate was: {human_move(candidate)}")
    # print(*score_map, sep='\n')
    assert (human_move(candidate) in best_moves)


@pytest.mark.parametrize("depth", [2, 3])
@pytest.mark.parametrize("solution", BEST_MOVES.items())
def test_depth(depth, solution):
  name, best_moves = solution
  w_ag = MiniMaxAgent(WHITE, depth=depth)
  candidate = w_ag.find_move(NODES[name])
  # print(NODES[name])
  # print(f"for above board, candidate was: {human_move(candidate)}")
  assert (human_move(candidate) in best_moves)


# @pytest.mark.parametrize("depth", [3])
# @pytest.mark.parametrize("solution", EXPERT_MOVES.items())
# def test_expert_moves(depth, solution):
#   name, best_moves = solution
#   w_ag = MiniMaxAgent(WHITE, depth=depth)
#   candidate = w_ag.find_move(NODES[name])
#   # print(NODES[name])
#   # print(f"for above board, candidate was: {human_move(candidate)}")
#   assert (human_move(candidate) in best_moves)

@pytest.mark.parametrize("depth", [2, 3])
@pytest.mark.parametrize("solution", BEST_MOVES.items())
def test_alpha_beta_memory(depth, solution):
  name, best_moves = solution
  w_ag = MiniMaxAgent(WHITE, depth=depth)
  candidate = w_ag.find_move(NODES[name])
  # print(NODES[name])
  # print(f"for above board, candidate was: {human_move(candidate)}")
  assert (human_move(candidate) in best_moves)
