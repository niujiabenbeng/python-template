#! /usr/bin/env python
# coding: utf-8

import os
import json
import pickle
import logging
import datetime
import multiprocessing

import tqdm

global_lock = multiprocessing.Lock()

__all__ = (
    "prepare_dir",
    "normlize_path",
    "read_pickle_file",
    "read_json_file",
    "read_list_file",
    "read_list_field",
    "read_map_file",
    "write_pickle_file",
    "write_json_file",
    "write_list_file",
    "traverse_directory",
    "initialize_logger",
    "get_global_logger",
    "get_local_logger",
    "ColorWrapper",
    "get_progress_tracker",
    "log_and_raise_exception",
    "format_time_interval",
    "merge_overlap",
)


def prepare_dir(path):
    """Make dir if necessary."""

    dirname = os.path.dirname(path)
    # 当前目录直接返回
    if not dirname: return None

    with global_lock:
        os.makedirs(dirname, exist_ok=True)


def normlize_path(path):
    """normalize path to standard format."""

    path = os.path.expanduser(path)
    path = os.path.realpath(path)
    path = os.path.abspath(path)
    path = os.path.normpath(path)
    return path


def read_pickle_file(path, *, check=True):
    "Read file in pickle format."

    if check:
        assert path and os.path.exists(path), \
            f"Failed to read file: {path}"
    if not path: return None
    if not os.path.exists(path): return None
    with open(path, "rb") as srcfile:
        return pickle.load(srcfile)


def read_json_file(path, *, check=True):
    "Read file in json format."

    if check:
        assert path and os.path.exists(path), \
            f"Failed to read file: {path}"
    if not path: return None
    if not os.path.exists(path): return None
    with open(path, "rb") as srcfile:
        return json.load(srcfile)


def read_list_file(path, sep=None, *, check=True):
    "Read file as a list of strings."

    if check:
        assert path and os.path.exists(path), \
            f"Failed to read file: {path}"
    if not path: return None
    if not os.path.exists(path): return None
    with open(path, "r") as srcfile:
        lines = [l.strip() for l in srcfile]
        # 去掉空行和注释行(以'#'开头的行)
        lines = [l for l in lines if l and (not l.startswith("#"))]
    if isinstance(sep, str):
        lines = [l.split(sep) for l in lines]
        lines = [tuple(filter(None, l)) for l in lines]
    return lines


def read_list_field(path, field=0, sep=" ", *, check=True):
    "Read file and extract filed."

    lines = read_list_file(path, sep, check=check)
    if not lines: return None
    if isinstance(field, int):
        return [n[field] for n in lines]
    return [[n[i] for i in field] for n in lines]


def read_map_file(path, vtype=str, *, check=True):
    "Read file as a dictionay."

    lines = read_list_file(path, " ", check=check)
    if not lines: return None
    return {k: vtype(v) for k, v in lines}


def write_pickle_file(data, path):
    """Write data to pickle file."""

    prepare_dir(path)
    with open(path, "wb") as dstfile:
        pickle.dump(data, dstfile, protocol=2)


def write_json_file(data, path):
    """Write data to json file."""

    prepare_dir(path)
    with open(path, "w") as dstfile:
        json.dump(data, dstfile, indent=2)


def write_list_file(data, path, sep=" "):
    """Write list to txt file."""

    prepare_dir(path)
    with open(path, "w") as dstfile:
        for line in data:
            if isinstance(line, (tuple, list)):
                line = sep.join([str(item) for item in line])
            dstfile.write(line + "\n")


def traverse_directory(root, stopf=None, targetf=None):
    """Traverse directory.

    Args:
        targetf: function with one argument. Check whether a target path
            can be produced from the current path or not, if it is the
            case, return target path, otherwise return None. When function
            `targetf` returns a path, yield it.
        stopf: function with one argument. Check whether to enter current
            directory or not. If current path is a directory and this
            function returns False, enter current path.
    """

    # 默认状况下, 相当于listdir
    stopf = stopf or (lambda path: True)
    targetf = targetf or (lambda path: path if stopf(path) else None)
    if not os.path.exists(root): return
    for name in os.listdir(root):
        path = os.path.join(root, name)
        target = targetf(path)
        if target: yield target
        if os.path.isdir(path) and (not stopf(path)):
            yield from traverse_directory(path, stopf, targetf)


def initialize_logger(name=None, file=None, *, display=True):
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

    # 局部的logger是全局logger的child, 这里防止局部的log扩散到全局log中
    logger.propagate = False
    logger.setLevel(logging.INFO)

    # 这里行号设置为3个字符宽度, 因为我自己写的程序一个文件很少超过1000行
    fmt = "%(asctime)s %(filename)s:%(lineno)3d] %(levelname)s: %(message)s"
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


def get_global_logger(logging_root):
    date = str(datetime.date.today())
    logging_file = os.path.join(logging_root, date, "log_global.txt")
    prepare_dir(logging_file)
    return initialize_logger(None, logging_file, display=True)


def get_local_logger(name, logging_root):
    assert name != "global"
    date = str(datetime.date.today())
    logging_file = os.path.join(logging_root, date, f"log_{name}.txt")
    prepare_dir(logging_file)
    return initialize_logger(name, logging_file, display=False)


class ColorWrapper:

    @staticmethod
    def color(text, color):
        # yapf: disable
        ansi_colors = {
            "black":     "0;30",    "bright black":     "0;90",
            "red":       "0;31",    "bright red":       "0;91",
            "green":     "0;32",    "bright green":     "0;92",
            "yellow":    "0;33",    "bright yellow":    "0;93",
            "blue":      "0;34",    "bright blue":      "0;94",
            "magenta":   "0;35",    "birght magenta":   "0;95",
            "cyan":      "0;36",    "bright cyan":      "0;96",
            "white":     "0;37",    "brignt white":     "0;97",
        }
        # yapf: enable
        all_colors = {}
        for key, value in ansi_colors.items():
            all_colors[key.lower().replace(" ", "")] = value
        all_colors["gray"] = ansi_colors["bright black"]
        color = color.lower().replace(" ", "")
        assert color in all_colors, f"Unknown color: {color}"
        return f"\033[{all_colors[color]}m{text}\033[0m"

    @staticmethod
    def black(text):
        return ColorWrapper.color(text, "black")

    @staticmethod
    def red(text):
        return ColorWrapper.color(text, "red")

    @staticmethod
    def green(text):
        return ColorWrapper.color(text, "green")

    @staticmethod
    def yellow(text):
        return ColorWrapper.color(text, "yellow")

    @staticmethod
    def blue(text):
        return ColorWrapper.color(text, "blue")

    @staticmethod
    def magenta(text):
        return ColorWrapper.color(text, "magenta")

    @staticmethod
    def cyan(text):
        return ColorWrapper.color(text, "cyan")

    @staticmethod
    def white(text):
        return ColorWrapper.color(text, "white")

    @staticmethod
    def gray(text):
        return ColorWrapper.color(text, "gray")


def get_progress_tracker(iterable=None, total=None):
    return tqdm.tqdm(
        iterable=iterable,
        total=total,
        mininterval=5,
        ascii=True,
        unit=" samples",
    )


def log_and_raise_exception(message, logger=None):
    logger = logger or logging.getLogger()
    logger.fatal(message)
    raise Exception(message)


def format_time_interval(value, unit="s"):
    if unit == "ms" and value > 1000:
        unit, value = "s", value / 1000
    if unit == "s" and value > 60:
        unit, value = "m", value / 60
    if unit == "m" and value > 60:
        unit, value = "h", value / 60
    if unit == "h" and value > 24:
        unit, value = "d", value / 24
    return f"{value:.2f}{unit}"


def merge_overlap(groups, overlapf=None, mergef=None):
    # 默认情况下, groups中的元素是set类型
    overlapf = overlapf or (lambda x, y: x & y)
    mergef = mergef or (lambda x, y: x | y)
    if len(groups) < 2: return groups

    def _merge_one(anchor, samples):
        """将`samples`中的元素merge到`anchor`中."""
        remains = []
        for s in samples:
            if overlapf(anchor, s):
                anchor = mergef(anchor, s)
            else:
                remains.append(s)
        if len(remains) == len(samples):
            return anchor, remains
        return _merge_one(anchor, remains)

    anchor, remains = _merge_one(groups[0], groups[1:])
    return [anchor] + merge_overlap(remains, overlapf, mergef)


if __name__ == "__main__":
    pass
