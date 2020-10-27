from PySide2 import QtWidgets, QtCore


class AboutWindow(QtWidgets.QWidget):
    """
    Small window showing some info to the user about the giffer.exe
    """
    def __init__(self, parent=None):
        super(AboutWindow, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('About')
        self.version = 'v1.0'
        self.build()

    def build(self):
        """
        Builds the UI.
        """
        main_layout = QtWidgets.QVBoxLayout(self)

        name = QtWidgets.QLabel(' '.join(['giffer.exe', self.version]))
        author = QtWidgets.QLabel('Made by Christian Corsica')
        site = QtWidgets.QLabel('''<a href='https://www.christiancorsica.com/'>Personal Website</a>''')
        documentation = QtWidgets.QLabel('''<a href='https://github.com/MongoWobbler/giffer'>Documentation</a>''')

        site.setOpenExternalLinks(True)
        documentation.setOpenExternalLinks(True)

        main_layout.addWidget(name, alignment=QtCore.Qt.AlignHCenter)
        main_layout.addWidget(author)
        main_layout.addWidget(site)
        main_layout.addWidget(documentation)
