"""
SecureMemoryManager - mlock'd buffers with 8-pass secure wipe.

Wipe pattern: 3 passes RAND_bytes + 5 passes zeros + OPENSSL_cleanse barrier.
All decrypted event data MUST be held in SecureString instances.
"""

import ctypes
import ctypes.util
import os
import weakref

# Path to bundled OpenSSL 3.5
_LIB_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'includes', 'openssl-3.5.0', 'dist', 'lib64', 'libcrypto.so'
)

# Fall back to system libcrypto for testing if bundled not yet built
if os.path.exists(_LIB_PATH):
    _libcrypto = ctypes.CDLL(_LIB_PATH)
else:
    _system_path = ctypes.util.find_library('crypto')
    if _system_path:
        _libcrypto = ctypes.CDLL(_system_path)
    else:
        raise RuntimeError("No libcrypto found. Run ./includes/build_deps.sh first.")

# Configure function signatures
_libcrypto.RAND_bytes.argtypes = [ctypes.c_char_p, ctypes.c_int]
_libcrypto.RAND_bytes.restype = ctypes.c_int
_libcrypto.OPENSSL_cleanse.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
_libcrypto.OPENSSL_cleanse.restype = None

# libc for mlock/munlock
_libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
_libc.mlock.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
_libc.mlock.restype = ctypes.c_int
_libc.munlock.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
_libc.munlock.restype = ctypes.c_int


def secure_wipe(buffer, size):
    """
    Perform 8-pass secure wipe on a ctypes buffer.
    Passes 1-3: random data via RAND_bytes
    Passes 4-8: zeros
    Final: OPENSSL_cleanse as compiler optimization barrier
    """
    ptr = ctypes.cast(buffer, ctypes.c_char_p)

    # 3 random passes
    for _ in range(3):
        _libcrypto.RAND_bytes(ptr, ctypes.c_int(size))

    # 5 zero passes
    zero_buf = b'\x00' * size
    for _ in range(5):
        ctypes.memmove(ptr, zero_buf, size)

    # Final barrier - prevents compiler from optimizing away the writes
    _libcrypto.OPENSSL_cleanse(ctypes.cast(ptr, ctypes.c_void_p), ctypes.c_size_t(size))


# Global registry of active SecureString instances
_active_strings = weakref.WeakSet()


class SecureString:
    """
    Holds sensitive text in an mlock'd buffer. Auto-wipes on clear() or __del__.
    """

    def __init__(self, text):
        if text is None:
            self._buffer = None
            self._size = 0
            return

        encoded = text.encode('utf-8')
        self._size = len(encoded)
        # Allocate buffer
        self._buffer = ctypes.create_string_buffer(encoded, self._size)
        # mlock to prevent swapping
        addr = ctypes.addressof(self._buffer)
        _libc.mlock(ctypes.c_void_p(addr), ctypes.c_size_t(self._size))
        # Register globally
        _active_strings.add(self)

    def get(self):
        """Return the stored string, or None if wiped."""
        if self._buffer is None or self._size == 0:
            return None
        try:
            return self._buffer.raw.decode('utf-8')
        except (ValueError, UnicodeDecodeError):
            return None

    def clear(self):
        """Securely wipe the buffer contents."""
        if self._buffer is not None and self._size > 0:
            secure_wipe(self._buffer, self._size)
            # munlock after wipe
            addr = ctypes.addressof(self._buffer)
            _libc.munlock(ctypes.c_void_p(addr), ctypes.c_size_t(self._size))
            self._buffer = None
            self._size = 0

    def __del__(self):
        self.clear()

    def __repr__(self):
        return "SecureString(***)" if self._buffer else "SecureString(wiped)"


def wipe_all_active():
    """Wipe all active SecureString instances. Called on app shutdown."""
    for ss in list(_active_strings):
        ss.clear()
