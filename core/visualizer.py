import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

WINDOW_WIDTH  = 850
WINDOW_SIZE   = np.array([WINDOW_WIDTH, WINDOW_WIDTH])
BOARD_SIZE    = np.array(WINDOW_SIZE * 0.75, dtype=int)
BOARD_OFFSET  = np.array([(WINDOW_WIDTH - BOARD_SIZE[0]) / 2, 0], dtype=int)
STONE_SIZE    = np.array(BOARD_SIZE * 0.04, dtype=int)
STONE_OFFSET  = np.array(STONE_SIZE // 3, dtype=int)
FONT = ('Helvetica', int(WINDOW_WIDTH*0.0175), 'bold')
COLOR_SCHEME = {'primary': '#DBB362',
                'dark'   : '#B78D39',
                'darker' : '#926919',
                'light'  : '#FFDD9A',
                'lighter': '#FFEBC2' }


class Visualizer(object):

  def __init__(self):
    self.root = tk.Tk()
    self.root.title("Gomoku")
    self.root.geometry(str(WINDOW_WIDTH) + 'x' + str(WINDOW_WIDTH))
    self.root.resizable(False, False)
    self.root.configure(background=COLOR_SCHEME['primary'])

    self.load_tkImages()
    self.load_frames()
    self.load_canvas()
    self.load_buttons()
    self.load_texts()

    self.canvas.bind("<ButtonPress-1>", self.OnMouseDown)
    self.root.mainloop()

  def load_tkImages(self):
    board = Image.open("./img/board.png").resize(BOARD_SIZE, Image.ANTIALIAS)
    self.tkBoard = ImageTk.PhotoImage(board)
    black = Image.open("./img/black.png").resize(STONE_SIZE, Image.ANTIALIAS)
    self.tkBlack = ImageTk.PhotoImage(black)
    white = Image.open("./img/white.png").resize(STONE_SIZE, Image.ANTIALIAS)
    self.tkWhite = ImageTk.PhotoImage(white)

  def load_frames(self):
    width = WINDOW_WIDTH
    height = (WINDOW_WIDTH - BOARD_SIZE[1]) // 2

    self.top_frame = tk.Frame(self.root, width=width, height=height)
    self.top_frame.configure(background=COLOR_SCHEME['dark'])
    self.top_frame.place(relx=0, rely=0, anchor='nw')

    self.canvas_frame = tk.Frame(self.root, width=width, height=BOARD_SIZE[1])
    self.canvas_frame.configure(background=COLOR_SCHEME['primary'])
    self.canvas_frame.place(relx=0.5, rely=0.5, anchor='center')

    self.bottom_frame = tk.Frame(self.root, width=width, height=height)
    self.bottom_frame.configure(background=COLOR_SCHEME['light'])
    self.bottom_frame.place(relx=0, rely=1, anchor='sw')

  def load_canvas(self):
    width = WINDOW_WIDTH
    height = BOARD_SIZE[1]

    self.canvas = tk.Canvas(self.canvas_frame, width=width, height=height)
    self.canvas.configure(background=COLOR_SCHEME['primary'])
    self.canvas.place(relx=0.5, rely=0.499, anchor='center')
    self.canvas.create_image(*BOARD_OFFSET, anchor='nw', image=self.tkBoard)

  def load_buttons(self):
    btn_config = {'width': 10, 'height': 2}

    r_btn = tk.Button(self.top_frame, text="Restart", font=FONT, **btn_config)
    r_btn.place(relx=0.5, rely=0.5, anchor='center')

    h_btn = tk.Button(self.bottom_frame, text="Help!", font=FONT, **btn_config)
    h_btn.place(relx=0.3, rely=0.5, anchor='sw')

    q_btn = tk.Button(self.bottom_frame, text="Quit", font=FONT, **btn_config)
    q_btn.place(relx=0.7, rely=0.5, anchor='se')


  def load_texts(self):
    txt_config = {'width': 25, 'height': 2}
    txt_config['background'] = COLOR_SCHEME['dark']
    p1_score = f"Time: {0}\nP1: {0} stones captured."
    p2_score = f"Time: {0}\nP2: {0} stones captured."

    p1_lbl = tk.Label(self.top_frame, text=p1_score, font=FONT, **txt_config)
    p1_lbl.place(relx=0.1, rely=0.65, anchor='nw')
    p2_lbl = tk.Label(self.top_frame, text=p2_score, font=FONT, **txt_config)
    p2_lbl.place(relx=0.9, rely=0.65, anchor='ne')

  def OnMouseDown(self, event):
    grid_coord = ((event.x, event.y) - BOARD_OFFSET) // (BOARD_SIZE * 0.052)
    if (grid_coord > 18).any() or (grid_coord < 0).any():
      return
    lhs = np.array(grid_coord * BOARD_SIZE * 0.052, dtype=int)
    offset = STONE_OFFSET + BOARD_OFFSET + lhs
    self.canvas.create_image(*offset, anchor="nw", image=self.tkWhite)
