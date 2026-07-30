#!/bin/bash
set -euo pipefail

VERSION="${1:-0.1.0}"
BINARY="${2:-dist/md2tex-linux}"
ICON_DIR="installer/icons"

PKG_NAME="md2tex_${VERSION}_amd64"
PKG_DIR="/tmp/${PKG_NAME}"

rm -rf "$PKG_DIR"
mkdir -p "$PKG_DIR/DEBIAN"
mkdir -p "$PKG_DIR/usr/bin"
mkdir -p "$PKG_DIR/usr/share/applications"
mkdir -p "$PKG_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$PKG_DIR/usr/share/icons/hicolor/64x64/apps"
mkdir -p "$PKG_DIR/usr/share/icons/hicolor/48x48/apps"
mkdir -p "$PKG_DIR/usr/share/icons/hicolor/32x32/apps"

cat > "$PKG_DIR/DEBIAN/control" <<EOF
Package: md2tex
Version: ${VERSION}
Section: text
Priority: optional
Architecture: amd64
Maintainer: Rafael Reyes <rafaelreyes0816@gmail.com>
Description: md2tex — Markdown to LaTeX converter
 Converts Markdown files into compilable LaTeX documents
 with automatic image handling, templates, and more.
 .
 Includes both GUI and CLI interfaces.
EOF

cat > "$PKG_DIR/DEBIAN/postinst" <<EOF
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications 2>/dev/null || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache /usr/share/icons/hicolor 2>/dev/null || true
fi
exit 0
EOF
chmod 755 "$PKG_DIR/DEBIAN/postinst"

install -m 755 "$BINARY" "$PKG_DIR/usr/bin/md2tex"

cat > "$PKG_DIR/usr/share/applications/md2tex.desktop" <<EOF
[Desktop Entry]
Name=md2tex
Comment=Markdown to LaTeX converter
Exec=md2tex
Icon=md2tex
Terminal=false
Type=Application
Categories=Office;TextEditor;Utility;
StartupNotify=true
EOF

for size in 256 64 48 32; do
    cp "${ICON_DIR}/${size}.png" "${PKG_DIR}/usr/share/icons/hicolor/${size}x${size}/apps/md2tex.png"
done

dpkg-deb --build "$PKG_DIR" "dist/${PKG_NAME}.deb"
rm -rf "$PKG_DIR"
echo "✅ dist/${PKG_NAME}.deb"
