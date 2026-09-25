import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Calendar.Model.SecureDatabase import SecureDatabase


def get_test_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    os.unlink(path)  # SecureDatabase will create it
    return path


def test_create_database():
    path = get_test_db()
    try:
        db = SecureDatabase(path, "testpassword123")
        assert db.verify_passphrase() is True
        db.close()
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_save_and_retrieve_event():
    path = get_test_db()
    try:
        db = SecureDatabase(path, "testpass")
        event_id = db.save_event(
            date_str="2026-07-12",
            time_str="08:00",
            title="Team Meeting",
            category="Operation",
            detail="Discuss objectives"
        )
        assert event_id is not None
        events = db.get_events_for_date("2026-07-12")
        assert len(events) == 1
        assert events[0]['title'] == "Team Meeting"
        assert events[0]['time'] == "08:00"
        assert events[0]['category'] == "Operation"
        assert events[0]['detail'] == "Discuss objectives"
        db.close()
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_update_event():
    path = get_test_db()
    try:
        db = SecureDatabase(path, "testpass")
        event_id = db.save_event("2026-07-12", "08:00", "Old Title", "Operation", "old detail")
        db.save_event("2026-07-12", "09:00", "New Title", "Implant", "new detail", event_id=event_id)
        events = db.get_events_for_date("2026-07-12")
        assert len(events) == 1
        assert events[0]['title'] == "New Title"
        assert events[0]['time'] == "09:00"
        db.close()
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_delete_event():
    path = get_test_db()
    try:
        db = SecureDatabase(path, "testpass")
        event_id = db.save_event("2026-07-12", "08:00", "To Delete", "Operation", "bye")
        db.delete_event(event_id)
        events = db.get_events_for_date("2026-07-12")
        assert len(events) == 0
        db.close()
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_multiple_events_sorted_by_time():
    path = get_test_db()
    try:
        db = SecureDatabase(path, "testpass")
        db.save_event("2026-07-12", "14:00", "Afternoon", "Operation", "")
        db.save_event("2026-07-12", "08:00", "Morning", "Operation", "")
        db.save_event("2026-07-12", None, "All Day", "Operation", "")
        events = db.get_events_for_date("2026-07-12")
        assert len(events) == 3
        # All-day (NULL time) sorts first, then by time
        assert events[0]['title'] == "All Day"
        assert events[1]['title'] == "Morning"
        assert events[2]['title'] == "Afternoon"
        db.close()
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_persistence_across_reopen():
    path = get_test_db()
    try:
        db = SecureDatabase(path, "testpass")
        db.save_event("2026-07-12", "10:00", "Persistent", "Operation", "stays")
        db.close()
        db2 = SecureDatabase(path, "testpass")
        events = db2.get_events_for_date("2026-07-12")
        assert len(events) == 1
        assert events[0]['title'] == "Persistent"
        db2.close()
    finally:
        if os.path.exists(path):
            os.unlink(path)
