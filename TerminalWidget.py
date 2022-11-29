from LibraryImport import *
from qterminal.backend import TelnetBackend, SSHBackend
from qterminal.mux import mux
logging.basicConfig(level=logging.INFO)

colors = {
    'black': QColor(0x00, 0x00, 0x00),
    'red': QColor(0xaa, 0x00, 0x00),
    'green': QColor(0x00, 0xaa, 0x00),
    'blue': QColor(0x00, 0x00, 0xaa),
    'cyan': QColor(0x00, 0xaa, 0xaa),
    'brown': QColor(0xaa, 0xaa, 0x00),
    'yellow': QColor(0xff, 0xff, 0x44),
    'magenta': QColor(0xaa, 0x00, 0xaa),
    'white': QColor(0xff, 0xff, 0xff),
    'gray': QColor(0xc0, 0xc0, 0xc0)
}
keymap = {
    Qt.Key.Key_Backspace: chr(127),
    Qt.Key.Key_Escape: chr(27),
    Qt.Key.Key_AsciiTilde: chr(126),
    Qt.Key.Key_Up: '\x1b[A',
    Qt.Key.Key_Down: '\x1b[B',
    Qt.Key.Key_Left: '\x1b[D',
    Qt.Key.Key_Right: '\x1b[C',
    Qt.Key.Key_PageUp: "~1",
    Qt.Key.Key_PageDown: "~2",
    Qt.Key.Key_Home: "~H",
    Qt.Key.Key_End: "~F",
    Qt.Key.Key_Insert: "~3",
    Qt.Key.Key_Delete: "~4",
    Qt.Key.Key_F1: "~a",
    Qt.Key.Key_F2: "~b",
    Qt.Key.Key_F3: "~c",
    Qt.Key.Key_F4: "~d",
    Qt.Key.Key_F5: "~e",
    Qt.Key.Key_F6: "~f",
    Qt.Key.Key_F7: "~g",
    Qt.Key.Key_F8: "~h",
    Qt.Key.Key_F9: "~i",
    Qt.Key.Key_F10: "~j",
    Qt.Key.Key_F11: "~k",
    Qt.Key.Key_F12: "~l",
}


class Terminal(QTextEdit):
    ConnectionSignal = pyqtSignal()

    def __init__(self, ComboBoxSelection, host, username=None, password=None):
        super(Terminal, self).__init__()
        print(host)
        self.__initUI(ComboBoxSelection, host, username, password)
        self.PasteShortCut = QShortcut(QKeySequence('Ctrl+V'), self)
        self.CopyShortCut = QShortcut(QKeySequence('Ctrl+Shift+C'), self)
        self.CopyAndBreakShortCut = QShortcut(QKeySequence('Ctrl+C'), self)
        self.BreakIntoRommonShortCut = QShortcut(
            QKeySequence('Ctrl+Shift+R'), self)
        self.BreakIntoRommonShortCut.activated.connect(self.SwitchBreakFeature)
        self.PasteShortCut.activated.connect(self.Paste)
        self.CopyShortCut.activated.connect(self.Copy)
        self.CopyAndBreakShortCut.activated.connect(self.CopyAndBreak)

    def __initUI(self, ComboBoxSelection, host, username=None, password=None):
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setReadOnly(True)
        self.setContentsMargins(0, 0, 0, 0)
        self.setContextMenuPolicy(
            Qt.ContextMenuPolicy.NoContextMenu)
        self.Font = QFont()
        self.Font.setFamily('Consolas')
        self.Font.setPixelSize(15)
        self.Colors = QPalette()
        self.CursorColor = QColorConstants.White
        self.Colors.setColor(
            QPalette().ColorRole["Text"], QColorConstants.Green)
        self.Colors.setColor(
            QPalette().ColorRole["Base"], QColor(40, 40, 40))
        self.Colors.setColor(
            QPalette().ColorRole["Window"], QColorConstants.Black)
        self.setPalette(self.Colors)
        self.setFont(self.Font)
        self.previousScrollValue = 0
        self.isProgramMovingScroll = False
        self.Cursor = self.textCursor()
        self._cursorX = 0
        self._cursorY = 0
        self.lines = 48
        self.columns = 100
        self.scrollingPage = False
        self.BreakFeatureTimer = QTimer()
        self.BreakFeatureTimer.setInterval(500)
        self.BreakFeatureTimer.timeout.connect(self.BreakIntoRommon)
        self.scroll = None
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.show()
        self.CheckCharSize()
        self.Resize()
        host = host.strip(' /')
        host = host.split('://')
        if len(host) == 2:
            if host[0] == "telnet":
                self.backend = TelnetBackend(self.columns, self.lines, host[1])
            elif host[0] == 'ssh':
                self.backend = SSHBackend(
                    self.columns, self.lines, host[1], username, password)
            else:
                if ComboBoxSelection == 'Telnet':
                    self.backend = TelnetBackend(
                        self.columns, self.lines, host[1])
                elif ComboBoxSelection == 'SSH':
                    self.backend = SSHBackend(
                        self.columns, self.lines, host[1], username, password)
        elif len(host) == 1:
            if ComboBoxSelection == 'Telnet':
                self.backend = TelnetBackend(self.columns, self.lines, host[0])
            elif ComboBoxSelection == 'SSH':
                self.backend = SSHBackend(
                    self.columns, self.lines, host[0], username, password)

        self.timerID = self.startTimer(1)

    def Resize(self):
        try:
            # int(self.width() // self._charWidth)
            self.backend.resize(
                85, int(self.height() // (self._charHeight - 2)))
            self.clear()
            x = ' ' * (85) + '\n'
            self.Cursor.insertText(
                (x) * (int(self.height() // (self._charHeight - 2))))
        except Exception as e:
            pass
    
    def Copy(self):
        data = QMimeData()
        data.setText(self.textCursor().selection().toPlainText())
        QApplication.clipboard().setMimeData(data)

    def CopyAndBreak(self):
        data = QMimeData()
        data.setText(self.textCursor().selection().toPlainText())
        QApplication.clipboard().setMimeData(data)
        self.backend.write(b'\x03')

    def SwitchBreakFeature(self):
        if self.BreakFeatureTimer.isActive():
            self.BreakFeatureTimer.stop()
            self.CursorColor = QColorConstants.White
        else:
            self.BreakFeatureTimer.start()
            self.CursorColor = QColorConstants.Red
        self.updateCursor()

    def updateCursor(self):
        self.Cursor.insertText('\n')
        self.Cursor.deletePreviousChar()

    def BreakIntoRommon(self):
        self.backend.write(b'\x03')
        self.backend.write(b'\x03')
        self.backend.write(b'\x0C')
        self.backend.write(b'\x0C')
        self.backend.write(b'\x18')
        self.backend.write(telnetlib.IAC)
        self.backend.write(telnetlib.BRK)

    def CheckCharSize(self):
        self.clear()
        self.Cursor.insertText('aa')
        while self.Cursor.columnNumber() > 1:
            columnNum = self.Cursor.columnNumber()
            self.Cursor.insertText('a')
        self._charWidth = self.width() / columnNum
        self.clear()
        rowNum = 0
        while self.verticalScrollBar().maximum() == 0:
            self.Cursor.insertText('\n')
            rowNum += 1
        self._charHeight = self.height() / rowNum
        self.clear()
        x = ' ' * (columnNum) + '\n'
        self.Cursor.insertText(x * rowNum)

    def Paste(self):
        self.backend.write(bytes(QApplication.clipboard().text(), 'utf-8'))

    def LineSize(self):
        return self.width() // self._charWidth, self.height() // self._charHeight

    def set_scroll(self, scroll):
        self.scroll = scroll
        self.scroll.setMaximum(0)
        tmp = len(self.backend.screen.history.top) + \
            len(self.backend.screen.history.bottom) - 1
        self.scroll.setMinimum(tmp if tmp > 0 else 0)
        self.scroll.valueChanged.connect(self.ValueChanged)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        try:
            self.Resize()
        except Exception as e:
            pass

        return super().resizeEvent(a0)

    def ValueChanged(self, value):
        if self.isProgramMovingScroll:
            self.isProgramMovingScroll = False
            self.previousScrollValue = value
            return
        self.scrollingPage = True
        if self.previousScrollValue > value:
            for i in range(abs(value - self.previousScrollValue)):
                self.backend.screen.prev_page()
        else:
            for i in range(abs(value - self.previousScrollValue)):
                self.backend.screen.next_page()
        self.scrollingPage = False
        self.previousScrollValue = value

    def paintEvent(self, a0: QPaintEvent) -> None:
        if self.scroll.value() == self.scroll.maximum():
            p = QPainter(self.viewport())
            p.fillRect(self.cursorRect(self.Cursor),
                       self.CursorColor)
        return super().paintEvent(a0)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() in keymap.keys():
            self.backend.write(keymap[e.key()])
        else:
            self.backend.write(e.text())
        return super().keyPressEvent(e)

    def timerEvent(self, e: QTimerEvent) -> None:
        if not self.backend.connected:
            print('Emmited')
            self.killTimer(self.timerID)
            self.ConnectionSignal.emit()
            return
        if not self.isVisible():
            return super().timerEvent(e)
        if self.scrollingPage:
            return super().timerEvent(e)
        # try:
        #     if self.LineSize() != (self.columns, self.lines):
        #         print('eee')
        #         self.backend.resize(
        #             80, int(self.height() // self._charHeight))
        #         self.columns, self.lines = self.LineSize()
        # except:
        #     pass
        if len(self.backend.screen.dirty) == 0 and self._cursorX == self.backend.cursor().x and self._cursorY == self.backend.cursor().y:
            return super().timerEvent(e)
        tmp = len(self.backend.screen.history.top) + \
            len(self.backend.screen.history.bottom)
        if tmp != self.scroll.maximum():
            self.scroll.setMaximum(tmp if tmp > 0 else 0)
            self.isProgramMovingScroll = True
            self.scroll.setValue(self.scroll.maximum())
        self.WriteToUI()
        self._cursorX = self.backend.cursor().x
        self._cursorY = self.backend.cursor().y
        # self.verticalScrollBar().setValue(round((self.backend.screen.cursor.y / 48) * self.verticalScrollBar().maximum()))
        # f = QFontMetrics(self.Font)
        return super().timerEvent(e)

    def WriteToUI(self):
        try:
            Cursor = self.textCursor()
            charFormat = QTextCharFormat()
            charFormat.setFont(self.Font)
            x = self.backend.screen.dirty.copy()
            y = self.backend.screen.buffer.copy()
            z = self.backend.screen.display.copy()
            for i in x:
                self.backend.screen.dirty.remove(i)
                line = y[i]
                string = z[i]
                if self.BreakFeatureTimer.isActive():
                    if re.search('rom.*>', string) != None or re.search("load.*>", string) or re.search("swit.*:", string):
                        self.SwitchBreakFeature()
                pre_char = None
                Cursor.movePosition(
                    Cursor.MoveOperation.Start, Cursor.MoveMode.MoveAnchor)
                Cursor.movePosition(
                    Cursor.MoveOperation.Down, Cursor.MoveMode.MoveAnchor, i)
                Cursor.movePosition(
                    Cursor.MoveOperation.EndOfLine, Cursor.MoveMode.KeepAnchor)
                # Cursor.removeSelectedText()
                same_text = ''
                for j in y[i]:
                    char = line[j]
                    if pre_char and char.bg == pre_char.bg and char.fg == pre_char.fg:
                        same_text += char.data
                        continue
                    else:
                        if same_text != '':
                            Cursor.insertText(same_text, charFormat)
                            same_text = ''
                        same_text += char.data
                        if char.fg == 'default':
                            pass
                        else:
                            charFormat.setForeground(
                                colors[char.fg]) if char.fg != 'white' else charFormat.setForeground(colors['gray'])
                        if char.bg == 'default':
                            pass
                        else:
                            charFormat.setBackground(colors[char.bg])
                        pre_char = char
                if same_text != '':
                    Cursor.insertText(same_text, charFormat)
                    same_text = ''
                Cursor.insertText(' ' * (85 - len(y[i])))
            self.Cursor.movePosition(
                self.Cursor.MoveOperation.Start, self.Cursor.MoveMode.MoveAnchor)
            self.updateCursor()
            self.Cursor.movePosition(self.Cursor.MoveOperation.Down,
                                     self.Cursor.MoveMode.MoveAnchor, self.backend.screen.cursor.y)
            self.Cursor.movePosition(self.Cursor.MoveOperation.Right,
                                     self.Cursor.MoveMode.MoveAnchor, self.backend.screen.cursor.x)
        except Exception as e:
            pass

        # self.Cursor.insertText('\n'.join(self.backend.screen.display))

    def wheelEvent(self, e: QWheelEvent) -> None:
        y = e.angleDelta().y()
        if y < 0:
            self.scroll.setValue(self.scroll.value() + 2)
        else:
            self.scroll.setValue(self.scroll.value() - 2)
        return super().wheelEvent(e)

    def closeEvent(self, a0: QCloseEvent) -> None:
        print('closed')
        self.killTimer(self.timerID)
        self.backend.close()
        self.BreakFeatureTimer.stop()
        return super().closeEvent(a0)


class QTerminal(QWidget):

    def __init__(self, ComboBoxSelection, host, username=None, password=None):
        super(QTerminal, self).__init__()
        self.resize(800, 600)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.term = Terminal(ComboBoxSelection, host, username, password)
        self.term.ConnectionSignal.connect(self.__initFailedUI)
        self.term.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.scroll_bar = QScrollBar(Qt.Orientation.Vertical, self.term)
        self.scroll_bar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.reconnectBtn = QPushButton()
        self.reconnectBtn.setText("Reconnect")
        self.reconnectBtn.clicked.connect(self.reconnect)
        self.reconnectBtn.setFixedSize(100, 40)
        # self.term.hide()
        # self.scroll_bar.hide()
        self.reconnectBtn.hide()
        self.layout.addWidget(self.term)
        self.layout.addWidget(self.scroll_bar)
        self.layout.addWidget(self.reconnectBtn)
        # self.term.hide()
        # self.scroll_bar.hide()

        self.term.set_scroll(self.scroll_bar)

    def reconnect(self):
        self.term.backend.reconnect()
        self.term.timerID = self.term.startTimer(1)
        self.reconnectBtn.hide()
        self.term.show()
        self.scroll_bar.show()

    def __initFailedUI(self):
        if self.reconnectBtn.isVisible():
            return
        self.reconnectBtn.show()
        self.term.hide()
        self.scroll_bar.hide()

    def CheckIfBackendIsStillConnected(self):
        return self.term.backend.connected

    def closeEvent(self, event):
        self.term.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    print('Debug Mode')
    term = QTerminal('ssh://10.122.187.40/')
    term.term.CheckCharSize()
    sys.exit(app.exec())
