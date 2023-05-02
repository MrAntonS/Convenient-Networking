"""
    history
    ~~~~~~~

    A tiny example to show how pagination works.

    :copyright: (c) 2011-2013 by Selectel, see AUTHORS for details.
    :license: LGPL, see LICENSE for more details.
"""

import os
import random
import string
import sys
import json

import pyte
from pyte import modes as mo


def print_screen(screen, text):

    for idx, line in enumerate(screen.display, 1):
        print("{0:2d} {1} ¶".format(idx, line))

    input(os.linesep + os.linesep + text)


def random_string(n, alphabet=string.ascii_letters + " "):
    return "".join(random.choice(alphabet) for _ in range(n))


if __name__ == "__main__":
    # ``ratio=1`` means scroll the whole screen.
    screen = pyte.HistoryScreen(80, 12, ratio=1)
    screen.set_mode(mo.LNM)
    stream = pyte.Stream(screen)

    pages = 3
    stream.feed(os.linesep.join(random_string(screen.columns)
                                for _ in range(screen.lines * pages)))
    print_screen(screen, "Hit ENTER to move up!")
    for _, i in enumerate(screen.history.top):
        print(_, end="")
        for j in i:
            print(i[j].data, end='')
        print()
    screen._reset_history()
    print("After resetting")
    for _, i in enumerate(screen.history.top):
        print(_, end="")
        for j in i:
            print(i[j].data, end='')
        print()