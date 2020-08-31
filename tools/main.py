#! /home/chenli/Documents/tools/anaconda3/envs/pytorch/bin/python
# coding: utf-8

# pylint: disable=unused-import
# pylint: disable=import-error

import logging

import init
import lib.util


def main():
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


if __name__ == '__main__':
    lib.util.initialize_logger()
    main()
