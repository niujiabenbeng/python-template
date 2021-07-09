#! /usr/bin/env python
# coding: utf-8

# pylint: disable=unused-import
# pylint: disable=wrong-import-order

import logging

import init
import lib.util


def main():
    logging.info("log in color: %s", lib.util.ColorWrapper.black("black"))
    logging.info("log in color: %s", lib.util.ColorWrapper.red("Red"))
    logging.info("log in color: %s", lib.util.ColorWrapper.green("Green"))
    logging.info("log in color: %s", lib.util.ColorWrapper.yellow("yellow"))
    logging.info("log in color: %s", lib.util.ColorWrapper.blue("Blue"))
    logging.info("log in color: %s", lib.util.ColorWrapper.magenta("magenta"))
    logging.info("log in color: %s", lib.util.ColorWrapper.cyan("cyan"))
    logging.info("log in color: %s", lib.util.ColorWrapper.white("white"))
    logging.info("log in color: %s", lib.util.ColorWrapper.gray("gray"))


if __name__ == '__main__':
    lib.util.initialize_logger()
    main()
