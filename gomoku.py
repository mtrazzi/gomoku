#!/usr/bin/env python3

import argparse
from core.clean.game_handler import GameHandler
from core.clean.player import Player
from core.clean.board import Board
from core.clean.rules import Rules
from core.clean.script import Script

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument('-H', "--heuristic",
                      type=str, default='?',
                      help="Heuristic function.")
  parser.add_argument('-t', "--type",
                      type=str, default="pvp",
                      choices=["pvp", "bot"],
                      help="Choose how the program should be executed.")
  parser.add_argument('-f', "--filename",
                      type=str, default=None,
                      help="text file to test sequence of moves")
  args = parser.parse_args()

  players = [Player(1), Player(2)]

  script = Script(args.filename) if args.filename else None

  game = GameHandler( board=Board(),
                      players=players,
                      rules=Rules(),
                      script=script)
  game.start()
