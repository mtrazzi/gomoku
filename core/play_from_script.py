import os

from core.board import Board

class Script(object):
  def __init__(self, filename='capture.txt'):
    self.board = Board()
    self.load_text_file(filename)

  def load_text_file(self, path='scripts/capture.txt'):
    with open(path, 'r') as f:
      raw_lines = [line for line in f]
      clean_lines = []
      for line in raw_lines:
        if line[0] == '#':
          continue
        elif '#' in line:
          clean_lines.append(line[:line.index('#')])
        else:
          clean_lines.append(line)
      lines = [[int(x) for x in l.rstrip('\n').split()] for l in clean_lines]
    self.moves = lines

def run_script(filename):
  script = Script(filename)
  script.board.print_map()
  for move in script.moves:
    x, y = move[0]-1, move[1]-1
    # if move not valid skip it
    if not script.board.respect_rules(x, y):
      print("Invalid move")
      continue
    done = script.board.do_move(x, y)
    if done:
      print(f'Winner is: {3 - script.board.color}')
      break
