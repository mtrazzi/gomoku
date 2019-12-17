
import tkinter as tk

from PIL import Image, ImageEnhance, ImageTk
import numpy as np

from gomoku.agent import Agent

WINDOW_WIDTH = 850
WINDOW_SIZE = np.array([WINDOW_WIDTH, WINDOW_WIDTH])
BOARD_SIZE = np.array(WINDOW_SIZE * 0.75, dtype=int)
BOARD_OFFSET = np.array([(WINDOW_WIDTH - BOARD_SIZE[0]) / 2, 0], dtype=int)
STONE_SIZE = np.array(BOARD_SIZE * 0.04, dtype=int)
STONE_OFFSET = np.array(STONE_SIZE // 3, dtype=int)
FONT = ('Helvetica', int(WINDOW_WIDTH*0.0175), 'bold')
COLOR = '#DBB362'


def _create_circle(self, x, y, r, **kwargs):
  """Create circle tkinter function for Monkey patch"""
  return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)


tk.Canvas.create_circle = _create_circle


class Visualizer(object):
  """Visualizer class

  Parameters
  ----------
  gameHandler: GameHandler
    The current game

  Attributes
  ----------
  root: tk.Tk
    Main Tk Object
  canvas: tk.Canvas
    The canvas where every image is drawn
  input: bool
    Can we send an input
  illegal_moves: list
    List of illegal move made this turn
  over: bool
    Is the game over
  """
  def __init__(self, gameHandler):
    self.gameHandler = gameHandler
    self.hover_stone = None
    self.input = False
    self.illegal_moves = []
    self.over = False
    self.coords = [-1, -1]

    self.root = tk.Tk()
    self.root.title("Gomoku")
    self.root.geometry(str(WINDOW_WIDTH) + 'x' + str(WINDOW_WIDTH))
    self.root.resizable(False, False)
    self.root.configure(background=COLOR)

    self.load_tkImages()
    self.load_frames()
    self.load_canvas()
    self.load_buttons()
    self.load_texts(f"Turn {self.gameHandler.turn}")

    self.canvas.bind("<ButtonPress-1>", self.OnMouseDown)
    self.canvas.bind("<Motion>", self.OnMouseMove)

    self.load_board()
    self.start()
    self.root.mainloop()

  def load_tkImages(self):
    """Load tkImages with Pillow for later use"""
    stop = Image.open("./img/stop.png").resize(STONE_SIZE, Image.ANTIALIAS)
    self.tkStop = ImageTk.PhotoImage(stop)
    board = Image.open("./img/board.png").resize(BOARD_SIZE, Image.ANTIALIAS)
    self.tkBoard = ImageTk.PhotoImage(board)
    black = Image.open("./img/black.png").resize(STONE_SIZE, Image.ANTIALIAS)
    self.tkBlack = ImageTk.PhotoImage(black)
    black.putalpha(ImageEnhance.Brightness(black.split()[3]).enhance(0.5))
    self.tkBlackOpac = ImageTk.PhotoImage(black)
    white = Image.open("./img/white.png").resize(STONE_SIZE, Image.ANTIALIAS)
    self.tkWhite = ImageTk.PhotoImage(white)
    white.putalpha(ImageEnhance.Brightness(white.split()[3]).enhance(0.5))
    self.tkWhiteOpac = ImageTk.PhotoImage(white)

  def load_frames(self):
    """Load tk.Frames"""
    width = WINDOW_WIDTH
    height = (WINDOW_WIDTH - BOARD_SIZE[1]) // 2

    self.top_frame = tk.Frame(self.root, width=width, height=height)
    self.top_frame.configure(background=COLOR)
    self.top_frame.place(relx=0, rely=0, anchor='nw')

    self.canvas_frame = tk.Frame(self.root, width=width, height=BOARD_SIZE[1])
    self.canvas_frame.configure(background=COLOR)
    self.canvas_frame.place(relx=0.5, rely=0.5, anchor='center')

    self.bottom_frame = tk.Frame(self.root, width=width, height=height)
    self.bottom_frame.configure(background=COLOR)
    self.bottom_frame.place(relx=0, rely=1, anchor='sw')

  def load_canvas(self):
    """Load tk.Canvas"""
    width = WINDOW_WIDTH
    height = BOARD_SIZE[1]

    self.canvas = tk.Canvas(self.canvas_frame, width=width, height=height)
    self.canvas.configure(background=COLOR)
    self.canvas.place(relx=0.5, rely=0.499, anchor='center')

  def load_buttons(self):
    """Load tk.Buttons"""
    btn_config = {'width': 10, 'height': 2, 'font': FONT}

    r_btn = tk.Button(self.top_frame, text="Restart")
    r_btn.configure(command=self.OnRestartPressed, **btn_config)
    r_btn.place(relx=0.5, rely=0.35, anchor='center')

    h_btn = tk.Button(self.bottom_frame, text="Help!")
    h_btn.configure(command=self.OnHelpPressed, **btn_config)
    h_btn.place(relx=0.3, rely=0.5, anchor='sw')

    q_btn = tk.Button(self.bottom_frame, text="Quit")
    q_btn.configure(command=self.OnQuitPressed, **btn_config)
    q_btn.place(relx=0.7, rely=0.5, anchor='se')

  def load_texts(self, global_msg):
    """Load tk.Labels

    Parameters
    ----------
    global_msg: str
      The global message to be displayed
    """
    txt_config = {'width': 25, 'height': 2, 'font': FONT}
    txt_config['background'] = COLOR

    p1_stones = self.gameHandler.players[0].captures
    p2_stones = self.gameHandler.players[1].captures
    p1_score = f"Time: {0}\nP1: {p1_stones} stones captured."
    p2_score = f"Time: {0}\nP2: {p2_stones} stones captured."

    p1_lbl = tk.Label(self.top_frame, text=p1_score, **txt_config)
    p1_lbl.place(relx=0.1, rely=0.65, anchor='nw')
    p2_lbl = tk.Label(self.top_frame, text=p2_score, **txt_config)
    p2_lbl.place(relx=0.9, rely=0.65, anchor='ne')
    global_lbl = tk.Label(self.top_frame, text=global_msg, **txt_config)
    global_lbl.place(relx=0.5, rely=0.85, anchor='center')

  def load_board(self):
    """Reset and display the current state of the board"""
    self.illegal_moves = []
    self.canvas.delete("all")
    self.canvas.create_image(*BOARD_OFFSET, anchor='nw', image=self.tkBoard)
    board = self.gameHandler.board
    size = self.gameHandler.board.size
    for i in range(size):
      for j in range(size):
        stone = board.board[i][j]
        if stone != 0 and stone != 3:
          stone = self.tkWhite if stone == 2 else self.tkBlack
          offset = self.coords_to_pixel([j, i])
          self.canvas.create_image(*offset, anchor="nw", image=stone)

    if len(self.gameHandler.move_history) > 0:
      last_move = self.gameHandler.move_history[-1]
      last_move = last_move[::-1]
      offset = self.coords_to_pixel(last_move) + STONE_SIZE // 2
      radius = STONE_SIZE[0] // 2
      self.canvas.create_circle(*offset, radius, outline="white", width=2)

    global_msg = f"Turn {self.gameHandler.turn}"
    if self.gameHandler.winner is not None:  # FIXME This doesn't belong here
      global_msg = f"P{self.gameHandler.winner.color} won."
      self.over = True
    self.load_texts(global_msg)

  def coords_to_pixel(self, coords):
    """Convert board coordinates into pixel coordinates"""
    lhs = np.array(coords * BOARD_SIZE * 0.052, dtype=int)
    offset = STONE_OFFSET + BOARD_OFFSET + lhs
    return offset

  def start(self):
    """Main Function, run the game"""
    if self.input:
      if self.gameHandler.play(self.coords[::-1]):
        self.load_board()
        self.input = False
        self.coords = [-1, -1]
      elif self.gameHandler.board.is_empty(*self.coords[::-1]):
        if self.coords in self.illegal_moves:
          self.root.after(1, self.start)
          return
        self.illegal_moves.append(self.coords)
        offset = self.coords_to_pixel(self.coords)
        self.canvas.create_image(*offset, anchor="nw", image=self.tkStop)
      self.root.after(1, self.start)
      return

    if self.over:
      self.root.after(1, self.start)
      return

    if self.gameHandler.script and self.gameHandler.script.running():
      move = self.gameHandler.script.get_move()
      self.gameHandler.play(move)
      self.load_board()
      self.root.after(250, self.start)
      return

    if not self.input:
      player = self.gameHandler.players[self.gameHandler.current]
      if isinstance(player, Agent):
        move = player.find_move(self.gameHandler)
        if not self.gameHandler.play(move):
          self.root.after(1, self.start)
          return

      self.load_board()
      player = self.gameHandler.players[self.gameHandler.current]
      if not isinstance(player, Agent):
        self.input = True

    self.root.after(1, self.start)

  def OnMouseMove(self, event):
    """Mouse move callback

    Parameters
    ----------
    event: tk.event
      The registered event (x, y) coordinates of the mouse
    """
    if not self.input or self.over:
      return
    coords = ((event.x, event.y) - BOARD_OFFSET) // (BOARD_SIZE * 0.052)
    if (coords > 18).any() or (coords < 0).any():
      return
    self.canvas.delete(self.hover_stone)
    player = self.gameHandler.current
    stone = self.tkWhiteOpac if player == 1 else self.tkBlackOpac

    config = {'anchor': "nw", 'image': stone}
    offset = self.coords_to_pixel(coords)
    self.hover_stone = self.canvas.create_image(*offset, **config)

  def OnMouseDown(self, event):
    """Mouse left click callback

    Parameters
    ----------
    event: tk.event
      The registered event (x, y) coordinates of the click
    """
    if not self.input or self.over:
      return
    coords = ((event.x, event.y) - BOARD_OFFSET) // (BOARD_SIZE * 0.052)
    if (coords > 18).any() or (coords < 0).any():
      return

    self.coords = [int(x) for x in coords]

  def OnRestartPressed(self):
    """Restart Button callback"""
    self.gameHandler.restart()
    self.hover_stone = None
    self.input = False
    self.illegal_moves = []
    self.over = False
    self.coords = [-1, -1]
    self.load_board()

  def OnQuitPressed(self):
    """Quit Button callback"""
    self.root.destroy()

  def OnHelpPressed(self, iteration=0):
    """Help Button callback"""
    move = self.gameHandler.move_help()
    if self.gameHandler.play(move):
      self.input = False
      self.load_board()
    elif iteration < 500:
      iteration += 1
      self.OnHelpPressed(iteration)
