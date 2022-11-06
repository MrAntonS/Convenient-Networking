from LibraryImport import *
logging.basicConfig(level=logging.DEBUG)

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

    # Stores buffer until next UI update cycle
    def AddTextToBuffer(self, buffer):
        logging.debug(f'AddTextToBuffer method has been called')
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
        logging.debug(f'MoveCarriageToTheLeft method has been called')
        if self.params == []:
            param = 1
        else:
            param = max(self.params.pop(0), 1)
        self.params = []
        self.Cursor.movePosition(
            self.MoveOp.Left, self.MoveMode.MoveAnchor, param)

    # Moves Cursor to the right
    def MoveCarriageToTheRight(self):
        logging.debug(f'MoveCarriageToTheRight method has been called')
        if self.params == []:
            param = 1
        else:
            param = max(self.params.pop(0), 1)
        self.params = []
        self.Cursor.movePosition(
            self.MoveOp.Right, self.MoveMode.MoveAnchor, param)

    # Move Cursor to previous line
    def MoveCarriageToPreviousLine(self):
        logging.debug(f'MoveCarriageToPreviousLine method has been called')
        if self.params == []:
            param = 1
        else:
            param = max(self.params.pop(0), 1)
        self.params = []
        self.Cursor.movePosition(
            self.MoveOp.Up, self.MoveMode.MoveAnchor, param)

    # Moves Cursor to the start of the line
    def MoveCarriageToTheStartOfTheLine(self):
        logging.debug(f'MoveCarriageToTheStartOfTheLine method has been called')
        self.Cursor.movePosition(
            self.MoveOp.StartOfLine, self.MoveMode.MoveAnchor)

    # Move Cursor to new Line
    def MoveCarriageToTheNewLine(self):
        logging.debug(f'MoveCarrigeToTheNewLine method has been called')
        self.Cursor.movePosition(
            self.MoveOp.EndOfLine, self.MoveMode.MoveAnchor)
        self.Cursor.insertText('\n')

    # Moves Cursor Based on column number
    def MoveCursorToColumn(self):
        logging.debug(f'Move cursor to Column method has beed called')
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
        logging.debug(f'Erase in Display method has been called')
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
        logging.debug(f'Erase in line method has been called')
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
        logging.debug(f'Line Has been Erased')

    # Change state to Normal state
    def ChangeStateToNormal(self):
        logging.debug(f'State has been changed to Normal')
        self.state = self.NORMAL

    # Change state to Escape Sequence state
    def ChangeStateToEscSeq(self):
        logging.debug(f'State has been changed to ESC sequence')
        self.state = self.ESCAPE_SEQ

    # Changes State to control sequence introduser state
    def ChangeStateToCSI(self):
        logging.debug(f'State has been changed to CSI')
        self.state = self.CSI
    
    # Resets parser state to prevent any unusual behavior
    def resetParser(self):
        logging.debug(f'Parser has been resetted')
        self.state = self.NORMAL
        self.params = []
        self.TemporaryStorage = 0

    def UpdateUI(self):
        while self.buffer.__len__() != 0:
            char = self.buffer.pop(0)
            assert isinstance(char, str), "Char is not a string"

            if char in self._c0Handlers.keys():
                logging.debug(f'Character {char} has been identified as c0, calling a handler')
                self._c0Handlers[char]()
                continue

            if self.state is self.NORMAL:
                logging.debug(f'Character {char} has been identified as normal, outputting')
                self.Cursor.insertText(char)

            elif self.state is self.ESCAPE_SEQ:
                logging.debug(f'Character {char} has been identified as Esc sequence, calling handler')
                try:
                    self._FeHandlers[char]()
                except:
                    logging.debug(f'Sequence is unhandled')

            elif self.state is self.CSI:
                logging.debug(f'State has been identified as CSI, calling handler')
                paramChars = [chr(i) for i in range(0x30, 0x3F)] + [' ']
                while char in paramChars:
                    if char.isnumeric():
                        logging.debug(f'Character {char} has been identified as parameter, saving to param variable')
                        self.TemporaryStorage *= 10
                        self.TemporaryStorage += int(char)
                    elif char == ';':
                        logging.debug(f'Character {char} has been identified as end of parameter, saving to parameters list')
                        self.params.append(self.TemporaryStorage)
                        self.TemporaryStorage = 0

                    if self.buffer.__len__() != 0:
                        logging.debug(f'Taking next character')
                        char = self.buffer.pop(0)
                    else:
                        logging.debug(f'No more characters in the buffer but CSI Did not end, waiting for next buffer chunk')
                        return
                else:
                    logging.debug(f'Saving params for future use')
                    self.params.append(self.TemporaryStorage)
                    self.TemporaryStorage = 0

                if char in self._CsiHandlers:
                    logging.debug(f'Character {char} has been identified as CSI command, calling handler')
                    self._CsiHandlers[char]()
                self.resetParser()               

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.UI_Update.stop()
        return super().closeEvent(a0)


if __name__ == '__main__':
    print('Debug Mode')
    term = Terminal()
    term.AddTextToBuffer("asdasdasdas")
    print(term.buffer)
