from LibraryImport import *

class TemplateEditor(QTextEdit):
    def __init__(self, content):
        super(TemplateEditor, self).__init__()
        self.content = content
        self.html = content
        self.setHtml(self.html)
        self.variables = variableWidget.getAllVariables(self.content)
        self.variable_locations = self.getAllVarLocations(self.variables, self.content)
        charStyle = QTextCharFormat()
        charStyle.setForeground(QColorConstants.Cyan)
        self.html = self.formatColor(self.formatText(self.content, self.variable_locations).split(chr(0x999)))
        self.setHtml(self.html)
        self.cursorPositionBeforeChange = self.textCursor().position()
        self.textChanged.connect(self.onTextChange)

    def onTextChange(self):
        #TODO ctrl+z will mess up the locations if you move cursor to different locations need to figure out how to handle that properly
        isCursorInVar = self.checkCursorInVar(self.cursorPositionBeforeChange)
        currentCursorPos = self.textCursor().position()
        shift= currentCursorPos - self.cursorPositionBeforeChange
        print(currentCursorPos)
        if isCursorInVar:
            variable, iter = isCursorInVar
            start, end = self.variable_locations[variable][iter]
            end += shift
            if end >= start: self.variable_locations[variable][iter] = [start, end]
            else: self.variable_locations[variable].pop(iter)
        self.shiftPositions(self.cursorPositionBeforeChange, shift)
        print(self.variable_locations)
            

    def timerEvent(self, e: QTimerEvent) -> None:
        print(self.toHtml())
        return super().timerEvent(e)

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

    def formatColor(self, string_list):
        string_list = string_list[0]
        sorted_list_of_seq = sorted([item for sublist in list(self.variable_locations.values()) for item in sublist], reverse=True)
        print(sorted_list_of_seq)
        for seq in sorted_list_of_seq:
            start, end = seq
            string_list = f"{string_list[:start]}<span style=\"color: cyan;\">{string_list[start:end]}</span>{string_list[end:]}"
        string_list = string_list.replace('\n', '<br>')
        return string_list

    def shiftPositions(self, startPos, shift):
        for var in self.variable_locations:
            for iter, seq in enumerate(self.variable_locations[var]):
                if seq[0] > startPos:
                    start, end = self.variable_locations[var][iter]
                    self.variable_locations[var][iter] = (start + shift, end + shift)

    def formatText(self, content, variable_locations_origin:dict, variable_value={"test": "WOOW", "testing": "BOO"}):
        #TODO write a script to format text with syntax highlighting and auto replacement for variables
        result_string = content
        variable_locations = variable_locations_origin
        print(self.variables)
        for variable_name in variable_locations:
            for iter, location in enumerate(variable_locations[variable_name]):
                start, end = location
                value = variable_value[variable_name]
                result_string = result_string[:start] + f"{value}" + result_string[end:]
                shift = start+len(value) - end
                self.shiftPositions(end, shift)
                variable_locations[variable_name][iter] = [start, start+len(value)]
        return result_string

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
            pass
        return super().keyPressEvent(a0)
