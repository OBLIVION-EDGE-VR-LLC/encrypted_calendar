'''
Although it is titled the Landing page it is being treated more like the initial
Setup.  Luckily this is just a view so it is subject to change, the Developer can
always make a view called GameBoard (as an example) which inherits the BaseView
'''

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCalendarWidget

sys.path.insert(0, '../Controllers')
sys.path.insert(1, '../Model')
sys.path.insert(2, '')

from Calendar.Model.CustomLabel import *


class LandingPage(BaseView.BaseView):

    def __init__(self):
        super(LandingPage, self).__init__()
        self.ctrl = None
        self.components = []
        self.p = None
        self.p2 = None
        self.initUI()


    def initUI(self):

        checkbox = QCheckBox('Show title', self)
        checkbox.move(20, 20)
        checkbox.toggle()
        self.components.append(checkbox)
        #insertimage onto screen

        self.p = QPixmap(os.getcwd() + '/images/1337_Logo_small.png')

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('StegoPop')
        self.folderitems = QDockWidget("DockWidget 1", self)
        self.fileitems = QDockWidget("Top-Secret Scheduler", self)
        self.folderButton = QDockWidget("DockWidget 3", self)

        self.dockWidget1 = QCalendarWidget()
        self.dockWidget2 = QTextEdit()
        self.dockWidget3 = QTextEdit()
        self.fileitems.setWidget(self.dockWidget1)
        self.fileitems.setFloating(False)
        # Set Style sheet here
        self.fileitems.setStyleSheet("""QDockWidget::title{ background-color: orange; text-align: 
        center;border-radius: 10px; } QDockWidget::title:hover{ background-color: red;} 
        QCalendarWidget QAbstractItemView{ selection-color: green; selection-background-color: black} """)

        self.folderitems.setWidget(self.dockWidget2)
        self.folderitems.setFloating(False)
        self.folderButton.setWidget(self.dockWidget3)
        self.folderButton.setFloating(False)

        hbox = QHBoxLayout(self)

        splitter1 = QSplitter(self)
        splitter1.setOrientation(Qt.Horizontal)

        left = QFrame(splitter1)
        left.setFrameShape(QFrame.StyledPanel)

        center = QFrame(splitter1)
        center.setFrameShape(QFrame.StyledPanel)


        splitter2 = QSplitter(splitter1)
        sizePolicy = splitter2.sizePolicy()
        sizePolicy.setHorizontalStretch(1)

        splitter2.setSizePolicy(sizePolicy)
        splitter2.setOrientation(Qt.Vertical)

        top_right = QFrame(splitter2)
        top_right.setFrameShape(QFrame.StyledPanel)
        splitter2.addWidget(self.fileitems)
        #splitter2.addWidget(logo)
        bottom_right = QFrame(splitter2)
        bottom_right.setFrameShape(QFrame.StyledPanel)
        splitter2.addWidget(self.folderitems)
        splitter2.addWidget(self.folderButton)
        splitter2.setGeometry(0,0,499,700)
        hbox.addWidget(splitter1)
        hbox.addWidget(top_right)
        self.setGeometry(500, 500, 750, 750)

        pallete = QPalette()
        pallete.setColor(QPalette.Background, Qt.gray)
        #pallete.setColor(QPalette.Background, Qt.green)
        self.setAutoFillBackground(True)
        self.setPalette(pallete)

        self.show()
