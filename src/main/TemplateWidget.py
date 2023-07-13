from LibraryImport import *

class TemplateEditor(QTextEdit):
    def __init__(self, content):
        super(TemplateEditor, self).__init__()
        self.setReadOnly(True)
        self.variables = variableWidget.getAllVariables(content)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        self.fonts = QFont()
        self.fonts.setFamily("Consolas")
        self.fonts.setPointSize(12)
        self.setFont(self.fonts)

        self.share = Share(self)
        self.share.setFixedSize(30, 30)

        self.html = content
        self.content = content
        self.setPlainText(self.html)
        self.content = self.toHtml()
        self.html = self.formatText(self.content, self.variables)
        self.setHtml(self.html)
        self.cursorPositionBeforeChange = self.textCursor().position()


    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.share.move(self.viewport().width() - 30, 0)
        return super().resizeEvent(a0)

    def timerEvent(self, e: QTimerEvent) -> None:
        return super().timerEvent(e)

    def connect_line_edits(self, field, text):
        self.variables[field] = text
        self.setHtml(self.formatText(self.content, self.variables))

    def keyPressEvent(self, e: QKeyEvent) -> None:
        self.cursorPositionBeforeChange = self.textCursor().position()
        if e.text() and (126 >= ord(e.text()) >= 32 or ord(e.text()) in [9, 10, 13]):
            charStyle = QTextCharFormat()
            charStyle.setForeground(QColorConstants.White) if not self.checkCursorInVar(self.cursorPositionBeforeChange) else charStyle.setForeground(QColorConstants.Cyan) 
            self.textCursor().insertText(e.text(), charStyle)
        else:    
            super().keyPressEvent(e)
        # print(repr(self.toPlainText()))
        # print(self.toHtml())

    def getAllVarLocations(self, variables, content):
        variable_locations = dict()
        for variable in variables:
            string = r'\{\{(' + variable + r')\}\}'
            p = re.compile(string)
            all_locations = re.finditer(p, content)
            variable_locations[variable] = (list(map(lambda location: location.span(), all_locations)))
        return variable_locations

    def checkCursorInVar(self, cursor_location):
        cursorLocation = cursor_location
        for variable in self.variable_locations:
            for iter, area in enumerate(self.variable_locations[variable]):
                start, end = area
                if end >= cursorLocation >= start:
                    # print(f"Cursor is modifying variable:{variable} at positions:{start}:{end}")
                    return variable, iter
        return False

    def formatText(self, content:str, variables:dict):
        result_string = content
        for variable_name in variables:
            value = self.variables[variable_name] if self.variables[variable_name] != '' else f"<span style=\"color: red;\">{variable_name.upper()}</span>"
            result_string = re.sub("\{\{" + variable_name + "(\|[^}]*)?\}\}", f"<span style=\"color: cyan;\">{value}</span>", result_string)
        return f"<span style=\"color: white;\">{result_string}</span>"

class variableWidget(QWidget):
    def __init__(self, content):
        super(variableWidget, self).__init__()
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.Vbox = QVBoxLayout()
        self.setLayout(self.Vbox)
        variables = variableWidget.getAllVariables(content)
        self.line_edits = dict()
        self.send_to_widget = lambda *args: None
        for variable in variables:
            line_edit = QLineEdit()
            line_edit.setText(variables[variable])
            line_edit.textChanged.connect(self.save_variable_name(variable))
            line_edit.setPlaceholderText(variable.upper())
            self.line_edits[variable] = line_edit
            self.Vbox.addWidget(line_edit)
        self.Vbox.addSpacerItem(QSpacerItem(0, 0, vPolicy=QSizePolicy.Policy.Expanding))


    def save_variable_name(self, name):
        def send_change_to_text_widget(text):
            self.send_to_widget(name, text)
        return send_change_to_text_widget

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
        
class Submit(QPushButton):
    def __init__(self, *args, **kwargs):
        super(Submit, self).__init__(*args, **kwargs)

class Share(QPushButton):
    def __init__(self, *args, **kwargs):
        super(Share, self).__init__(*args, **kwargs)
        self.setText('\U0001F517')
        self.setFont(QFont('Arial', 12))

class TemplateWidget(QWidget):
    def __init__(self, content, host):
        super(TemplateWidget, self).__init__()
        self.hostname = host
        self.initUI(content)
        pass

    def initUI(self, content):
        self.mainLayout = QVBoxLayout()
        self.innerLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)
        self.setWindowTitle(self.hostname)

        self.templateEditor = TemplateEditor(content)
        self.innerLayout.addWidget(self.templateEditor)

        self.varWidget = variableWidget(content)
        self.innerLayout.addWidget(self.varWidget)
        self.mainLayout.addLayout(self.innerLayout)

        self.submit = Submit(text="Submit")
        self.mainLayout.addWidget(self.submit)
        
        self.varWidget.send_to_widget = self.templateEditor.connect_line_edits

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key.Key_Return:
            pass
        return super().keyPressEvent(a0)
