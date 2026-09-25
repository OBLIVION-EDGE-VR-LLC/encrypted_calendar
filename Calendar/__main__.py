import sys
from PyQt5.QtWidgets import QApplication
from Calendar.Model.Tools.Constants import STYLE_SHEET_GLOBAL
from Calendar.Views.MainWindow import MainWindow

app = QApplication(sys.argv)
app.setStyleSheet(STYLE_SHEET_GLOBAL)
ex = MainWindow()
sys.exit(app.exec_())
