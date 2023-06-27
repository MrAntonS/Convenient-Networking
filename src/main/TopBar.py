from LibraryImport import *

class TopBar(QWidget):
    def __init__(self):
        super(TopBar, self).__init__()
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