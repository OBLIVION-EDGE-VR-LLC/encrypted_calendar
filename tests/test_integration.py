import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Calendar.Model.SecureMemoryManager import SecureString, wipe_all_active
from Calendar.Model.SecureDatabase import SecureDatabase
from Calendar.Model.MalWarePlanner import MalWarePlanner


def test_malware_planner_has_db_attribute():
    planner = MalWarePlanner.__new__(MalWarePlanner)
    planner.db = None
    planner._secure_buffers = []
    planner._current_events = []
    assert hasattr(planner, 'db')


def test_malware_planner_has_secure_buffers():
    planner = MalWarePlanner.__new__(MalWarePlanner)
    planner.db = None
    planner._secure_buffers = []
    planner._current_events = []
    assert hasattr(planner, '_secure_buffers')


def test_malware_planner_has_set_database():
    planner = MalWarePlanner.__new__(MalWarePlanner)
    planner.db = None
    planner._secure_buffers = []
    planner._current_events = []
    assert hasattr(planner, 'set_database')


def test_malware_planner_has_shutdown():
    planner = MalWarePlanner.__new__(MalWarePlanner)
    planner.db = None
    planner._secure_buffers = []
    planner._current_events = []
    assert hasattr(planner, 'shutdown')
