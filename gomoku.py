import argparse
from core.pvp import pvp
from core.play_from_script import run_script
from core.agent import play_agent, botvsbot

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument('-H', "--heuristic", type=str, default='?', help="Heuristic function.")
  parser.add_argument('-m', "--mode", type=str, default="pvp", choices=["pvp", "hvsbot", "script", "botvsbot"], help="Choose how the program should be executed.")
  parser.add_argument('-f', "--filename", type=str, default="capture.txt", help="text file to test sequence of moves")
  parser.add_argument('-a', "--algorithm", nargs='+', type=str, default="minmax", choices=["random", "minmax"], help="algorithm for the bot")
  args = parser.parse_args()

  if args.mode == 'pvp':
    pvp()
  elif args.mode == 'script':
    run_script(args.filename)
  elif args.mode == 'hvsbot':
    play_agent(args.algorithm[0])
  elif args.mode == 'botvsbot':
    if len(args.algorithm) > 1:
      botvsbot(args.algorithm[0], args.algorithm[1])
    else:
      botvsbot(args.algorithm[0], 'minmax')