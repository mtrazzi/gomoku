from core.board import Board
import sys

def pvp():
  board = Board()
  while (1):
      x,y = board.get_input()
      board.do_move(x, y)