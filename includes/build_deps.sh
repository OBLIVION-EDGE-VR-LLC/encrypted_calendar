#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Building OpenSSL 3.5.0 ==="
cd "$SCRIPT_DIR/openssl-3.5.0"
if [ ! -f "dist/lib/libcrypto.so" ]; then
    ./Configure --prefix="$SCRIPT_DIR/openssl-3.5.0/dist" \
        --openssldir="$SCRIPT_DIR/openssl-3.5.0/dist/ssl" \
        enable-ml-kem enable-ml-dsa enable-argon2 \
        shared linux-x86_64
    make -j$(nproc)
    make install_sw
fi

echo "=== Building SQLCipher ==="
cd "$SCRIPT_DIR/sqlcipher"
if [ ! -f ".libs/libsqlcipher.so" ]; then
    ./configure --enable-tempstore=yes \
        CFLAGS="-DSQLITE_HAS_CODEC -I$SCRIPT_DIR/openssl-3.5.0/dist/include" \
        LDFLAGS="-L$SCRIPT_DIR/openssl-3.5.0/dist/lib -lcrypto -lm -lpthread -ldl"
    make -j$(nproc)
fi

echo "=== Build complete ==="
echo "OpenSSL libs: $SCRIPT_DIR/openssl-3.5.0/dist/lib/"
echo "SQLCipher lib: $SCRIPT_DIR/sqlcipher/.libs/libsqlcipher.so"
