import argparse
import logging

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--verbose", "-v", action="count", default=0, help="increase verbosity (can be used multiple times)")
    
    args = parser.parse_args()
    logging.basicConfig(level={0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}[args.verbose])
    return args

def main():
    args = parse_args()

