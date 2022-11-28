from LibraryImport import *
from TerminalWidget import QTerminal

class ConsoleWidget(QWidget):
    def __init__(self, ComboBoxSelection, host, username=None, password=None):
        super(ConsoleWidget, self).__init__()
        self.mainLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.host = host
        self.initUI(ComboBoxSelection, host, username, password)

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

    def initUI(self, ComboBoxSeleciton, host, usr, psw):
        self.Layout = QVBoxLayout()
        self.mainLayout.addLayout(self.Layout)
        self.mainWidget = QTerminal(ComboBoxSeleciton, host, usr, psw)
        # self.mainWidget.term.CheckCharSize()
        self.Colors = QPalette()
        self.Layout.setContentsMargins(4, 4, 4, 4)
        self.Layout.addWidget(self.mainWidget)

    def write(self, text):
        self.mainWidget.term.backend.write(text)

    def Paste(self):
        self.mainWidget.term.backend.write(bytes(QApplication.clipboard().text(), 'utf-8'))

    def closeEvent(self, a0: QCloseEvent) -> None:
        try:
            self.mainWidget.close()
        except:
            pass
        return super().closeEvent(a0)

    # def mousePressEvent(self, a0: QMouseEvent) -> None:
    #     if a0.button() == Qt.MouseButton.RightButton and self.mainWidget.textCursor().hasSelection():
    #         self.tn.write(
    #             bytes(self.mainWidget.textCursor().selection().toPlainText(), 'ascii'))
    #     return super().mousePressEvent(a0)

    # def LostConnection(self, afk):
    #     try:
    #         if not afk:
    #             host = self.host.replace("telnet://", '')
    #             host = host.split(':')
    #             self.tn = Telnet_(host[0], host[1], timeout=1)
    #             timer = self.worker.AFKTIMER
    #             time.sleep(0.05)
    #             while self.tn.read_eager() != b'':
    #                 continue
    #             self.worker = self.Worker(self.tn)
    #             self.worker.AFKTIMER = timer
    #             self.th = QThread()
    #             self.worker.moveToThread(self.th)
    #             self.worker.timeUpdate.connect(self.UpdateLabel)
    #             self.worker.finished.connect(self.th.quit)
    #             self.worker.strSignal.connect(self.UpdateUI)
    #             self.worker.lostConnection.connect(self.LostConnection)
    #             self.worker.checkVisibility.connect(self.CheckVisibility)
    #             self.worker.StopBreakingSig.connect(self.BreakToRommon)
    #             self.th.finished.connect(self.th.deleteLater)
    #             self.th.started.connect(self.worker.UpdateTimer.start)
    #             self.th.start()
    #         else:
    #             try:
    #                 self.BreakTimer.stop()
    #             except Exception:
    #                 pass
    #             self.worker.checkTimer.stop()
    #             self.UpdateLabel(-2)
    #             self.mainLayout.takeAt(0)
    #             self.mainWidget.close()
    #             self.initFailedUI()
    #             pass
    #     except Exception as e:
    #         print(e, "@@@@")
    #         self.worker.checkTimer.stop()
    #         self.UpdateLabel(-2)
    #         try:
    #             self.BreakTimer.stop()
    #         except Exception:
    #             pass
    #         self.mainLayout.takeAt(0)
    #         self.mainWidget.close()
    #         self.initFailedUI()
    #         pass

    # def initFailedUI(self):
    #     self.FailedLayout = QGridLayout()
    #     self.mainLayout.addLayout(self.FailedLayout)
    #     self.btn = QPushButton()
    #     self.btn.setText("Reconnect")
    #     self.btn.setFixedSize(QSize(100, 40))
    #     self.FailedLayout.addWidget(self.btn, 2, 2)
    #     self.btn.clicked.connect(self.Reconnect)
    #     self.noConnectionEmitter = QTimer()
    #     self.noConnectionEmitter.setInterval(50)
    #     self.noConnectionEmitter.timeout.connect(lambda: self.UpdateLabel(-2))
    #     self.noConnectionEmitter.start()
    #     pass

    # def Reconnect(self):
    #     self.mainLayout.takeAt(0)
    #     self.btn.close()
    #     self.noConnectionEmitter.stop()
    #     del self.noConnectionEmitter
    #     del self.btn
    #     del self.FailedLayout
    #     self.connect(self.host)

    # def UpdateUI(self, string):
    #     if self.worker.breaking:
    #         # print(re.match("load*>", decod), repr(decod))
    #         if re.search('rom.*>', string) != None or re.search("load.*>", string) or re.search("swit.*:", string):
    #             print("Found one")
    #             self.BreakToRommon()
    #     self.mainWidget.AddTextToBuffer(string)
    #     pass
