from LibraryImport import *
from ConsoleWidget import ConsoleWidget
from ConnectionWidget import Connection_Window
from TemplateWidget import TemplateWidget


class MainWindow(QMainWindow):
    def __init__(self):
        # Call the inherited classes __init__ method
        super(MainWindow, self).__init__()
        self.initUi()
        self.socket = socket.socket()
        self.socket.bind(("", 5100))
        self.socket.setblocking(False)
        self.socket.listen(1)
        self.timer = QTimer()
        self.timer.timeout.connect(self.CheckForNewTabs)
        self.timer.start()
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.installEventFilter(self)

    def initUi(self):
        self.cntWidget = QWidget()
        self.VboxLayout = QVBoxLayout()
        self.connectLayout = QHBoxLayout()
        self.connectIns = QHBoxLayout()
        self.hostlbl = QLabel()
        self.hostlbl.setText("Host:")
        self.hostlbl.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        self.portlbl = QLabel()
        self.portlbl.setText("Port:")
        self.portlbl.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        self.host = QLineEdit()
        self.host.setFixedWidth(200)
        self.host.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        self.connectbtn = QPushButton()
        self.connectbtn.setText("Connect")
        self.connectbtn.setFixedWidth(70)
        self.connectbtn.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        self.port = QLineEdit()
        self.port.setFixedWidth(100)
        self.port.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        self.TimerLabel = QLabel()
        self.TimerLabel.setText('No connection')
        self.connectIns.addWidget(self.hostlbl)
        self.connectIns.addWidget(self.host)
        self.connectIns.addWidget(self.portlbl)
        self.connectIns.addWidget(self.port)
        self.connectIns.addWidget(self.connectbtn)
        self.copyright = QLabel()
        self.copyright.setText("Made by Anton Saenko")
        self.connectIns.addWidget(self.copyright)
        self.connectLayout.addLayout(self.connectIns)
        self.connectLayout.addSpacerItem(QSpacerItem(
            600, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.connectLayout.addWidget(self.TimerLabel)
        self.host.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.port.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.connectbtn.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.VboxLayout.addLayout(self.connectLayout)
        self.setWindowTitle("ConvNet")
        self.setGeometry(1000, 300, 1000, 700)
        self.setCentralWidget(self.cntWidget)
        self.cntWidget.setLayout(self.VboxLayout)
        self.VboxLayout.setContentsMargins(3, 7, 3, 3)
        self.TabWidget = QTabWidget()
        self.TabWidget.setContentsMargins(0, 0, 0, 0)
        self.TabWidget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.TabWidget.setAutoFillBackground(True)
        self.VboxLayout.addWidget(self.TabWidget)
        self.menu = self.menuBar()
        self.stopScrollingBtn = self.menu.addAction(
            "Stop scrolling to the bottom")
        self.openTemplate = self.menu.addAction("Open Template File")
        self.openTemplate.triggered.connect(self.ReadFile)
        self.connectbtn.clicked.connect(self.AddNewTab)
        self.stopScrollingBtn.triggered.connect(self.stopScrolling)
        self.Colors = QPalette()
        self.setPalette(self.Colors)
        self.TabWidget.setPalette(self.Colors)
        self.PATH = '/'.join(sys.executable.split('\\')[:-1])
        self.setWindowIcon(QIcon(f"{self.PATH}/img/clown-face.png"))
        self.TabWidget.setTabsClosable(True)
        self.TabWidget.tabCloseRequested.connect(self.CloseTab)
        self.show()

    def ReadFile(self):
        fname = QFileDialog.getOpenFileName(
            self, "Open File", self.PATH + "/Templates", "Text Files (*.txt)")
        if fname[0] == '':
            return
        with open(fname[0], 'r') as f:
            self.content = f.readlines()
        self.OpenVariableWidget(self.content)

    def OpenVariableWidget(self, content):
        try:
            curHost = self.TabWidget.currentWidget().host
            print(curHost)
            self.temp_widget = TemplateWidget(content, curHost)
            self.temp_widget.submit.clicked.connect(self.Done)
            self.temp_widget.show()
        except:
            curHost = "No Connection"
            self.temp_widget = TemplateWidget(content, curHost)
            self.temp_widget.submit.clicked.connect(self.temp_widget.close)
            self.temp_widget.show()
        pass

    def Done(self):
        values = self.temp_widget.vars
        for i in values.keys():
            self.content = ''.join(self.content).replace(i, values[i].text())
        self.temp_widget.close()
        del self.temp_widget
        # print(repr(self.content))
        # print(self.content)
        self.TabWidget.currentWidget().tn.write(bytes(self.content, 'ascii'))
        pass

    def CloseTab(self, ind):
        self.TabWidget.widget(ind).close()
        self.TabWidget.removeTab(ind)

    def stopScrolling(self):
        for i in range(self.TabWidget.count()):
            self.TabWidget.widget(
                i).track_cursor = not self.TabWidget.widget(i).track_cursor

    def checkForTabScrollBtn(self):
        for child in self.TabWidget.findChildren(QToolButton):
            child.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def CheckForNewTabs(self):
        try:
            c, addr = self.socket.accept()
            x = c.recv(1024)
            self.AddNewTab(x.decode('ascii'))
        except BlockingIOError as e:
            pass

    def AddNewTab(self, host=None):
        if isinstance(host, bool):
            if self.port.text() != '':
                host = self.host.text() + ':' + self.port.text()
            else:
                host = self.host.text()
        consoleWidget = ConsoleWidget(host)
        consoleWidget.updateTime.connect(self.UpdateTimerLabel)
        index = self.TabWidget.addTab(consoleWidget, str(host))
        consoleWidget.track_cursor = self.TabWidget.currentWidget().track_cursor
        self.checkForTabScrollBtn()

    def UpdateTimerLabel(self, timer):
        if timer == 0:
            self.TimerLabel.setText('No protection')
        elif timer == -1 or timer == -2:
            if self.TabWidget.count() == 1:
                self.TimerLabel.setText("No connection")
        else:
            self.TimerLabel.setText(
                f"Protection will be active for {timer} minutes")

    def closeEvent(self, a0: QCloseEvent) -> None:
        while self.TabWidget.count() > 0:
            self.TabWidget.widget(0).close()
            self.TabWidget.removeTab(0)
        return super().closeEvent(a0)


if __name__ == '__main__':
    args = sys.argv
    try:
        s = socket.socket()  # create a socket object
        host = '127.0.0.1'  # Host i.p
        port = 5100  # Reserve a port for my app
        s.settimeout(1)
        s.connect((host, port))
        if len(args) > 1:
            x = ' '.join(args[1:])
            s.send(bytes(x, 'ascii'))
        else:
            raise BaseException
    except Exception as e:
        print(e, "!!!")
        app = QApplication(sys.argv)
        main = MainWindow()
        if len(args) > 1:
            main.AddNewTab(' '.join(args[1:]))
        else:
            pass
        sys.exit(app.exec())
