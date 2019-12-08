from gomoku.board import Board
from gomoku.script import Script


def test_print_board():
  board = Board()
  print(board)


def test_script():
  Script('./scripts/capture.txt')
