import tkinter as tk

import numpy as np

WINDOW_WIDTH = 850
WINDOW_SIZE = np.array([WINDOW_WIDTH, WINDOW_WIDTH])
BOARD_SIZE = np.array(WINDOW_SIZE * 0.75, dtype=int)
BOARD_OFFSET = np.array([(WINDOW_WIDTH - BOARD_SIZE[0]) / 2, 0], dtype=int)
STONE_SIZE = np.array(BOARD_SIZE * 0.04, dtype=int)
STONE_OFFSET = np.array(STONE_SIZE // 3, dtype=int)
FONT = ('Helvetica', int(WINDOW_WIDTH*0.0175), 'bold')
COLOR = '#DBB362'


def coords_to_pixel(coords):
  """Convert board coordinates into pixel coordinates"""
  lhs = np.array(coords * BOARD_SIZE * 0.052, dtype=int)
  offset = STONE_OFFSET + BOARD_OFFSET + lhs
  return offset


def _create_circle(self, x, y, r, **kwargs):
  """Monkey patch: Create circle tkinter function"""
  return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)


tk.Canvas.create_circle = _create_circle
