from core.clean.board import Board
from core.clean.script import Script

def test_print_board():
  board = Board()
  print(board)

def test_script():
  script = Script('./scripts/capture.txt')
