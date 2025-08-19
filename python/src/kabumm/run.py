import argparse
import logging

from kabumm.backend import make_backend

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
        backend.write("BUMM")
        backend.set_pixels([(i, 0, 0) for i in range(args.number)])
        for i in range(10):
            print(backend.is_cut())

