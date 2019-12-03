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
  # counter is to alternate between black (id = 1) and white (id = 2) stones
  counter = 0
  script.board.print_map()
  for move in script.moves:
    x, y = move[0]-1, move[1]-1
    # if move not valid skip it
    if not script.board.respect_rules(counter + 1, x, y):
      print("Invalid move")
      continue
    script.board.add_point(counter + 1, x, y)
    counter = (counter + 1) % 2
    # kill stones of opposite colors
    script.board.kill_dead_stones(counter + 1, (x,y))
    script.board.print_map()