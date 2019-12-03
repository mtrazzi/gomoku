import argparse
from core.pvp import pvp
from core.play_from_script import run_script

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument("--heuristic", type=str, default='?', help="Heuristic function.")
  parser.add_argument("--type", type=str, default="pvp", choices=["pvp", "bot", "script"], help="Choose how the program should be executed.")
  parser.add_argument("--filename", type=str, default="capture.txt", help="text file to test sequence of moves")
  args = parser.parse_args()

  if args.type == 'pvp':
    pvp()
  elif args.type =='script':
    run_script(args.filename)