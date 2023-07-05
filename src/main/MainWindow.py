from LibraryImport import *
from ConsoleWidget import ConsoleWidget
from ConnectionWidget import Connection_Window
from TemplateWidget import TemplateWidget
from qterminal.mux import mux
from TopBar import TopBar
from shared.GetFile import getDictFromPickleFile, dumpDictToPickleFile, getEntryInDict, appendToPickleFile
import base64

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
        self.connectionBar = TopBar()
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
        self.openTemplate = self.menu.addMenu("Templates")
        self.initTemplateMenu()
        # self.openTemplate.triggered.connect(self.ReadFile)
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

    def initTemplateMenu(self, templates_incom = None, menu = None):
        self.actions_ = []
        if templates_incom == None:
            menu = self.openTemplate
            self.templates = templates = getDictFromPickleFile("templates.data")
        else:
            templates = templates_incom
        for entry in templates:
            if isinstance(templates[entry], dict):
                print(entry, "is dict")
                menu_embedded = menu.addMenu(entry)
                self.initTemplateMenu(templates[entry], menu_embedded)
            else: 
                action = menu.addAction(entry)
                func = self.initTemplateEditor(templates[entry])
                action.triggered.connect(func)
                self.actions_.append(action)
                print(f"added function {entry} with {templates[entry]}")

        if templates_incom == None:
            action = menu.addAction("Export")
            action.triggered.connect(self.importTest)
            share = menu.addAction("Share")
            share.triggered.connect(self.shareTemplateTest)
        
    def initTemplateEditor(self, prompt):
        def initTemplateEditorInner():
            self.templatewid = TemplateWidget(prompt, self.TabWidget.tabText(self.TabWidget.currentIndex()))
            self.templatewid.show()
        return initTemplateEditorInner
        
    def shareTemplateTest(self):
        #TODO migrate this code (actual implementation) to shared and implement clipboards usage
        sample_string = "conf t\nshow ip int br\nexit\n\rasddddddasssssssssssss"*100
        sample_string_bytes = sample_string.encode("ascii")
  
        base64_bytes = base64.b64encode(sample_string_bytes)
        base64_string = base64_bytes.decode("ascii")

        sample_string_bytes = base64.b64decode(base64_bytes)
        sample_string1 = sample_string_bytes.decode("ascii")
        print(base64_string)
        print(sample_string1)

    def importTest(self):
        appendToPickleFile({"Test1": {"Test_embed": "<h1>YAY</h1> {{test}}", "ASDWQEQWEQWD": "Success"}}, 'templates.data')
        self.openTemplate.clear()
        self.initTemplateMenu()

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
