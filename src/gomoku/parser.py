#!/usr/bin/env python3

import argparse

from gomoku.agents import NegaMaxAgent, PVSAgent
from gomoku.board import Board
from gomoku.bot import minimax_agent_wrapper
from gomoku.game_handler import GameHandler
from gomoku.player import Player
from gomoku.script import Script
from gomoku.visualizer import Visualizer

AGENTS = {
  "human": Player,
  "minimax": minimax_agent_wrapper("minimax"),
  "negamax": NegaMaxAgent,
  "pvs": PVSAgent,
  "alpha_beta": minimax_agent_wrapper("alpha_beta"),
  "alpha_beta_memory": minimax_agent_wrapper("alpha_beta_memory"),
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
  parser.add_argument('-D', '--depth', type=int, default=2, help="Depth of the search tree for Minimax Agents")
  parser.add_argument('-p1', "--player1",
                      type=str, default="human",
                      choices=CHOICES,
                      help="Choose Player 1 behaviour.")
  parser.add_argument('-p2', "--player2",
                      type=str, default="minimax",
                      choices=CHOICES,
                      help="Choose Player 2 behaviour.")
  parser.add_argument('-s', "--script", type=str, default=None,
                      help="Text file to test sequence of moves.")

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
                     script=script)

  if args.debug:
    game.start()
  else:
    Visualizer(game)
