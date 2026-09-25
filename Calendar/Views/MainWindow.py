import atexit
import os
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QMessageBox, QLineEdit

sys.path.insert(0, '../Controllers')
sys.path.insert(1, '../Model')
sys.path.insert(2, '')

from Calendar.Model.SecureDatabase import SecureDatabase
from Calendar.Model.SecureMemoryManager import wipe_all_active
from Calendar.Model.Tools.Constants import STYLE_SHEET_GLOBAL
from Calendar.Views import LandingPage

# Database file location
_DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'calendar_secure.db')


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ctrl = None
        self.components = []
        self.view = None
        self.db = None
        self._authenticate()

    def _authenticate(self):
        """Prompt for passphrase and open encrypted database."""
        max_attempts = 3
        db_exists = os.path.exists(_DB_PATH)

        for attempt in range(max_attempts):
            passphrase, ok = QInputDialog.getText(
                self, 'Secure Calendar',
                'Enter passphrase:' if db_exists else 'Create new passphrase:',
                QLineEdit.Password
            )

            if not ok or not passphrase:
                sys.exit(0)

            self.db = SecureDatabase(_DB_PATH, passphrase)

            if self.db.verify_passphrase():
                self.initUI()
                return
            else:
                self.db.close()
                self.db = None
                remaining = max_attempts - attempt - 1
                if remaining > 0:
                    QMessageBox.warning(
                        self, 'Authentication Failed',
                        f'Wrong passphrase. {remaining} attempts remaining.'
                    )

        QMessageBox.critical(self, 'Locked Out', 'Too many failed attempts.')
        sys.exit(1)

    def initUI(self):
        self.setStyleSheet(STYLE_SHEET_GLOBAL)
        self.view = LandingPage.LandingPage(db=self.db)
        self.statusBar().showMessage('Encrypted Calendar - All data secured at rest')
        self.setCentralWidget(self.view)

        self.setGeometry(300, 300, 796, 650)
        self.setWindowTitle('Secure Calendar')
        self.show()

        # Backup shutdown via atexit
        atexit.register(self._shutdown)

    def closeEvent(self, event):
        """Override close to securely wipe all memory."""
        self._shutdown()
        event.accept()

    def _shutdown(self):
        """Securely wipe all data and close database."""
        if self.view and hasattr(self.view, 'ctrl') and self.view.ctrl:
            if hasattr(self.view.ctrl, 'OperationPlanner'):
                self.view.ctrl.OperationPlanner.shutdown()
        wipe_all_active()
        if self.db:
            self.db.close()
            self.db = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
