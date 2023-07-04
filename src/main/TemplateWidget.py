from LibraryImport import *

class TemplateEditor(QTextEdit):
    def __init__(self, content):
        super(TemplateEditor, self).__init__()
        self.content = content

    def keyPressEvent(self, e: QKeyEvent) -> None:
        
        return super().keyPressEvent(e)

    def formatText(self, content):
        #TODO write a script to format text with syntax highlighting and auto replacement for variables
        pass
class TemplateWidget(QWidget):
    def __init__(self, content, host):
        super(TemplateWidget, self).__init__()
        self.vars = dict()
        self.hostname = host
        self.initUI(content)
        pass

    def initUI(self, content):
        self.mainLayout = QHBoxLayout()
        self.Vbox = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.setWindowTitle(self.hostname)
        self.templateEditor = TemplateEditor(content)
        self.templateEditor.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.templateEditor)
        self.mainLayout.addLayout(self.Vbox)
        p = re.compile(r'({{[^}]+}})')
        all_vars = re.findall(p, ''.join(content))
        for variable in all_vars:
            if variable in self.vars.keys():
                continue
            title = variable[2:-2]
            title = title.split('|')
            if len(title) == 1:
                title = title[0]
                suggested = ''
            else:
                suggested = title[1]
                title = title[0]
            if title in self.vars.keys():
                continue
            layout = QHBoxLayout()
            layout.addSpacerItem(QSpacerItem(40, 0))
            label = QLabel(text=title + ":")
            line_edit = QLineEdit()
            line_edit.setText(suggested)
            layout.addWidget(label)
            layout.addWidget(line_edit)
            layout.addSpacerItem(QSpacerItem(40, 0))
            self.vars[i] = line_edit
            self.vars["{{" + title + "}}"] = line_edit
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
