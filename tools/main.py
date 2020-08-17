#! /home/chenli/Documents/tools/anaconda3/envs/pytorch/bin/python
# coding: utf-8

# pylint: disable=invalid-name
# pylint: disable=unused-import
# pylint: disable=import-error

import time
import random
import logging

import init
import lib.util


def sleep_and_add_one(seconds):
    time.sleep(seconds)
    return seconds + 1


def main():
    start_time = time.time()
    samples = list(range(1, 10))
    random.shuffle(samples)
    results = lib.util.TaskPool.map(4, sleep_and_add_one, samples)
    logging.info("samples: %s", samples)
    logging.info("results: %s", results)
    logging.info("elapsed: %.2fs", time.time() - start_time)
    logging.info("log in color: %s", ", ".join([
        lib.util.BLACK("black"),
        lib.util.RED("Red"),
        lib.util.GREEN("Green"),
        lib.util.YELLOW("yellow"),
        lib.util.BLUE("Blue"),
        lib.util.MAGENTA("magenta"),
        lib.util.CYAN("cyan"),
        lib.util.WHITE("white"),
        lib.util.GRAY("gray"),
    ]))


if __name__ == "__main__":
    lib.util.initialize_logger()
    main()
