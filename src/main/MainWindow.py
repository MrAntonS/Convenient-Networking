from LibraryImport import *
from ConsoleWidget import ConsoleWidget
from ConnectionWidget import Connection_Window
from TemplateWidget import TemplateWidget
from qterminal.mux import mux


class ConnectionBar(QWidget):
    def __init__(self):
        super(ConnectionBar, self).__init__()
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
        self.protocolComboBox = QComboBox()
        self.protocolComboBox.addItem("Telnet")
        self.protocolComboBox.addItem("SSH")
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
        self.connectIns.addWidget(self.protocolComboBox)
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
        self.protocolComboBox.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.connectbtn.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setLayout(self.connectLayout)


class MainWindow(QMainWindow):
    AddTab = pyqtSignal(str)

    def __init__(self):
        # Call the inherited classes __init__ method
        super(MainWindow, self).__init__()
        self.initUi()
        self.socket = socket.socket()
        self.socket.bind(("127.0.0.1", 5100))
        self.socket.listen(1)
        self.ProtectionTimer = 600
        self.socket.setblocking(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.installEventFilter(self)
        self.TabThread = threading.Thread(target=self.CheckForNewTabs)
        self.TabThread.daemon = True
        self.AddTab.connect(self.AddNewTab)
        self.Tab = QShortcut(QKeySequence("Ctrl+Tab"), self)
        self.Tab.activated.connect(lambda: self.TabWidget.setCurrentIndex((self.TabWidget.currentIndex() + 1) % self.TabWidget.count()))
        self.TabBack = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        self.TabBack.activated.connect(lambda: self.TabWidget.setCurrentIndex((self.TabWidget.currentIndex() - 1) % self.TabWidget.count()))
        self.TabThread.start()

    def initUi(self):
        self.cntWidget = QWidget()
        self.VboxLayout = QVBoxLayout()
        self.connectionBar = ConnectionBar()
        self.VboxLayout.addWidget(self.connectionBar)
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
        self.connectionBar.connectbtn.clicked.connect(self.AddNewTab)
        self.stopScrollingBtn.triggered.connect(self.stopScrolling)
        self.Colors = QPalette()
        self.setPalette(self.Colors)
        self.TabWidget.setPalette(self.Colors)
        self.TabWidget.setTabsClosable(True)
        self.PATH = sys.path[-1]
        self.setWindowIcon(QIcon(f"{self.PATH}/img/convNet.ico"))
        self.TabWidget.tabCloseRequested.connect(self.CloseTab)
        self.show()
        self.startTimer(100)

    def timerEvent(self, a0: QTimerEvent) -> None:
        currWidget = self.TabWidget.currentWidget()
        if currWidget != None:
            assert isinstance(currWidget, ConsoleWidget)
            if not currWidget.mainWidget.term.backend.connected:
                self.connectionBar.TimerLabel.setText("No Connection")
            else:
                if currWidget.mainWidget.term.protocol == 2:
                    self.connectionBar.TimerLabel.setText(
                        "Protection not needed")
                    return
                lastTimePressed = currWidget.mainWidget.term.lastTimeKeyWasPressed
                if self.ProtectionTimer - (time.perf_counter() - lastTimePressed) < 0:
                    if currWidget.mainWidget.term.backend.isProtectionActive:
                        currWidget.mainWidget.term.backend.isProtectionActive = False
                    self.connectionBar.TimerLabel.setText("No protection")
                else:
                    if not currWidget.mainWidget.term.backend.isProtectionActive:
                        currWidget.mainWidget.term.backend.isProtectionActive = True
                    self.connectionBar.TimerLabel.setText(
                        f"Protection will be active for {round((self.ProtectionTimer - (time.perf_counter() - lastTimePressed)) / 60, 1)}")

        return super().timerEvent(a0)

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
        consoleWid = self.TabWidget.currentWidget()
        assert isinstance(consoleWid, ConsoleWidget)
        consoleWid.write(self.content)
        pass

    def CloseTab(self, ind):
        self.TabWidget.widget(ind).close()
        self.TabWidget.removeTab(ind)

    def stopScrolling(self):
        for i in range(self.TabWidget.count()):
            self.TabWidget.widget(
                i).mainWidget.term.track_cursor = not self.TabWidget.widget(i).mainWidget.term.track_cursor

    def checkForTabScrollBtn(self):
        for child in self.TabWidget.findChildren(QToolButton):
            child.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def CheckForNewTabs(self):
        while True:
            try:
                conn, addr = self.socket.accept()
                output = conn.recv(1024)
                if output == b'':
                    continue
                self.AddTab.emit(output.decode('ascii'))
            except Exception as e:
                pass

    def AddNewTab(self, host=None):

        if isinstance(host, bool):
            if self.connectionBar.port.text() != '':
                host = self.connectionBar.host.text() + ':' + self.connectionBar.port.text()
            else:
                host = self.connectionBar.host.text()
        consoleWidget = ConsoleWidget(
            self.connectionBar.protocolComboBox.currentText(), host)
        index = self.TabWidget.addTab(consoleWidget, str(host))
        self.checkForTabScrollBtn()

    def closeEvent(self, a0: QCloseEvent) -> None:
        mux.stop()
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
        s.settimeout(0.1)
        s.connect((host, port))
        if len(args) > 1:
            x = ' '.join(args[1:])
            s.send(bytes(x, 'ascii'))
            mux.stop()
        else:
            sys.exit(-1)
    except Exception as e:
        s.close()
        app = QApplication(sys.argv)
        main = MainWindow()
        if len(args) > 1:
            main.AddNewTab(' '.join(args[1:]))
        else:
            pass
        sys.exit(app.exec())
