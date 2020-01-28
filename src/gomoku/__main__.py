#!/usr/bin/env python3

import argparse

import numpy as np

from gomoku.board import Board
from gomoku.game_handler import GameHandler
from gomoku.minimax import minimax_agent_wrapper
from gomoku.player import Player
from gomoku.script import Script
from gomoku.visualizer import Visualizer

AGENTS = {
  "human": Player,
  "minimax": minimax_agent_wrapper("minimax"),
  "alpha_beta": minimax_agent_wrapper("alpha_beta"),
  "alpha_beta_memory": minimax_agent_wrapper("alpha_beta_memory"),
  "alpha_beta_basic": minimax_agent_wrapper("alpha_beta_basic"),
  "mtdf": minimax_agent_wrapper("mtdf"),
}
CHOICES = AGENTS.keys()

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument('-b', '--board', type=str, default=None,
                      help='Text file which represent a board state.')
  parser.add_argument('-d', "--debug", action='store_true', default=False,
                      help="Enable terminal mode.")
  parser.add_argument('-H', "--heuristic", type=str, default='?',
                      help="Heuristic function.")
  parser.add_argument('-D', '--depth', type=int, default=10, help="Depth of the\
                        search tree for Minimax Agents", choices=range(1, 11))
  parser.add_argument('-p1', "--player1",
                      type=str, default="human",
                      choices=CHOICES,
                      help="Choose Player 1 behaviour.")
  parser.add_argument('-p2', "--player2",
                      type=str, default="alpha_beta_basic",
                      choices=CHOICES,
                      help="Choose Player 2 behaviour.")
  parser.add_argument('-s', "--script", type=str, default=None,
                      help="Text file to test sequence of moves.")
  parser.add_argument('-c', "--competition", type=float, default=np.Inf,
                      help="Enable competition mode (max time to play).")

  args = parser.parse_args()

  players = []

  players.append(AGENTS[args.player1](1))
  players.append(AGENTS[args.player2](2))

  for player in players:
    if hasattr(player, 'depth'):
      player.depth = args.depth

  script = Script(args.script) if args.script else None

  game = GameHandler(board=Board(filename=args.board),
                     players=players,
                     script=script,
                     time_limit=args.competition)

  if args.debug:
    game.start()
  else:
    Visualizer(game)
