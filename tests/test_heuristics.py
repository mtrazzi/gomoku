import numpy as np
import pytest

from gomoku.heuristics import score, score_for_color, simple_heuristic
from gomoku.board import Board

CONSECUTIVE = range(1, 5)
OPEN_ENDS = range(2)

@pytest.mark.parametrize("consecutive", CONSECUTIVE)
@pytest.mark.parametrize("open_ends", OPEN_ENDS)
def test_score(consecutive, open_ends):
  # test that a position where it's our turn is better
  assert (score(consecutive, open_ends, True) >=
          score(consecutive, open_ends, False))
  if open_ends < 2:
    # test that more open_ends is better
    for current_turn in [False, True]:
      assert (score(consecutive, open_ends, current_turn) <=
              score(consecutive, open_ends + 1, current_turn))

def test_simple_heuristic():
  board = Board("boards/1.txt")
