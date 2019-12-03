from core.board import Board
import sys

def pvp():
  board = Board()
  while (1):
      moves = board.get_input()
      x, y = moves[0]-1, moves[1]-1
      board.do_move(x, y)