from core.board import Board
import sys

def pvp():
  board = Board()
  counter = 0

  while (1):
      moves = board.get_input()
      x, y = moves[0]-1, moves[1]-1
      board.add_point(counter + 1, x, y)
      counter = (counter + 1) % 2
      board.kill_dead_stones(counter + 1, (x,y))