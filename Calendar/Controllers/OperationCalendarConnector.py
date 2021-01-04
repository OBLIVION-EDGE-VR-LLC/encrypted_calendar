from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QListWidget, QPushButton, QTextEdit, QTimeEdit, QComboBox, QLineEdit, QCheckBox

from Calendar.Controllers.BaseController import BaseController
#import model
from Calendar.Model.MalWarePlanner import MalWarePlanner


class OperationCalendarConnector(BaseController):
    def __init__(self, view):
        super(OperationCalendarConnector, self).__init__(view)
        ##################
        # Connect Events #
        ##################
        self.OperationPlanner = MalWarePlanner(parent=view)
        self.OperationPlanner.event_list = QListWidget(parent=view.splitter2)
        self.OperationPlanner.event_title = QLineEdit("Operation Title", parent=view.splitter2)
        self.OperationPlanner.event_category = QComboBox(parent=view.splitter2)
        self.OperationPlanner.event_time = QTimeEdit(QTime(8, 0), parent=view.splitter2)
        self.OperationPlanner.allday_check = QCheckBox('All Day', parent=view.splitter2)
        self.OperationPlanner.event_detail = QTextEdit("Event Detail", parent=view.splitter2)
        self.OperationPlanner.add_button = QPushButton('Add/Update', parent=view.splitter2)
        self.OperationPlanner.del_button = QPushButton('Delete', parent=view.splitter2)


        self.OperationPlanner.allday_check.toggled.connect(self.OperationPlanner.event_time.setDisabled)
        # disable time when "all day" is checked.
        self.OperationPlanner.allday_check.toggled.connect(self.OperationPlanner.event_time.setDisabled)

        # Populate the event list when the calendar is clicked
        self.OperationPlanner.selectionChanged.connect(self.OperationPlanner.populate_list)

        # Populate the event form when an item is selected
        self.OperationPlanner.event_list.itemSelectionChanged.connect(self.OperationPlanner.populate_form)

        # Save event when save is hit
        self.OperationPlanner.add_button.clicked.connect(self.OperationPlanner.save_event)

        # connect delete button
        self.OperationPlanner.del_button.clicked.connect(self.OperationPlanner.delete_event)

        # Enable 'delete' only when an event is selected
        self.OperationPlanner.event_list.itemSelectionChanged.connect(
            self.OperationPlanner.check_delete_btn)
        self.OperationPlanner.check_delete_btn()

        # check for selection of "new…" for category
        self.OperationPlanner.event_category.currentTextChanged.connect(self.OperationPlanner.on_category_change)
        # Add event categories
        self.OperationPlanner.event_category.addItems(
            ['Select category…', 'New…', 'Implant',
             'Operation', 'DocExfil', 'other']
        )
        self.OperationPlanner.event_category.model().item(0).setEnabled(False)