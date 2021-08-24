'''
Although it is titled the Landing page it is being treated more like the initial
Setup.  Luckily this is just a view so it is subject to change, the Developer can
always make a view called GameBoard (as an example) which inherits the BaseView
'''

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCalendarWidget

from Calendar.Controllers.OperationCalendarConnector import OperationCalendarConnector
from Calendar.Model.MalWarePlanner import MalWarePlanner
from Calendar.Model.Tools.Constants import STYLE_SHEET_CALENDAR

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
        self.spliter2 = None
        self.initUi()

    def initUi(self):

        self.splitter1 = QSplitter(self)
        self.splitter1.setOrientation(Qt.Horizontal)

        self.splitter2 = QSplitter(self.splitter1)
        sizePolicy = self.splitter2.sizePolicy()
        sizePolicy.setHorizontalStretch(1)

        self.setSizePolicy(sizePolicy)
        self.splitter2.setOrientation(Qt.Vertical)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('RAM Calendar')
        self.folderitems = QDockWidget("Secret Schedule", self)
        self.fileitems = QDockWidget("Schedule Maker", self)
        self.folderButton = QDockWidget("Mission Report", self)
        controller_planner = OperationCalendarConnector(self)
        self.dockWidget1 = controller_planner.OperationPlanner
        self.dockWidget2 = QTextEdit()
        self.dockWidget3 = QTextEdit()
        self.fileitems.setWidget(self.dockWidget1)
        self.fileitems.setFloating(False)



        # disable closable and floatable feautres
        self.folderitems.setFeatures(QDockWidget.DockWidgetMovable)
        self.folderButton.setFeatures(QDockWidget.DockWidgetMovable)
        self.fileitems.setFeatures(QDockWidget.DockWidgetMovable)

        # Set Style sheet here
        self.fileitems.setStyleSheet(STYLE_SHEET_CALENDAR)

        self.folderitems.setStyleSheet("""QDockWidget::title{ background-color: orange; text-align: 
                center;border-radius: 10px; } QDockWidget::title:hover{ background-color: green;} """)
        self.folderButton.setStyleSheet("""QDockWidget::title{ background-color: orange; text-align: 
                center;border-radius: 10px; } QDockWidget::title:hover{ background-color: red;} """)

        self.folderitems.setWidget(self.dockWidget2)
        self.folderitems.setFloating(False)
        self.folderButton.setWidget(self.dockWidget3)
        self.folderButton.setFloating(False)

        hbox = QHBoxLayout(self)



        top_right = QFrame(self.splitter2)
        top_right.setFrameShape(QFrame.StyledPanel)
        self.splitter1.addWidget(self.fileitems)
        bottom_right = QFrame(self.splitter2)
        bottom_right.setFrameShape(QFrame.StyledPanel)
        self.splitter2.addWidget(self.folderitems)
        self.splitter2.addWidget(self.folderButton)
        self.splitter2.setGeometry(0, 0, 499, 700)
        hbox.addWidget(self.splitter1)
        hbox.addWidget(top_right)
        self.setGeometry(500, 500, 750, 750) # 500, 500, 750,750

        pallete = QPalette()
        pallete.setColor(QPalette.Background, Qt.gray)

        self.setAutoFillBackground(True)
        self.setPalette(pallete)

        self.show()
