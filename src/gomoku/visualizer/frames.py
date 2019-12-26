import tkinter as tk

from gomoku.visualizer.utils import BOARD_SIZE, COLOR, FONT, WINDOW_WIDTH


class Frames(object):
  def __init__(self, root,
               restartCallback=None,
               helpCallback=None,
               quitCallback=None,
               undoCallback=None):
    self.root = root
    self.restartCallback = restartCallback
    self.helpCallback = helpCallback
    self.quitCallback = quitCallback
    self.undoCallback = undoCallback

    self.load_frames()
    self.load_buttons()

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

  def load_texts(self, players, timers, message):
    """Load tk.Labels

    Parameters
    ----------
    msg: str
      The global message to be displayed
    """
    txt_config = {'width': 25, 'height': 2, 'font': FONT}
    txt_config['background'] = COLOR

    p1_stones = players[0].captures
    p2_stones = players[1].captures
    p1_score = f"Time: {timers[0]}s\nP1: {p1_stones} stones captured."
    p2_score = f"Time: {timers[1]}s\nP2: {p2_stones} stones captured."

    p1_lbl = tk.Label(self.top_frame, text=p1_score, **txt_config)
    p1_lbl.place(relx=0.1, rely=0.65, anchor='nw')
    p2_lbl = tk.Label(self.top_frame, text=p2_score, **txt_config)
    p2_lbl.place(relx=0.9, rely=0.65, anchor='ne')
    global_lbl = tk.Label(self.top_frame, text=message, **txt_config)
    global_lbl.place(relx=0.5, rely=0.85, anchor='center')

  def load_buttons(self):
    """Load tk.Buttons"""
    btn_config = {'width': 8, 'height': 2, 'font': FONT}

    r_btn = tk.Button(self.bottom_frame, text="Restart")
    r_btn.configure(command=self.restartCallback, **btn_config)
    r_btn.place(relx=0.35, rely=0.5, anchor='s')

    u_btn = tk.Button(self.bottom_frame, text="Undo")
    u_btn.configure(command=self.undoCallback, **btn_config)
    u_btn.place(relx=0.45, rely=0.5, anchor='s')

    h_btn = tk.Button(self.bottom_frame, text="Help!")
    h_btn.configure(command=self.helpCallback, **btn_config)
    h_btn.place(relx=0.55, rely=0.5, anchor='s')

    q_btn = tk.Button(self.bottom_frame, text="Quit")
    q_btn.configure(command=self.quitCallback, **btn_config)
    q_btn.place(relx=0.65, rely=0.5, anchor='s')
