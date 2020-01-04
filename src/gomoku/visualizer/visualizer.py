import time
import tkinter as tk

from gomoku.agent import Agent
from gomoku.bot import MiniMaxAgent
from gomoku.visualizer.canvas import Canvas
from gomoku.visualizer.frames import Frames
from gomoku.visualizer.utils import COLOR, WINDOW_WIDTH


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
    self.playerInput = False
    self.update = False
    self.over = False
    self.move = None
    self.illegal_moves = []
    self.begins = [time.time(), time.time()]
    self.timers = [0, 0]

    self.root = tk.Tk()
    self.root.title("Gomoku")
    self.root.geometry(str(WINDOW_WIDTH) + 'x' + str(WINDOW_WIDTH))
    self.root.resizable(False, False)
    self.root.configure(background=COLOR)

    self.frames = Frames(self.root,
                         restartCallback=self.OnRestartPressed,
                         helpCallback=self.OnHelpPressed,
                         quitCallback=self.OnQuitPressed,
                         undoCallback=self.OnUndoPressed)
    self.canvas = Canvas(self.frames.canvas_frame,
                         readyForInput=self.readyForInput,
                         mouseDownCallback=self.OnMouseDown)

    self.canvas.load_board(self.gameHandler)
    players = self.gameHandler.players
    message = f"Turn {self.gameHandler.turn}"
    self.frames.load_texts(players, self.timers, message)

    self.refresh_labels()
    self.start()
    self.root.mainloop()

  def refresh_labels(self):
    message = f"Turn {self.gameHandler.turn}"
    if self.gameHandler.winner is not None:
      message = f"P{self.gameHandler.winner.color} won."
    self.frames.load_texts(self.gameHandler.players, self.timers, message)
    self.root.after(1000, self.refresh_labels)

  def start(self):
    if not self.update:
      self.canvas.load_board(self.gameHandler)
      self.update = True
      self.root.after(1, self.start)
      return

    if self.over:
      self.root.after(1, self.start)
      return
    current = self.gameHandler.current
    player = self.gameHandler.players[current]
    is_script = self.gameHandler.script and self.gameHandler.script.running()

    if is_script:
      move = self.gameHandler.script.get_move()
    elif isinstance(player, Agent):
      self.playerInput = False
      move = player.find_move(self.gameHandler)
    else:
      # trying to launch some alpha beta in background...
      self.playerInput = True
      # if time.time() - self.timers[1 - current] < 0.5:
      #   opponent = self.gameHandler.players[1 - current]
      #   if isinstance(opponent, MiniMaxAgent):
      #     print("gouligoula")
      #     opponent.find_move(self.gameHandler, 1)
      if self.move is None:
        self.root.after(1, self.start)
        return
      move = self.move[::-1]

    self.timers[current] = round(time.time() - self.begins[current])

    if not self.gameHandler.board.is_empty(*move):
      self.root.after(1, self.start)
      return

    if not self.gameHandler.play(move):
      if move not in self.illegal_moves:
        self.illegal_moves.append(move)
        self.canvas.show_illegal_move(move[::-1])
      self.root.after(1, self.start)
      return

    self.playerInput = not self.playerInput
    self.move = None
    self.illegal_moves = []
    self.update = False
    self.begins = [time.time(), time.time()]
    self.over = self.gameHandler.winner is not None

    self.root.after(250 if is_script else 1, self.start)
    return

  def readyForInput(self):
    return self.playerInput and not self.over

  def OnMouseDown(self, move):
    self.move = move

  def OnRestartPressed(self):
    """Restart Button callback"""
    self.gameHandler.restart()
    self.canvas.reset()

    self.playerInput = False
    self.update = False
    self.over = False
    self.move = None
    self.illegal_moves = []
    self.begins = [time.time(), time.time()]
    self.timers = [0, 0]

    self.canvas.load_board(self.gameHandler)
    players = self.gameHandler.players
    message = f"Turn {self.gameHandler.turn}"
    self.frames.load_texts(players, self.timers, message)

  def OnQuitPressed(self):
    """Quit Button callback"""
    self.root.destroy()

  def OnHelpPressed(self, iteration=0):
    """Help Button callback"""
    if not self.readyForInput():
      return
    self.move = self.gameHandler.move_help()
    self.playerInput = False
  
  def OnUndoPressed(self):
    """Undo Button callback"""
    if not self.readyForInput():
      return
    for _ in range(2):
      self.gameHandler.undo_move()
    for player in self.gameHandler.players:
      if hasattr(player, 'undo_scores'):
        player.table = player.undo_table
    self.playerInput = False
    self.canvas.load_board(self.gameHandler)
