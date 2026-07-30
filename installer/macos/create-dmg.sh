#!/bin/bash
set -euo pipefail

VERSION="${1:-0.1.0}"
APP_BUNDLE="${2:-dist/md2tex.app}"

DMG_NAME="md2tex-${VERSION}.dmg"
DMG_PATH="dist/${DMG_NAME}"
STAGING_DIR="/tmp/md2tex-dmg-staging"

rm -rf "$STAGING_DIR" "$DMG_PATH"
mkdir -p "$STAGING_DIR"

cp -R "$APP_BUNDLE" "$STAGING_DIR/md2tex.app"

# Symlink to /Applications for drag-and-drop install
ln -s /Applications "$STAGING_DIR/Applications"

# Create DMG
hdiutil create -volname "md2tex ${VERSION}" \
    -srcfolder "$STAGING_DIR" \
    -ov -format UDZO \
    "$DMG_PATH"

rm -rf "$STAGING_DIR"
echo "✅ ${DMG_PATH}"
