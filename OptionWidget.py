from LibraryImport import *


class OptionWidget(QWidget):
    def __init__(self):
        super(OptionWidget, self).__init__()
    def checkIfOptionFileExists(self):
        print(sys.path)
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    options = OptionWidget()
    options.show()
    options.checkIfOptionFileExists()
    sys.exit(app.exec())