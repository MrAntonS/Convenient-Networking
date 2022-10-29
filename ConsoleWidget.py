from LibraryImport import *


class ConsoleWidget(QWidget):
    updateTime = pyqtSignal(float)

    class TextEdit(QTextEdit):
        def __init__(self):
            super(ConsoleWidget.TextEdit, self).__init__()
            self.Cursor = self.textCursor()
            self.setTextCursor(self.Cursor)
            self.CursorColor = QColorConstants.White

        def paintEvent(self, a0: QPaintEvent) -> None:
            p = QPainter(self.viewport())
            p.fillRect(self.cursorRect(self.Cursor),
                       self.CursorColor)
            return super().paintEvent(a0)

    class Worker(QObject):
        strSignal = pyqtSignal(str)
        lostConnection = pyqtSignal(bool)
        finished = pyqtSignal()
        timeUpdate = pyqtSignal(float)
        checkVisibility = pyqtSignal()
        StopBreakingSig = pyqtSignal()

        def __init__(self, tn) -> None:
            self.tn = tn
            self.running = True
            self.AFKTIMER = time.perf_counter()
            self.checkTimer = QTimer()
            self.checkTimer.setInterval(50)
            self.checkTimer.timeout.connect(self.send_time)
            self.checkTimer.start()
            self.UpdateTimer = QTimer()
            self.UpdateTimer.timeout.connect(self.UpdateCycle)
            self.visible = True
            self.breaking = False
            self.Protection = 600
            self.NotSeen = ''
            super(ConsoleWidget.Worker, self).__init__()

        def send_time(self):
            self.timeUpdate.emit(
                round(max(0, (self.Protection - (time.perf_counter() - self.AFKTIMER)) / 60), 1))

        def UpdateCycle(self):
            self.checkVisibility.emit()
            try:
                reading = self.tn.read_eager()
                try:
                    decod = reading.decode("utf-8")
                except Exception:
                    decod = ""
                if self.NotSeen + decod != '':
                    # print(repr(self.NotSeen + decod))
                    if self.visible:
                        self.NotSeen = self.NotSeen + decod
                        if len(self.NotSeen) > 30:
                            self.strSignal.emit(self.NotSeen[:30])
                            self.NotSeen = self.NotSeen[30:]
                        else:
                            self.strSignal.emit(self.NotSeen)
                            self.NotSeen = ''
                    else:
                        self.NotSeen += decod
                        if self.breaking:
                            if re.search('rom.*>', decod) != None or re.search("load.*>", decod) or re.search("swit.*:", decod):
                                print("Found one")
                                self.StopBreakingSig.emit()

            except Exception as e:
                if time.perf_counter() - self.AFKTIMER > self.Protection:
                    self.UpdateTimer.stop()
                    self.finished.emit()
                    self.lostConnection.emit(True)
                    return
                print(e, "@")
                self.checkTimer.stop()
                self.UpdateTimer.stop()
                self.finished.emit()
                self.lostConnection.emit(False)
                return

        def Stop(self):
            try:
                self.tn.close()
            except Exception:
                pass
            print("DONE")
            self.UpdateTimer.stop()
            self.checkTimer.stop()
            self.finished.emit()

    def __init__(self, host):
        super(ConsoleWidget, self).__init__()
        self.mainLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.host = host
        self.flag_for_escape_seq = False
        self.num_for_escape_seq = None
        self.track_cursor = True
        self.Connected = False
        self.string = ''
        self.connect(self.host)
        self.BreakTimer = QTimer()
        self.BreakTimer.setInterval(500)
        self.BreakTimer.timeout.connect(self.Break)
        self.reloadToRommon = QShortcut(QKeySequence('Ctrl+Shift+R'), self)
        self.copy = QShortcut(QKeySequence('Ctrl+Shift+C'), self)
        self.copyAndBreak = QShortcut(QKeySequence('Ctrl+C'), self)
        self.paste = QShortcut(QKeySequence('Ctrl+V'), self)
        self.paste.activated.connect(self.Paste)
        self.copy.activated.connect(self.Copy)
        self.copyAndBreak.activated.connect(self.CopyAndBreak)
        self.reloadToRommon.activated.connect(self.BreakToRommon)

    def BreakToRommon(self):
        self.mainWidget.CursorColor = QColorConstants.White if self.mainWidget.CursorColor != QColorConstants.White else QColorConstants.Red
        self.worker.breaking = not self.worker.breaking
        if self.worker.breaking:
            self.BreakTimer.start()
        else:
            self.BreakTimer.stop()

    def Break(self):
        self.tn.write(b'\x03')
        self.tn.write(b'\x03')
        self.tn.write(b'\x0C')
        self.tn.write(b'\x0C')
        self.tn.write(b'\x18')
        self.tn.write(telnetlib.IAC)
        self.tn.write(telnetlib.BRK)

    def connect(self, host):
        try:
            host = host.replace("telnet://", '')
            host = host.split(':')
            self.tn = Telnet_(host[0], host[1], timeout=1)
            self.initUI()
        except Exception as e:
            print(e)
            self.tn = False
        if self.tn == False:
            self.initFailedUI()
            return
        self.worker = self.Worker(self.tn)
        self.th = QThread()
        self.worker.moveToThread(self.th)
        self.worker.finished.connect(self.KillProcess)
        self.worker.strSignal.connect(self.UpdateUI)
        self.worker.lostConnection.connect(self.LostConnection)
        self.worker.timeUpdate.connect(self.UpdateLabel)
        self.worker.checkVisibility.connect(self.CheckVisibility)
        self.worker.StopBreakingSig.connect(self.BreakToRommon)
        self.th.finished.connect(self.th.deleteLater)
        self.th.started.connect(self.worker.UpdateTimer.start)
        self.th.start()

    def CheckVisibility(self):
        if self.isVisible():
            self.worker.visible = True
        else:
            self.worker.visible = False

    # Checks if widget is visible and update a label of main widget that say how much more time connection is protected
    def UpdateLabel(self, timer):
        if self.isVisible():
            self.updateTime.emit(timer)

    def KillProcess(self):
        self.th.quit()
        self.th.deleteLater()
        del self.th

    def initUI(self):
        if not self.Connected:
            self.Layout = QVBoxLayout()
            self.mainLayout.addLayout(self.Layout)
            self.mainWidget = self.TextEdit()
            self.mainWidget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.mainWidget.setReadOnly(True)
            self.Colors = QPalette()
            self.Layout.setContentsMargins(4, 4, 4, 4)
            self.Colors.setColor(
                QPalette().ColorRole["Text"], QColorConstants.DarkGreen)
            self.Colors.setColor(
                QPalette().ColorRole["Base"], QColor(40, 40, 40))
            self.Colors.setColor(
                QPalette().ColorRole["Window"], QColorConstants.Black)
            self.setPalette(self.Colors)
            self.Layout.addWidget(self.mainWidget)
            self.mainWidget.setFontPointSize(15)
            self.mainWidget.setContextMenuPolicy(
                Qt.ContextMenuPolicy.NoContextMenu)
            self.mainWidget.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse)
            self.Connected = True
        if self.Connected:
            self.mainWidget.show()
            self.mainLayout.addLayout(self.Layout)
        pass

    def Copy(self):
        self.mainWidget.copy()

    def CopyAndBreak(self):
        # print("AAA")
        self.mainWidget.copy()
        self.tn.write(b'\x03')

    def Paste(self):
        self.tn.write(bytes(QApplication.clipboard().text(), 'utf-8'))

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        try:
            self.worker.AFKTIMER = time.perf_counter()
        except Exception:
            pass
        try:
            if a0.key() == 16777235:
                self.tn.write(bytes(b"\x1B\x5B\x41"))
            elif a0.key() == 16777237:
                self.tn.write(bytes(b"\x1B\x5B\x42"))
            elif a0.key() == 16777234:
                self.tn.write(bytes(b"\x1B\x5B\x44"))
            elif a0.key() == 16777236:
                self.tn.write(bytes(b"\x1B\x5B\x43"))
            else:
                self.tn.write(bytes(a0.text(), 'utf-8'))
        except Exception as e:
            print(e)
        return super().keyPressEvent(a0)

    def closeEvent(self, a0: QCloseEvent) -> None:
        try:
            self.tn.close()
        except Exception:
            pass
        try:
            self.noConnectionEmitter.stop()
            del self.noConnectionEmitter
        except Exception as e:
            print(e)
            pass
        try:
            self.worker.UpdateTimer.stop()
        except Exception:
            pass
        try:
            self.updateTime.emit(-1)
        except Exception:
            pass
        try:
            self.th.quit()
        except Exception as e:
            print(e)
        try:
            self.worker.checkTimer.stop()
        except Exception as e:
            print(e)
            pass
        try:
            self.BreakTimer.stop()
        except Exception as e:
            pass
        return super().closeEvent(a0)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.MouseButton.RightButton and self.mainWidget.textCursor().hasSelection():
            self.tn.write(
                bytes(self.mainWidget.textCursor().selection().toPlainText(), 'ascii'))
        return super().mousePressEvent(a0)

    def LostConnection(self, afk):
        try:
            if not afk:
                host = self.host.replace("telnet://", '')
                host = host.split(':')
                self.tn = Telnet_(host[0], host[1], timeout=1)
                timer = self.worker.AFKTIMER
                time.sleep(0.05)
                while self.tn.read_eager() != b'':
                    continue
                self.worker = self.Worker(self.tn)
                self.worker.AFKTIMER = timer
                self.th = QThread()
                self.worker.moveToThread(self.th)
                self.worker.timeUpdate.connect(self.UpdateLabel)
                self.worker.finished.connect(self.th.quit)
                self.worker.strSignal.connect(self.UpdateUI)
                self.worker.lostConnection.connect(self.LostConnection)
                self.worker.checkVisibility.connect(self.CheckVisibility)
                self.worker.StopBreakingSig.connect(self.BreakToRommon)
                self.th.finished.connect(self.th.deleteLater)
                self.th.started.connect(self.worker.UpdateTimer.start)
                self.th.start()
            else:
                try:
                    self.BreakTimer.stop()
                except Exception:
                    pass
                self.worker.checkTimer.stop()
                self.UpdateLabel(-2)
                self.mainLayout.takeAt(0)
                self.mainWidget.close()
                self.initFailedUI()
                pass
        except Exception as e:
            print(e, "@@@@")
            self.worker.checkTimer.stop()
            self.UpdateLabel(-2)
            try:
                self.BreakTimer.stop()
            except Exception:
                pass
            self.mainLayout.takeAt(0)
            self.mainWidget.close()
            self.initFailedUI()
            pass

    def initFailedUI(self):
        self.FailedLayout = QGridLayout()
        self.mainLayout.addLayout(self.FailedLayout)
        self.btn = QPushButton()
        self.btn.setText("Reconnect")
        self.btn.setFixedSize(QSize(100, 40))
        self.FailedLayout.addWidget(self.btn, 2, 2)
        self.btn.clicked.connect(self.Reconnect)
        self.noConnectionEmitter = QTimer()
        self.noConnectionEmitter.setInterval(50)
        self.noConnectionEmitter.timeout.connect(lambda: self.UpdateLabel(-2))
        self.noConnectionEmitter.start()
        pass

    def Reconnect(self):
        self.mainLayout.takeAt(0)
        self.btn.close()
        self.noConnectionEmitter.stop()
        del self.noConnectionEmitter
        del self.btn
        del self.FailedLayout
        self.connect(self.host)

    def UpdateUI(self, string):
        if self.worker.breaking:
            # print(re.match("load*>", decod), repr(decod))
            if re.search('rom.*>', string) != None or re.search("load.*>", string) or re.search("swit.*:", string):
                print("Found one")
                self.BreakToRommon()
        for char in string:
            # /r-to the beginning of the line
            # /n-to the bottom
            # string = string.replace('\n\r', '\n', 1)
            # string = string.replace('\r\r', '', 1)
            # string = string.replace('\r\n', '\n', 1)
            if char == '\x1b':
                self.flag_for_escape_seq = True
                self.num_for_escape_seq = 0
            elif not self.flag_for_escape_seq:
                if char == '\x08':
                    self.mainWidget.Cursor.movePosition(
                        QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor)
                    char = ''
                elif char == '\x07':
                    char = ''
                elif char == '\r':
                    self.mainWidget.Cursor.movePosition(
                        QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.MoveAnchor)
                elif char == '\n':
                    self.mainWidget.Cursor.movePosition(
                        QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.MoveAnchor)
                    self.mainWidget.Cursor.insertText(char)
                else:
                    self.mainWidget.Cursor.deleteChar()
                    self.mainWidget.Cursor.insertText(char)
            else:
                if char.isnumeric():
                    self.num_for_escape_seq = self.num_for_escape_seq * \
                        10 + int(char)
                elif char == 'D':
                    self.mainWidget.Cursor.movePosition(
                        QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, max(self.num_for_escape_seq, 1))
                    self.num_for_escape_seq = None
                    self.flag_for_escape_seq = False
                elif char == 'K':
                    if self.num_for_escape_seq == 0:
                        self.mainWidget.Cursor.movePosition(
                            QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
                    elif self.num_for_escape_seq == 1:
                        self.mainWidget.Cursor.movePosition(
                            QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.KeepAnchor)
                    elif self.num_for_escape_seq == 2:
                        self.mainWidget.Cursor.movePosition(
                            QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.MoveAnchor)
                        self.mainWidget.Cursor.movePosition(
                            QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
                    self.mainWidget.Cursor.removeSelectedText()
                    self.flag_for_escape_seq = False
                    self.num_for_escape_seq = None
                elif char == 'C':
                    self.mainWidget.Cursor.movePosition(
                        QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, max(self.num_for_escape_seq, 1))
                    self.num_for_escape_seq = None
                    self.flag_for_escape_seq = False
                elif char == ';':
                    self.num_for_escape_seq = 0
                    self.flag_for_escape_seq = True
                    pass
                elif char == "H":
                    self.num_for_escape_seq = max(1, self.num_for_escape_seq)
                    self.mainWidget.Cursor.movePosition(
                        QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.MoveAnchor)
                    self.mainWidget.Cursor.movePosition(
                        QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, self.num_for_escape_seq - 1)
                    self.num_for_escape_seq = None
                    self.flag_for_escape_seq = False
                    pass
                elif char == 'J':
                    if self.num_for_escape_seq == 0:
                        self.mainWidget.Cursor.movePosition(
                            self.mainWidget.Cursor.MoveOperation["End"], self.mainWidget.Cursor.MoveMode['KeepAnchor'])
                    self.mainWidget.Cursor.removeSelectedText()
                    self.num_for_escape_seq = None
                    self.flag_for_escape_seq = False
                elif char == "[":
                    pass
                else:
                    self.num_for_escape_seq = None
                    self.flag_for_escape_seq = False
            if self.track_cursor:
                self.mainWidget.setTextCursor(self.mainWidget.Cursor)
        pass
