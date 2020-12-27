import sys
from Calendar.Views.MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
ex = MainWindow()
sys.exit(app.exec_())
