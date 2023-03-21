from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QWindow, QResizeEvent
import sys
from subprocess import Popen, PIPE, STDOUT
import win32gui
import win32process
from time import sleep


def get_hwnds_for_pid (pid):
    def callback (hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds


class QEmbed(QWidget):
    def __init__(self):
        super(QEmbed, self).__init__()
        exePath = "putty telnet://F241-10-17-COMM:2031"
        # exePath = "notepad"
        self.x = Popen(exePath)
        print(self.x.pid)
        sleep(3)
        hwnd = get_hwnds_for_pid(self.x.pid)
        hwnd1 = win32gui.FindWindow(None, "Calculator")
        print(hwnd, hwnd1) 
        window = QWindow.fromWinId(hwnd[-1])
        self.y = self.createWindowContainer(window, self, )
        self.resize(1000, 600)
        self.y.resize(self.size())
        self.show()
    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.y.resize(a0.size())
        return super().resizeEvent(a0)


if __name__ == "__main__":
    args = sys.argv
    app = QApplication(args)
    t = QEmbed()
    t.show()
    sys.exit(app.exec())
