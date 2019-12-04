#!/usr/bin/env python3

import argparse
from core.play_from_script import run_script
from core.agent import play_agent, botvsbot
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
  parser.add_argument('-m', "--mode",
                      type=str, default="pvp",
                      choices=["pvp", "hvsbot", "script", "botvsbot"],
                      help="Choose how the program should be executed.")
  parser.add_argument('-f', "--filename",
                      type=str, default=None,
                      help="text file to test sequence of moves")
  parser.add_argument('-a', "--algorithm",
                      nargs='+', type=str, default="minmax", 
                      choices=["random", "minmax"], 
                      help="algorithm for the bot")
  args = parser.parse_args()

  players = [Player(1), Player(2)]

  script = Script(args.filename) if args.filename else None

  game = GameHandler(board=Board(),
                     players=players,
                     rules=Rules(),
                     mode=args.mode,
                     algorithm=args.algorithm,
                     script=script)
  game.start()
