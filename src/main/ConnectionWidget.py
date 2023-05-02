from LibraryImport import *


class Connection_Window(QWidget):
    connected = pyqtSignal(str)

    def __init__(self):
        super(Connection_Window, self).__init__()
        self.connection = None
        self.initUI()
    def initUI(self):
        self.setFixedSize(400, 200)
        self.Grid = QGridLayout()
        self.setLayout(self.Grid)
        self.inputL = QLineEdit()
        self.sendButton = QPushButton()
        self.sendButton.setText("Connect")
        self.inputL.setFixedSize(300, 30)
        self.Grid.addWidget(self.inputL, 2, 1)
        self.Grid.addWidget(self.sendButton, 3, 3)
        self.sendButton.clicked.connect(self.Sending)

    def Sending(self):
        self.connection = self.inputL.text()
        self.connected.emit(self.connection)
        self.close()
