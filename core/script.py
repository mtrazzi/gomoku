import re

class Script(object):

  def __init__(self, filename):
    self.filename = filename
    self.move = []
    self.load_script(filename)

  def load_script(self, filename):
    with open(filename, 'r') as f:
      lines = [re.sub('#.*', '', line.strip()) for line in f]
      lines = [line for line in lines if line]
      try:
        self.move = [[int(x) - 1 for x in line.split()] for line in lines]
      except:
        raise Exception("File not well formatted.")

  def input(self):
    move = self.move.pop(0)
    return move

  def running(self):
    return len(self.move) != 0

  def restart(self):
    self.load_script(self.filename)
