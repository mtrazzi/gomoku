class Player(object):
  """Class Player

  Parameters
  ----------
  stone: int
    Player color

  Attributes
  ----------
  captures: int
    Number of stone captured
  last_move: tuple (x, y)
    Last move
  """
  def __init__(self, stone):
    self.stone = stone
    self.last_move = (-1, -1)
    self.captures = 0
    self.aligned_five_prev = False
    return

  def get_move(self):
    while 1:
      raw = input(f"P{self.stone} next move: $> ")
      move = raw.strip().split()
      if move == ['exit']:
        return ()
      try:
        x, y = [int(i) for i in move]
      except Exception:
        print("\033[1;31mMove badly formatted: \n",
              "must type \"x y\" with x and y integers\n",
              "Example : \"2 3\"\033[0m")
        continue
      return (x - 1, y - 1)
    return ()
