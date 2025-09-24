import argparse
import logging
import time


from kabumm.backend import make_backend
from kabumm.game import Game

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--number", "-n", type=int, default=16, help="number of leds/wires")
    parser.add_argument("--verbose", "-v", action="count", default=0, help="increase verbosity (can be used multiple times)")
    
    args = parser.parse_args()
    logging.basicConfig(level={0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}[args.verbose])
    return args

def main():
    args = parse_args()
    with make_backend(num_wires_and_pixels=args.number) as backend:
        backend.set_pixels([(i, 0, 0) for i in range(args.number)])
        game = Game(backend)
        while not game.finished:
            game.tick()
            time.sleep(0.1)

