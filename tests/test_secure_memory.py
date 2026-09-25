import ctypes
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Calendar.Model.SecureMemoryManager import secure_wipe, SecureString, wipe_all_active


def test_secure_wipe_zeros_buffer():
    """After secure_wipe, the buffer should be all zeros."""
    size = 256
    buf = ctypes.create_string_buffer(b"SENSITIVE DATA HERE" * 13, size)
    secure_wipe(buf, size)
    # After wipe, all bytes should be zero (final passes are zero)
    assert buf.raw == b'\x00' * size


def test_secure_wipe_does_not_leave_original():
    """Original data must not remain after wipe."""
    original = b"TOP SECRET EVENT DETAILS!!!"
    size = len(original)
    buf = ctypes.create_string_buffer(original, size)
    secure_wipe(buf, size)
    assert buf.raw != original


def test_secure_string_get_returns_text():
    ss = SecureString("my secret event")
    assert ss.get() == "my secret event"


def test_secure_string_clear_wipes_data():
    ss = SecureString("my secret event")
    ss.clear()
    assert ss.get() is None


def test_secure_string_del_wipes():
    ss = SecureString("ephemeral")
    ss.__del__()
    assert ss.get() is None


def test_wipe_all_active_clears_all():
    s1 = SecureString("one")
    s2 = SecureString("two")
    wipe_all_active()
    assert s1.get() is None
    assert s2.get() is None
