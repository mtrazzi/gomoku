import tkinter as tk

from PIL import Image, ImageEnhance, ImageTk

from gomoku.visualizer.utils import (BOARD_OFFSET, BOARD_SIZE, COLOR,
                                     STONE_SIZE, WINDOW_WIDTH, coords_to_pixel)


class Canvas(object):
  def __init__(self, root, readyForInput, mouseDownCallback):
    self.root = root
    self.load_tkImages()
    self.load_canvas()

    self.hover_stone = None
    self.color = None

    self.readyForInput = readyForInput
    self.mouseDownCallback = mouseDownCallback
    self.canvas.bind("<ButtonPress-1>", self.OnMouseDown)
    self.canvas.bind("<Motion>", self.OnMouseMove)

  def load_tkImages(self):
    """Load tkImages with Pillow for later use"""
    stop = Image.open("./img/stop.png").resize(STONE_SIZE, Image.ANTIALIAS)
    self.tkStop = ImageTk.PhotoImage(stop)
    board = Image.open("./img/board.png").resize(BOARD_SIZE, Image.ANTIALIAS)
    self.tkBoard = ImageTk.PhotoImage(board)
    black = Image.open("./img/black.png").resize(STONE_SIZE, Image.ANTIALIAS)
    self.tkBlack = ImageTk.PhotoImage(black)
    black.putalpha(ImageEnhance.Brightness(black.split()[3]).enhance(0.5))
    self.tkBlackAlpha = ImageTk.PhotoImage(black)
    white = Image.open("./img/white.png").resize(STONE_SIZE, Image.ANTIALIAS)
    self.tkWhite = ImageTk.PhotoImage(white)
    white.putalpha(ImageEnhance.Brightness(white.split()[3]).enhance(0.5))
    self.tkWhiteAlpha = ImageTk.PhotoImage(white)

  def load_canvas(self):
    """Load tk.Canvas"""
    width = WINDOW_WIDTH
    height = BOARD_SIZE[1]

    self.canvas = tk.Canvas(self.root, width=width, height=height)
    self.canvas.configure(background=COLOR)
    self.canvas.place(relx=0.5, rely=0.499, anchor='center')

  def load_board(self, gameHandler):
    """Reset and display the current state of the board"""
    self.color = gameHandler.current
    self.canvas.delete("all")
    self.canvas.create_image(*BOARD_OFFSET, anchor='nw', image=self.tkBoard)
    board = gameHandler.board
    size = gameHandler.board.size
    for i in range(size):
      for j in range(size):
        stone = board.board[i][j]
        if stone != 0:
          stone = self.tkWhite if stone == 2 else self.tkBlack
          offset = coords_to_pixel([j, i])
          self.canvas.create_image(*offset, anchor="nw", image=stone)

    if len(gameHandler.move_history) > 0:
      last_move = gameHandler.move_history[-1]
      last_move = last_move[::-1]
      offset = coords_to_pixel(last_move) + STONE_SIZE // 2
      radius = STONE_SIZE[0] // 2
      self.canvas.create_circle(*offset, radius, outline="white", width=2)

  def show_illegal_move(self, coords):
    offset = coords_to_pixel(coords)
    self.canvas.create_image(*offset, anchor="nw", image=self.tkStop)

  def reset(self):
    self.hover_stone = None

  def OnMouseMove(self, event):
    """Mouse move callback

    Parameters
    ----------
    event: tk.event
      The registered event (x, y) coordinates of the mouse
    """
    if not self.readyForInput():
      return
    coords = ((event.x, event.y) - BOARD_OFFSET) // (BOARD_SIZE * 0.052)
    if (coords > 18).any() or (coords < 0).any():
      return
    self.canvas.delete(self.hover_stone)
    stone = self.tkWhiteAlpha if self.color == 1 else self.tkBlackAlpha

    config = {'anchor': "nw", 'image': stone}
    offset = coords_to_pixel(coords)
    self.hover_stone = self.canvas.create_image(*offset, **config)

  def OnMouseDown(self, event):
    """Mouse left click callback

    Parameters
    ----------
    event: tk.event
      The registered event (x, y) coordinates of the click
    """
    if not self.readyForInput():
      return
    coords = ((event.x, event.y) - BOARD_OFFSET) // (BOARD_SIZE * 0.052)
    if (coords > 18).any() or (coords < 0).any():
      return

    self.mouseDownCallback([int(x) for x in coords])
