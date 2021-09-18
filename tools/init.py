#! /usr/bin/env python
# coding: utf-8

import os
import sys
import warnings
warnings.filterwarnings("ignore")

dirname = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(dirname, ".."))


def check_pylint_env():
    # pylint: disable=import-outside-toplevel
    import pylint.config
    assert pylint.config.find_pylintrc(), \
        "pylint is not properly configured."
    print("pylint is properly configured.")


if __name__ == "__main__":
    check_pylint_env()
