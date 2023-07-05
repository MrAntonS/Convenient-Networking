from LibraryImport import *

class TemplateEditor(QTextEdit):
    def __init__(self, content):
        super(TemplateEditor, self).__init__()
        self.content = content
        self.setHtml(content)
        self.formatText(content)

    def timerEvent(self, e: QTimerEvent) -> None:
        print(self.textCursor().position())
        print(self.toHtml())
        return super().timerEvent(e)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        return super().keyPressEvent(e)

    def formatText(self, content):
        #TODO write a script to format text with syntax highlighting and auto replacement for variables
        result_string = ""
        self.variables = variableWidget.getAllVariables(content)
        for variable in self.variables:
            string = r'({{' + variable + r'[^}]*}})'
            print(string)
            p = re.compile(string)
            print(content)
            all_locations = re.finditer(p, content)
            for i in all_locations:
                print(i.span())
        
        pass

class variableWidget(QWidget):
    def __init__(self, content):
        super(variableWidget, self).__init__()
        self.Vbox = QVBoxLayout()
        self.setLayout(self.Vbox)
        variables = variableWidget.getAllVariables(content)
        for variable in variables:
            layout = QHBoxLayout()
            layout.addSpacerItem(QSpacerItem(40, 0))
            label = QLabel(text=variable + ":")
            line_edit = QLineEdit()
            line_edit.setText(variables[variable])
            layout.addWidget(label)
            layout.addWidget(line_edit)
            layout.addSpacerItem(QSpacerItem(40, 0))
            self.Vbox.addLayout(layout)
        layout = QHBoxLayout()
        layout.addSpacerItem(QSpacerItem(40, 0))
        self.submit = QPushButton(text="Submit")
        layout.addWidget(self.submit)
        layout.addSpacerItem(QSpacerItem(40, 0))
        self.Vbox.addLayout(layout)

    def getAllVariables(content):
        vars = dict()
        p = re.compile(r'({{[^}]+}})')
        all_vars = re.findall(p, ''.join(content))
        for variable in all_vars:
            if variable in vars.keys():
                continue
            title = variable[2:-2]
            title = title.split('|')
            if len(title) == 1:
                title = title[0]
                suggested = ''
            else:
                suggested = title[1]
                title = title[0]
            if title in vars.keys():
                continue
            vars[title] = suggested
        return vars
class TemplateWidget(QWidget):
    def __init__(self, content, host):
        super(TemplateWidget, self).__init__()
        self.hostname = host
        self.initUI(content)
        pass

    def initUI(self, content):
        self.mainLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.setWindowTitle(self.hostname)

        self.templateEditor = TemplateEditor(content)
        self.mainLayout.addWidget(self.templateEditor)

        self.varWidget = variableWidget(content)
        self.mainLayout.addWidget(self.varWidget)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key.Key_Return:
            self.submit.click()
        return super().keyPressEvent(a0)
