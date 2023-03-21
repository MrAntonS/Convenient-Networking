from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QWindow
import sys
from subprocess import Popen, PIPE, STDOUT
import win32gui
from time import sleep


class QEmbed(QWidget):
    def __init__(self):
        super(QEmbed, self).__init__()
        exePath = "putty google.com"
        x = Popen(exePath)
        sleep(3)
        hwnd = win32gui.FindWindow(None, "Putty")
        print(hwnd, x.pid) 
        window = QWindow.fromWinId(hwnd)
        window.resize(6000, 5000)
        x = self.createWindowContainer(window, self)
        self.resize(1000, 600)
        x.resize(self.size())
        self.show()


if __name__ == "__main__":
    args = sys.argv
    app = QApplication(args)
    t = QEmbed()
    t.show()
    sys.exit(app.exec())
