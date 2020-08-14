#! /home/chenli/Documents/tools/anaconda3/envs/pytorch/bin/python
# coding: utf-8

import os
import pickle
import logging
import threading


### 全局锁
# pylint: disable=invalid-name
global_lock = threading.Lock()


def prepare_dir(path):
    """Make dir if necessary."""

    dirname = os.path.dirname(path)
    ### 当前目录直接返回
    if not dirname: return None

    global_lock.acquire()
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    global_lock.release()
    return None


def dump_to_file(data, path):
    """dump data to file."""

    prepare_dir(path)
    with open(path, "wb") as dstfile:
        pickle.dump(data, dstfile, protocol=2)


def initialize_logger(name=None, file=None, display=True):
    """Configurate logger based on settings.

    Args:
        name: str. Logger name, 'None' means root logger.
        file: str. Path of file to log to, 'None' or empty string to disable
            logging to file.
        display: bool. Indicate whether the logger logs to console or not.

    Returns:
        The required logger instance.
    """

    logger = logging.getLogger(name)
    if logger.handlers: return logger

    ### 局部的logger是全局logger的child, 这里防止局部的log扩散到全局log中
    logger.propagate = False
    logger.setLevel(logging.INFO)

    fmt = "%(asctime)s %(filename)s:%(lineno)d] %(levelname)s: %(message)s"
    fmt = logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")

    if file:
        prepare_dir(file)
        handler = logging.FileHandler(file)
        handler.setFormatter(fmt)
        logger.addHandler(handler)

    if display:
        console = logging.StreamHandler()
        console.setFormatter(fmt)
        logger.addHandler(console)

    return logger


if __name__ == "__main__":
    pass
