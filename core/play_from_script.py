import os

from core.board import Board

class Script(object):
  def __init__(self, filename='capture.txt'):
    self.board = Board()
    self.load_text_file(filename)

  def load_text_file(self, filename='capture.txt', dir_name='scripts'):
    path = os.path.join(dir_name, filename)
    with open(path, 'r') as f:
      raw_lines = [line for line in f]
      for idx,line in enumerate(raw_lines):
        if line[0] == '#':
          raw_lines.remove(line)
        elif '#' in line:
          raw_lines[idx] = line[:line.index('#')]
      lines = [[int(x) for x in l.rstrip('\n').split()] for l in raw_lines]
    self.moves = lines

def run_script(filename):
  script = Script(filename)
  counter = 0
  script.board.print_map()
  for move in script.moves:
      x, y = move[0]-1, move[1]-1
      script.board.add_point(counter + 1, x, y)
      counter = (counter + 1) % 2
      script.board.kill_dead_stones(counter + 1, (x,y))
      script.board.print_map()