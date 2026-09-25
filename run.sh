#!/bin/bash
# Launch Secure Calendar with SQLCipher encryption enabled
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export LD_PRELOAD="$SCRIPT_DIR/includes/sqlcipher/.libs/libsqlcipher.so"
export LD_LIBRARY_PATH="$SCRIPT_DIR/includes/openssl-3.5.0/dist/lib64:$LD_LIBRARY_PATH"

exec python3 -m Calendar "$@"
