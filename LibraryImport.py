#!/usr/bin/python3
import sys
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import time
import telnetlib
import os
import socket
import re
import logging
import threading
import select
from QTermWidget import QTermWidget


class Telnet_(telnetlib.Telnet):
    def write(self, buffer):
        """Write a string to the socket, doubling any IAC characters.

        Can block if the connection is blocked.  May raise
        OSError if the connection is closed.

        """
        sys.audit("telnetlib.Telnet.write", self, buffer)
        self.msg("send %r", buffer)
        self.sock.sendall(buffer)

class Terminal(QTermWidget):
    def __init__(self, process: str, args: list):
        super().__init__(0)
        self.finished.connect(self.close)
        self.setTerminalSizeHint(False)
        self.setColorScheme("Tango")
        self.setShellProgram(process)
        self.setArgs(args)
        self.startShellProgram()