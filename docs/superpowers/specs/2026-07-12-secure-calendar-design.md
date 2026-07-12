# Secure Calendar Design Spec

## Overview

Enhance the RAM-only calendar application with:
1. **Encryption at rest** via SQLCipher (AES-256) compiled against bundled OpenSSL 3.5
2. **Secure erase** (3 random passes + 5 zero passes) on record deletion and after viewing
3. **Post-quantum algorithm availability** via OpenSSL 3.5's native ML-KEM/ML-DSA support
4. **Passphrase-based key derivation** via Argon2id

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   PyQt5 UI Layer                     │
│          (MalWarePlanner / LandingPage)              │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              SecureMemoryManager                      │
│  - mlock'd buffers for decrypted event data          │
│  - secure_wipe(): 3 random passes + 5 zero passes   │
│  - hooks into clear_form() / populate_list()         │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              SecureDatabase (SQLCipher)               │
│  - AES-256 encryption at rest                        │
│  - Key derived via Argon2id from user passphrase     │
│  - Compiled against ./includes/openssl-3.5           │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│         ./includes/openssl-3.5.0/                    │
│  - PQ algorithms (ML-KEM, ML-DSA) available          │
│  - OPENSSL_cleanse used for secure memory wipe       │
│  - RAND_bytes for random pass generation             │
└─────────────────────────────────────────────────────┘
```

### Data Flow

1. App launches -> passphrase dialog -> Argon2id derives 256-bit key
2. SQLCipher opens encrypted DB with derived key
3. User selects a date -> events queried from SQLCipher -> decrypted into mlock'd buffer -> displayed in UI
4. User navigates away / clears form -> secure_wipe() runs 8-pass erase on the buffer holding old event data
5. User deletes a record -> row deleted from SQLCipher + secure_wipe() on the in-memory copy
6. App closes -> all mlock'd buffers get secure_wipe() -> SQLCipher DB closed (remains encrypted on disk)

## Secure Memory Manager

**File:** `Calendar/Model/SecureMemoryManager.py`

### Responsibilities

- Allocate mlock'd byte buffers for any decrypted event data using ctypes and mmap
- Provide `secure_wipe(buffer, size)` that performs:
  - Pass 1-3: overwrite with RAND_bytes (from bundled OpenSSL 3.5)
  - Pass 4-8: overwrite with `\x00` zeros
  - Final: call OPENSSL_cleanse as a compiler-barrier to prevent optimization away
- Provide `SecureString` wrapper class that holds text in an mlock'd buffer and auto-wipes on `__del__` or explicit `.clear()`

### OpenSSL Binding via ctypes

```python
libcrypto = ctypes.CDLL("./includes/openssl-3.5.0/dist/lib/libcrypto.so")
libcrypto.RAND_bytes(buffer, size)       # random passes
libcrypto.OPENSSL_cleanse(buffer, size)  # final barrier
```

### mlock Usage

- All buffers holding decrypted event text get mlock() to prevent swap-to-disk
- munlock() called only after secure_wipe() completes

## Secure Database (SQLCipher)

**File:** `Calendar/Model/SecureDatabase.py`

### Schema

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,          -- ISO format YYYY-MM-DD
    time TEXT,                   -- HH:MM or NULL for all-day
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    detail TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_date ON events(date);
```

### Key Derivation

- On startup, a QInputDialog prompts for passphrase
- Passphrase -> Argon2id (time_cost=3, memory=65536KB, parallelism=4) -> 256-bit key
- Key passed to SQLCipher via `PRAGMA key = x'...'`
- Argon2id provided by the bundled OpenSSL 3.5's KDF provider

### SQLCipher Configuration

```sql
PRAGMA cipher_page_size = 4096;
PRAGMA kdf_iter = 256000;
PRAGMA cipher_memory_security = ON;
```

### Integration with MalWarePlanner

- `MalWarePlanner.events` dict replaced with method calls to SecureDatabase
- `save_event()` -> INSERT or UPDATE in SQLCipher
- `delete_event()` -> DELETE from SQLCipher + VACUUM to reclaim space
- `populate_list()` -> SELECT by date, results loaded into SecureString buffers

### First-Run Behavior

- If no DB file exists, create it with the passphrase-derived key
- If DB exists but passphrase is wrong, SQLCipher throws error -> re-prompt (max 3 attempts then exit)

## OpenSSL 3.5 Integration & Build

### Directory Structure

```
./includes/
├── openssl-3.5.0/          # OpenSSL source + build
│   ├── dist/               # Compiled output (lib/, include/, bin/)
│   └── ...
├── sqlcipher/              # SQLCipher source + build
│   └── ...
└── build_deps.sh           # Master build script for both
```

### OpenSSL Build

```bash
cd ./includes/openssl-3.5.0
./Configure --prefix=$(pwd)/dist --openssldir=$(pwd)/dist/ssl \
    enable-ml-kem enable-ml-dsa \
    shared linux-x86_64
make -j$(nproc)
make install_sw
```

### SQLCipher Build

```bash
cd ./includes/sqlcipher
./configure --enable-tempstore=yes \
    CFLAGS="-DSQLITE_HAS_CODEC -I../openssl-3.5.0/dist/include" \
    LDFLAGS="-L../openssl-3.5.0/dist/lib -lcrypto"
make
```

### Post-Quantum Availability

- ML-KEM (FIPS 203) and ML-DSA (FIPS 204) enabled at compile time
- Available for future use (PQ-secured network sync, PQ key exchange for multi-user)
- Currently used for: RAND_bytes, OPENSSL_cleanse, and Argon2id KDF

## Wipe Triggers & App Lifecycle

| Trigger | Location | What Gets Wiped |
|---------|----------|-----------------|
| `clear_form()` | MalWarePlanner.py | Previous event title, detail, category strings |
| `populate_list()` | MalWarePlanner.py | All previously loaded event summary strings |
| `populate_form()` | MalWarePlanner.py | Previous form data before loading new event |
| `delete_event()` | MalWarePlanner.py | Deleted event's in-memory copy after DB deletion |
| App `closeEvent` | MainWindow.py | All active SecureString instances + DB close |

### Close Event Handling

Override `closeEvent(self, event)` in MainWindow to:
1. Wipe all active SecureString buffers (8-pass)
2. Close SQLCipher connection
3. munlock all locked memory regions
4. Accept the close event

### Error/Crash Safety

- If the app crashes, mlock'd pages are freed by the OS but NOT wiped (accepted limitation)
- The encrypted DB on disk remains safe regardless of crash state
- Register `atexit` handler as backup for graceful shutdown paths that bypass closeEvent

## Dependencies

**requirements.txt:**
```
PyQt5
argon2-cffi
```

SQLCipher and OpenSSL are local compiled deps in `./includes/`, not pip packages.

## NIST Compliance Notes

- **NIST SP 800-131A**: AES-256 for encryption at rest
- **NIST SP 800-88**: Secure erase via multi-pass overwrite (3 random + 5 zero)
- **FIPS 203 (ML-KEM)**: Post-quantum key encapsulation available
- **FIPS 204 (ML-DSA)**: Post-quantum digital signatures available
- **NIST SP 800-132**: Key derivation via Argon2id with appropriate parameters
