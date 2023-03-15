from LibraryImport import *
# from TerminalWidget import QTerminal

class ConsoleWidget(QWidget):
    def __init__(self, ComboBoxSelection, host, username=None, password=None):
        super(ConsoleWidget, self).__init__()
        self.mainLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.host = host
        self.initUI(ComboBoxSelection, host, username, password)

    def initUI(self, ComboBoxSeleciton, host, usr, psw):
        self.Layout = QVBoxLayout()
        self.mainLayout.addLayout(self.Layout)
        self.mainWidget = Terminal('fish', [])
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