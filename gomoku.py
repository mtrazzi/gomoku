#!/usr/bin/env python3

import argparse
from core.game_handler import GameHandler
from core.player import Player
from core.board import Board
from core.rules import Rules
from core.script import Script

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument('-H', "--heuristic", type=str, default='?',
                      help="Heuristic function.")
  parser.add_argument('-t', "--type", type=str, default="pvp",
                      choices=["pvp", "bot"],
                      help="Choose how the program should be executed.")
  parser.add_argument('-b', '--board', type=str, default=None,
                      help='Text file which represent a board state')
  parser.add_argument('-s', "--script", type=str, default=None,
                      help="Text file to test sequence of moves")
  args = parser.parse_args()

  players = [Player(1), Player(2)]

  script = Script(args.script) if args.script else None

  game = GameHandler( board=Board(filename=args.board),
                      players=players,
                      rules=Rules(),
                      script=script)
  game.start()
