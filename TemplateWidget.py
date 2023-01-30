from LibraryImport import *


class TemplateWidget(QWidget):
    def __init__(self, content, host):
        super(TemplateWidget, self).__init__()
        self.vars = dict()
        self.hostname = host
        self.initUI(content)
        pass

    def initUI(self, content):
        self.Vbox = QVBoxLayout()
        self.setLayout(self.Vbox)
        self.setWindowTitle(self.hostname)
        p = re.compile(r'({{[^}]+}})')
        all_vars = re.findall(p, ''.join(content))
        for i in all_vars:
            if i in self.vars.keys():
                continue
            i1 = i[2:-2]
            # print(i1, "i1 before")
            # print(i, 'i')
            i1 = i1.split('|')
            if len(i1) == 1:
                i1 = i1[0]
                suggested = ''
            else:
                suggested = i1[1]
                i1 = i1[0]
            # print(i1, 'i1 after')
            if i1 in self.vars.keys():
                continue
            # checking
            layout = QHBoxLayout()
            layout.addSpacerItem(QSpacerItem(40, 0))
            label = QLabel(text=i1 + ":")
            line_edit = QLineEdit()
            line_edit.setText(suggested)
            layout.addWidget(label)
            layout.addWidget(line_edit)
            layout.addSpacerItem(QSpacerItem(40, 0))
            self.vars[i] = line_edit
            self.vars["{{" + i1 + "}}"] = line_edit
            self.Vbox.addLayout(layout)
        layout = QHBoxLayout()
        layout.addSpacerItem(QSpacerItem(40, 0))
        self.submit = QPushButton(text="Submit")
        layout.addWidget(self.submit)
        layout.addSpacerItem(QSpacerItem(40, 0))
        self.Vbox.addLayout(layout)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key.Key_Return:
            self.submit.click()
        return super().keyPressEvent(a0)
