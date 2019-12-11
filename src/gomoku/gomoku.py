#!/usr/bin/env python3

import argparse

from gomoku.board import Board
from gomoku.bot import MiniMaxAgent, RandomAgent
from gomoku.game_handler import GameHandler
from gomoku.player import Player
from gomoku.script import Script
from gomoku.visualizer import Visualizer

AGENTS = {
  "human": Player,
  "minimax": MiniMaxAgent,
  "random": RandomAgent,
}

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument('-b', '--board', type=str, default=None,
                      help='Text file which represent a board state.')
  parser.add_argument('-d', "--debug", action='store_true', default=False,
                      help="Enable terminal mode.")
  parser.add_argument('-H', "--heuristic", type=str, default='?',
                      help="Heuristic function.")
  parser.add_argument('-p1', "--player1",
                      type=str, default="human",
                      choices=["human", "random", "minimax"],
                      help="Choose Player 1 behaviour.")
  parser.add_argument('-p2', "--player2",
                      type=str, default="minimax",
                      choices=["human", "random", "minimax"],
                      help="Choose Player 2 behaviour.")
  parser.add_argument('-s', "--script", type=str, default=None,
                      help="Text file to test sequence of moves.")

  args = parser.parse_args()

  players = []

  players.append(AGENTS[args.player1](1))
  players.append(AGENTS[args.player2](2))

  script = Script(args.script) if args.script else None

  game = GameHandler(board=Board(filename=args.board),
                     players=players,
                     script=script)

  if args.debug:
    game.start()
  else:
    Visualizer(game)
