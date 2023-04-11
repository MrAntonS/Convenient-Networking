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
    'gray': QColor(0xc0, 0xc0, 0xc0),
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
        # print(host)
        self.__initUI(ComboBoxSelection, host, username, password)
        self.lastTimeKeyWasPressed = time.perf_counter()
        self.PasteShortCut = QShortcut(QKeySequence('Ctrl+V'), self)
        self.CopyShortCut = QShortcut(QKeySequence('Ctrl+Shift+C'), self)
        self.CopyAndBreakShortCut = QShortcut(QKeySequence('Ctrl+C'), self)
        self.space = QShortcut(QKeySequence('Space'), self)
        self.BreakIntoRommonShortCut = QShortcut(
            QKeySequence('Ctrl+Shift+R'), self)
        self.space.activated.connect(lambda: self.backend.write(' '))
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
        self.textColors = QColorConstants.Green
        self.textBackground = QColor(40, 40, 40)
        self.Colors.setColor(
            QPalette().ColorRole["Text"], self.textColors)
        self.Colors.setColor(
            QPalette().ColorRole["Base"], self.textBackground)
        self.Colors.setColor(
            QPalette().ColorRole["Window"], QColorConstants.Black)
        self.setPalette(self.Colors)
        self.setFont(self.Font)
        self.track_cursor = True
        # The cursor that writes current screen
        self.MainCursor = self.textCursor()
        # The Cursor that gets displayed
        self.DisplayedCursor = self.textCursor()
        # The Cursor that stays above the terminal and write down history that comes in
        self.HistoryCursor = self.textCursor()

        # Character Formatting
        self.charFormat = QTextCharFormat()
        self.charFormat.setFont(self.Font)

        self.lines = 24
        self.protocol = 0
        self.columns = 100
        self.BreakFeatureTimer = QTimer()
        self.BreakFeatureTimer.setInterval(500)
        self.BreakFeatureTimer.timeout.connect(self.BreakIntoRommon)
        self.show()
        host = host.strip(' /')
        host = host.split('://')
        # To-Do rewrite this as a dictionary
        clients = {
            'telnet': TelnetBackend,
            'ssh': SSHBackend
        }
        try:
            self.backend = clients[host[0].lower()](self.columns, self.lines, host[-1], username, password) if \
                len(host) == 2 else clients[ComboBoxSelection.lower()](self.columns, self.lines, host[-1], username, password)
            self.protocol = 1 if isinstance(self.backend, TelnetBackend) else 2
        except KeyError:
            self.backend = clients[ComboBoxSelection.lower()](self.columns, self.lines, host[-1], username, password)
            self.protocol = 1 if isinstance(self.backend, TelnetBackend) else 2
            
        self.Clear_Last_24_lines()
        self.HistoryCursor.movePosition(
            QTextCursor.MoveOperation.Start, QTextCursor.MoveMode.MoveAnchor)
        self.timerID = self.startTimer(1)

    def Clear_Last_24_lines(self):
        x = ' ' * (self.columns) + '\n'
        self.MainCursor.insertText(x * self.lines)
        self.MainCursor.deletePreviousChar()

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

    def BreakIntoRommon(self):
        self.backend.write(b'\x03')
        self.backend.write(b'\x03')
        self.backend.write(b'\x0C')
        self.backend.write(b'\x0C')
        self.backend.write(b'\x18')
        self.backend.write(telnetlib.IAC)
        self.backend.write(telnetlib.BRK)

    def Paste(self):
        self.backend.write(bytes(QApplication.clipboard().text(), 'utf-8'))

    def paintEvent(self, a0: QPaintEvent) -> None:
        super(Terminal, self).paintEvent(a0)
        p = QPainter(self.viewport())
        self.Move_Cursor_to_desired_line(
            self.backend.screen.cursor.y + 1, self.DisplayedCursor)
        self.DisplayedCursor.movePosition(QTextCursor.MoveOperation.Right,
                                          QTextCursor.MoveMode.MoveAnchor, self.backend.screen.cursor.x)
        p.setPen(self.CursorColor)
        rect = self.cursorRect(self.DisplayedCursor)
        rect.setWidth(0)
        p.drawRect(rect)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        self.lastTimeKeyWasPressed = time.perf_counter()
        if e.key() in keymap.keys():
            self.backend.write(keymap[e.key()])
        else:
            self.backend.write(e.text())
        return super().keyPressEvent(e)

    def timerEvent(self, e: QTimerEvent) -> None:
        if not self.backend.connected:
            self.killTimer(self.timerID)
            self.ConnectionSignal.emit()
            return
        if not self.isVisible():
            return super().timerEvent(e)
        if len(self.backend.screen.dirty) == 0 and self._cursorX == self.backend.cursor().x and self._cursorY == self.backend.cursor().y:
            return super().timerEvent(e)
        self.WriteToUI()
        self._cursorX = self.backend.cursor().x
        self._cursorY = self.backend.cursor().y
        return super().timerEvent(e)

    def Push_History_to_the_bottom(self):
        if not self.backend.screen.history.top:
            # No history
            return
        self.Move_Cursor_to_desired_line(1, self.HistoryCursor)
        self.HistoryCursor.movePosition(QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.MoveAnchor)
        history = self.backend.screen.history.top
        while history:
            line = history.popleft()
            same_text = ''
            pre_char = None
            for j in line:
                char = line[j]
                if pre_char and char.bg == pre_char.bg and char.fg == pre_char.fg:
                    same_text += char.data
                    continue
                else:
                    if same_text != '':
                        self.HistoryCursor.insertText(same_text, self.charFormat)
                        same_text = ''
                    same_text += char.data
                    if char.fg == 'default':
                        self.charFormat.setForeground(self.textColors)
                    else:
                        self.charFormat.setForeground(
                            colors[char.fg]) if char.fg != 'white' else self.charFormat.setForeground(colors['gray'])

                    if char.bg == 'default':
                        self.charFormat.setBackground(self.textBackground)
                    else:
                        self.charFormat.setBackground(colors[char.bg])

                    pre_char = char
            if same_text != '':
                self.HistoryCursor.insertText(same_text, self.charFormat)
            self.HistoryCursor.insertText('\n')

        

    def Move_Cursor_to_desired_line(self, line_num, cursor: QTextCursor):
        cursor.movePosition(QTextCursor.MoveOperation.End,
                            QTextCursor.MoveMode.MoveAnchor)
        cursor.movePosition(QTextCursor.MoveOperation.Up,
                            QTextCursor.MoveMode.MoveAnchor, self.lines - line_num)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine,
                            QTextCursor.MoveMode.MoveAnchor)

    def WriteToUI(self):
        self.Push_History_to_the_bottom()
        buffer = self.backend.screen.buffer
        screen = self.backend.screen.display
        dirty = self.backend.screen.dirty
        while dirty:
            i = dirty.pop()
            line = buffer[i].copy()
            string = screen[i - 1]
            if self.BreakFeatureTimer.isActive():
                if re.search('rom.*>', string) != None or re.search("load.*>", string) or re.search("swit.*:", string):
                    self.SwitchBreakFeature()
            pre_char = None
            self.Move_Cursor_to_desired_line(
                line_num=i+1, cursor=self.MainCursor)
            self.MainCursor.movePosition(
                QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
            # Very important
            self.MainCursor.removeSelectedText()
            same_text = ''
            for j in line:
                char = line[j]
                if pre_char and char.bg == pre_char.bg and char.fg == pre_char.fg:
                    same_text += char.data
                    continue
                else:
                    if same_text != '':
                        self.MainCursor.insertText(same_text, self.charFormat)
                        same_text = ''
                    same_text += char.data
                    if char.fg == 'default':
                        self.charFormat.setForeground(self.textColors)
                    else:
                        self.charFormat.setForeground(
                            colors[char.fg]) if char.fg != 'white' else self.charFormat.setForeground(colors['gray'])

                    if char.bg == 'default':
                        self.charFormat.setBackground(self.textBackground)
                    else:
                        self.charFormat.setBackground(colors[char.bg])

                    pre_char = char
            if same_text != '':
                self.MainCursor.insertText(same_text, self.charFormat)
        self.MainCursor.movePosition(
            QTextCursor.MoveOperation.Start, QTextCursor.MoveMode.MoveAnchor)
        self.MainCursor.insertText('\n')
        self.MainCursor.deletePreviousChar()
        if self.track_cursor:
            self.setTextCursor(self.DisplayedCursor)

    def closeEvent(self, a0: QCloseEvent) -> None:
        # print('closed')
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
        self.reconnectBtn = QPushButton()
        self.reconnectBtn.setText("Reconnect")
        self.reconnectBtn.clicked.connect(self.reconnect)
        self.reconnectBtn.setFixedSize(100, 40)
        self.reconnectBtn.hide()
        self.layout.addWidget(self.term)
        self.layout.addWidget(self.reconnectBtn)

    def reconnect(self):
        self.term.backend.reconnect()
        self.term.timerID = self.term.startTimer(1)
        self.reconnectBtn.hide()
        self.term.show()

    def __initFailedUI(self):
        if self.reconnectBtn.isVisible():
            return
        self.reconnectBtn.show()
        self.term.hide()

    def CheckIfBackendIsStillConnected(self):
        return self.term.backend.connected

    def closeEvent(self, event):
        self.term.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    print('Debug Mode')
    term = QTerminal('ssh://10.122.187.40/')
    sys.exit(app.exec())
