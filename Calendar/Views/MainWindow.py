import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

sys.path.insert(0, '../Controllers')
sys.path.insert(1, '../Model')
sys.path.insert(2, '')

from Calendar.Views import LandingPage


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ctrl = None
        self.components = []
        self.view = None
        self.initUI()

    def initUI(self):
        self.view = LandingPage.LandingPage()
        self.view.initUi()
        self.statusBar().showMessage('StatusBar: Everything is Deleted when Closed')
        self.setCentralWidget(self.view)

        self.setGeometry(300, 300, 796, 650) #796, 650

        self.setWindowTitle('RAM Calendar')
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
