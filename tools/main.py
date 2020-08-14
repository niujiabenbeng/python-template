#! /home/chenli/Documents/tools/anaconda3/envs/pytorch/bin/python
# coding: utf-8

# pylint: disable=invalid-name
# pylint: disable=unused-import
# pylint: disable=import-error

import time
import logging

import init
import lib.util


def sleep_and_add_one(seconds):
    time.sleep(seconds)
    return seconds + 1


def main():
    start_time = time.time()
    samples = list(range(1, 10))
    results = lib.util.TaskPool.map(4, sleep_and_add_one, samples)
    logging.info("samples: %s", samples)
    logging.info("results: %s", results)
    logging.info("elapsed: %.2fs", time.time() - start_time)


if __name__ == "__main__":
    lib.util.initialize_logger()
    main()
