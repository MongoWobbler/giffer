import sys
from PySide2.QtWidgets import QApplication
import giffer.main as giffer


if __name__ == '__main__':
    app = QApplication(sys.argv)  # set up Qt application
    video = sys.argv[1] if len(sys.argv) > 1 else None  # used to open giffer with video
    window = giffer.MainWindow(starting_video=video)
    window.show()
    sys.exit(app.exec_())
