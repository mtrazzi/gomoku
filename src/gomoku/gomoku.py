#!/usr/bin/env python3

import argparse

from gomoku.board import Board
from gomoku.bot import MiniMaxAgent, RandomAgent
from gomoku.game_handler import GameHandler
from gomoku.player import Player
from gomoku.rules import Rules
from gomoku.script import Script

AGENTS = {
  "minimax": MiniMaxAgent,
  "random": RandomAgent,
}

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument('-H', "--heuristic", type=str, default='?',
                      help="Heuristic function.")
  parser.add_argument('-m', "--mode",
                      type=str, default="pvp",
                      choices=["pvp", "hvsbot", "botvsbot", "botvsh"],
                      help="Choose how the program should be executed.")
  parser.add_argument('-b', '--board', type=str, default=None,
                      help='Text file which represent a board state')
  parser.add_argument('-s', "--script", type=str, default=None,
                      help="Text file to test sequence of moves")
  parser.add_argument('-a', "--algorithm",
                      nargs='+', type=str, default="minimax",
                      choices=["random", "minimax"],
                      help="algorithm for the bot")

  args = parser.parse_args()

  if args.mode in ["pvp", "script"]:
    players = [Player(1), Player(2)]
  elif args.mode == "hvsbot":
    players = [Player(1), AGENTS[args.algorithm](2)]
  elif args.mode == "botvsbot":
    players = [AGENTS[args.algorithm[0]](1), AGENTS[args.algorithm[1]](2)]
  elif args.mode == "botvsh":
    players = [AGENTS[args.algorithm](1), Player(2)]

  script = Script(args.script) if args.script else None

  game = GameHandler(board=Board(filename=args.board),
                     players=players,
                     rules=Rules(),
                     mode=args.mode,
                     script=script)
  game.start()
