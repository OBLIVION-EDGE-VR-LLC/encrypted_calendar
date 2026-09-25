# Secure Calendar - Quickstart

## Prerequisites

- Python 3.12+
- Linux x86_64
- Build tools: `gcc`, `make`, `autoconf`, `libtool`
- System packages: `libffi-dev`, `libssl-dev`, `tcl-dev`

## 1. Build Dependencies

Compile the bundled OpenSSL 3.5.0 (with post-quantum support) and SQLCipher:

```bash
./includes/build_deps.sh
```

This will take 10-15 minutes on first run. Subsequent runs skip already-built libraries.

**What gets built:**
- OpenSSL 3.5.0 with ML-KEM (FIPS 203) and ML-DSA (FIPS 204) enabled
- SQLCipher linked against the local OpenSSL for AES-256 database encryption

## 2. Install Python Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Run the Application

```bash
python -m Calendar
```

On first launch you will be prompted to **create a passphrase**. This passphrase derives the AES-256 encryption key for your database via Argon2id. There is no recovery mechanism — if you forget the passphrase, the data is unrecoverable.

On subsequent launches, enter your passphrase to unlock. You get 3 attempts before lockout.

## 4. Run Tests

```bash
pytest tests/ -v
```

## Security Features

| Feature | Implementation |
|---------|---------------|
| Encryption at rest | SQLCipher (AES-256) via `./includes/` |
| Key derivation | Argon2id (time=3, memory=64MB, parallelism=4) |
| Secure RAM wipe | 3 random passes + 5 zero passes + OPENSSL_cleanse barrier |
| Swap protection | mlock on all buffers holding decrypted data |
| Wipe triggers | Every form clear, date navigation, event deletion, app close |
| Post-quantum | OpenSSL 3.5 with ML-KEM/ML-DSA available |

## Architecture

```
User passphrase
    |
    v
Argon2id KDF --> 256-bit key --> SQLCipher (encrypted .db on disk)
                                      |
                                      v
                              mlock'd SecureString buffers (RAM)
                                      |
                                      v
                              PyQt5 UI display
                                      |
                              (on navigate/close)
                                      v
                              8-pass secure wipe
```

## File Layout

```
Calendar/
├── Model/
│   ├── SecureMemoryManager.py   # mlock, secure_wipe, SecureString
│   ├── SecureDatabase.py        # SQLCipher wrapper, Argon2id KDF
│   └── MalWarePlanner.py        # Calendar widget with DB + wipe integration
├── Views/
│   ├── MainWindow.py            # Passphrase dialog, closeEvent handler
│   └── LandingPage.py           # UI layout
├── Controllers/
│   └── OperationCalendarConnector.py
└── __main__.py

includes/
├── openssl-3.5.0/               # OpenSSL source + compiled output in dist/
├── sqlcipher/                   # SQLCipher source + compiled .libs/
└── build_deps.sh                # Master build script

tests/
├── test_secure_memory.py
├── test_secure_database.py
└── test_integration.py
```

## NIST Compliance

- **SP 800-131A**: AES-256 encryption at rest
- **SP 800-88**: Multi-pass secure erase (3 random + 5 zero)
- **SP 800-132**: Key derivation via Argon2id
- **FIPS 203**: ML-KEM post-quantum key encapsulation (available)
- **FIPS 204**: ML-DSA post-quantum digital signatures (available)

## Troubleshooting

**"No libcrypto found"** — Run `./includes/build_deps.sh` to compile OpenSSL.

**Passphrase rejected on existing database** — The passphrase must match exactly. There is no reset mechanism by design.

**mlock fails (EPERM)** — Your user may need elevated `RLIMIT_MEMLOCK`. Add to `/etc/security/limits.conf`:
```
youruser  hard  memlock  unlimited
```

**SQLCipher not detected** — The app falls back to unencrypted sqlite3 if `./includes/sqlcipher/.libs/libsqlcipher.so` does not exist. Build it with `./includes/build_deps.sh`.
