#!/usr/bin/env python3

import argparse

from core.game_handler import GameHandler
from core.player import Player
from core.board import Board
from core.rules import Rules
from core.script import Script
from core.visualizer import Visualizer
from core.bot import MiniMaxAgent, RandomAgent, AGENTS

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument('-a', "--algorithm",
                      nargs='+', type=str, default="minmax",
                      choices=["random", "minmax"],
                      help="Algorithm for the bot.")
  parser.add_argument('-b', '--board', type=str, default=None,
                      help='Text file which represent a board state.')
  parser.add_argument('-d', "--debug", action='store_true', default=False,
                      help="Enable terminal mode.")
  parser.add_argument('-H', "--heuristic", type=str, default='?',
                      help="Heuristic function.")
  parser.add_argument('-m', "--mode",
                      type=str, default="pvp",
                      choices=["pvp", "hvsbot", "botvsbot"],
                      help="Choose how the program should be executed.")
  parser.add_argument('-s', "--script", type=str, default=None,
                      help="Text file to test sequence of moves.")

  args = parser.parse_args()

  if args.mode in ["pvp", "script"]:
    players = [Player(1), Player(2)]
  elif args.mode == "hvsbot":
    players = [Player(1), AGENTS[args.algorithm[0]](2)]
  elif args.mode == "botvsbot":
    players = [AGENTS[args.algorithm[0]](1), AGENTS[args.algorithm[1]](2)]

  script = Script(args.script) if args.script else None

  game = GameHandler( board=Board(filename=args.board),
                      players=players,
                      rules=Rules(),
                      mode=args.mode,
                      script=script)

  if args.debug:
    game.start()
  else:
    Visualizer(game)
