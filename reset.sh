#!/bin/bash
# Reset Secure Calendar - securely erases the encrypted database
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_PATH="$SCRIPT_DIR/calendar_secure.db"

if [ ! -f "$DB_PATH" ]; then
    echo "No database found. Nothing to reset."
    exit 0
fi

echo "WARNING: This will permanently destroy all calendar data."
read -p "Are you sure? (type YES to confirm): " confirm

if [ "$confirm" != "YES" ]; then
    echo "Aborted."
    exit 1
fi

# Secure erase: 3 random passes + 5 zero passes
SIZE=$(stat -c%s "$DB_PATH")
echo "Securely erasing database ($SIZE bytes)..."

for i in 1 2 3; do
    dd if=/dev/urandom of="$DB_PATH" bs="$SIZE" count=1 conv=notrunc status=none 2>/dev/null
    echo "  Random pass $i/3 complete"
done

for i in 1 2 3 4 5; do
    dd if=/dev/zero of="$DB_PATH" bs="$SIZE" count=1 conv=notrunc status=none 2>/dev/null
    echo "  Zero pass $i/5 complete"
done

rm "$DB_PATH"
echo "Database securely erased and removed."
echo "Run ./run.sh to create a new database with a fresh passphrase."
