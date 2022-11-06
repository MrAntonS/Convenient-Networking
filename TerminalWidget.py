from LibraryImport import *

ESC = chr(0x1B)
BELL = chr(0x07)
BACKSPACE = chr(0x08)
TAB = chr(0x09)
CARRIAGE_RETURN = chr(0x0D)


class Terminal(QTextEdit):
    NORMAL = 0
    ESCAPE_SEQ = 1
    CSI = 2

    def __init__(self):
        super(Terminal, self).__init__()
        self.setAcceptRichText(False)
        self.Cursor = self.textCursor()
        self.setTextCursor(self.Cursor)
        self.CursorColor = QColorConstants.White
        self.buffer = list()
        self.state = self.NORMAL
        self.MoveMode = QTextCursor.MoveMode
        self.MoveOp = QTextCursor.MoveOperation
        self.params = []
        self.TemporaryStorage = 0
        self._c0Handlers = {
            BELL: self.MakeSound,
            BACKSPACE: self.MoveCarriageToTheLeft,
            CARRIAGE_RETURN: self.MoveCarriageToTheStartOfTheLine,
            ESC: self.ChangeStateToEscSeq,
            '\r': self.MoveCarriageToTheStartOfTheLine,
            '\n': self.MoveCarriageToTheNewLine
        }

        self._FeHandlers = {
            '[': self.ChangeStateToCSI
        }

        self._CsiHandlers = {
            'C': self.MoveCarriageToTheRight,
            'D': self.MoveCarriageToTheLeft,
            'E': self.MoveCarriageToTheNewLine,
            'F': self.MoveCarriageToPreviousLine,
            'H': self.MoveCursorToColumn,
            'J': self.EraseInDisplay,
            'K': self.EraseInLine,
        }
        self.UI_Update = QTimer()
        self.UI_Update.timeout.connect(self.UpdateUI)
        self.UI_Update.start()

    def paintEvent(self, a0: QPaintEvent) -> None:
        p = QPainter(self.viewport())
        p.fillRect(self.cursorRect(self.Cursor),
                   self.CursorColor)
        return super().paintEvent(a0)

    def AddTextToBuffer(self, buffer):
        try:
            self.buffer += list(buffer)
        except:
            return False
        return True

    # Will be used to make bell sound
    def MakeSound(self):
        pass

    # Moves Cursor to the left
    def MoveCarriageToTheLeft(self):
        if self.params == []:
            param = 1
        else:
            param = max(self.params.pop(0), 1)
        self.params = []
        self.Cursor.movePosition(
            self.MoveOp.Left, self.MoveMode.MoveAnchor, param)

    # Moves Cursor to the right
    def MoveCarriageToTheRight(self):
        if self.params == []:
            param = 1
        else:
            param = max(self.params.pop(0), 1)
        self.params = []
        self.Cursor.movePosition(
            self.MoveOp.Right, self.MoveMode.MoveAnchor, param)

    # Move Cursor to previous line
    def MoveCarriageToPreviousLine(self):
        if self.params == []:
            param = 1
        else:
            param = max(self.params.pop(0), 1)
        self.params = []
        self.Cursor.movePosition(
            self.MoveOp.Up, self.MoveMode.MoveAnchor, param)

    # Moves Cursor to the start of the line
    def MoveCarriageToTheStartOfTheLine(self):
        self.Cursor.movePosition(
            self.MoveOp.StartOfLine, self.MoveMode.MoveAnchor)

    # Move Cursor to new Line
    def MoveCarriageToTheNewLine(self):
        self.Cursor.movePosition(
            self.MoveOp.EndOfLine, self.MoveMode.MoveAnchor)
        self.Cursor.insertText('\n')

    # Moves Cursor Based on column number
    def MoveCursorToColumn(self):
        if self.params == []:
            param1, param2 = 1, 1
        else:
            param1, param2 = max(self.params[0], 1), max(self.param[1], 1)
        self.params = []
        self.Cursor.movePosition(
            self.MoveOp.StartOfLine, self.MoveMode.MoveAnchor)
        self.Cursor.movePosition(
            self.MoveOp.Right, self.MoveMode.MoveAnchor, param2)

    # Erases part or whole screen
    def EraseInDisplay(self):
        if self.params == []:
            param = 1
        else:
            param = self.params[0]
        self.params = []
        if param == 0:
            self.Cursor.movePosition(
                self.MoveOp.End, self.MoveMode.KeepAnchor)
        if param == 1:
            self.Cursor.movePosition(
                self.MoveOp.Start, self.MoveMode.KeepAnchor)
        if param == 2:
            self.Cursor.movePosition(
                self.MoveOp.Start, self.MoveMode.MoveAnchor)
            self.Cursor.movePosition(
                self.MoveOp.End, self.MoveMode.KeepAnchor)
        self.Cursor.removeSelectedText()

    # Erase part or whole line
    def EraseInLine(self):
        if self.params == []:
            param = 1
        else:
            param = max(self.params[0], 1)
        self.params = []
        if param == 0:
            self.Cursor.movePosition(
                self.MoveOp.EndOfLine, self.MoveMode.KeepAnchor)
        if param == 1:
            self.Cursor.movePosition(
                self.MoveOp.StartOfLine, self.MoveMode.KeepAnchor)
        if param == 2:
            self.Cursor.movePosition(
                self.MoveOp.StartOfLine, self.MoveMode.MoveAnchor)
            self.Cursor.movePosition(
                self.MoveOp.EndOfLine, self.MoveMode.KeepAnchor)
        self.Cursor.removeSelectedText()

    # Change state to Normal state
    def ChangeStateToNormal(self):
        self.state = self.NORMAL

    # Change state to Escape Sequence state
    def ChangeStateToEscSeq(self):
        self.state = self.ESCAPE_SEQ

    # Changes State to control sequence introduser state
    def ChangeStateToCSI(self):
        self.state = self.CSI
    
    # Resets parser state to prevent any unusual behavior
    def resetParser(self):
        self.state = self.NORMAL
        self.params = []
        self.TemporaryStorage = 0

    def UpdateUI(self):
        while self.buffer.__len__() != 0:
            char = self.buffer.pop(0)
            assert isinstance(char, str), "Char is not a string"

            if char in self._c0Handlers.keys():
                self._c0Handlers[char]()
                continue

            if self.state is self.NORMAL:
                self.Cursor.insertText(char)

            if self.state is self.ESCAPE_SEQ:
                try:
                    self._FeHandlers[char]()
                except:
                    print('Unhandled escape sequence')

            if self.state is self.CSI:
                paramChars = [chr(i) for i in range(0x30, 0x3F)] + [' ']
                while char in paramChars:
                    if char.isnumeric():
                        self.TemporaryStorage *= 10
                        self.TemporaryStorage += int(char)
                    elif char == ';':
                        self.params.append(self.TemporaryStorage)
                        self.TemporaryStorage = 0

                    if self.buffer.__len__() != 0:
                        char = self.buffer.pop(0)
                    else:
                        return
                else:
                    self.params.append(self.TemporaryStorage)
                    self.TemporaryStorage = 0

                if char in self._CsiHandlers:
                    self._CsiHandlers[char]()
                else:
                    self.resetParser() 
                self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())               

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.UI_Update.stop()
        return super().closeEvent(a0)


if __name__ == '__main__':
    print('Debug Mode')
    term = Terminal()
    term.AddTextToBuffer("asdasdasdas")
    print(term.buffer)
