import sys
from PyQt6 import uic
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import time
import telnetlib
import os
import socket
import re
import logging
import threading
import select


class Telnet_(telnetlib.Telnet):
    def write(self, buffer):
        """Write a string to the socket, doubling any IAC characters.

        Can block if the connection is blocked.  May raise
        OSError if the connection is closed.

        """
        sys.audit("telnetlib.Telnet.write", self, buffer)
        self.msg("send %r", buffer)
        self.sock.sendall(buffer)
