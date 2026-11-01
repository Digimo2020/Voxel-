#!/usr/bin/env bash
# build_mac.sh (v1.1) - [2026-10-31]
# Build the Voxel macOS application and drag-and-drop DMG only.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=============================================="
echo " Building Voxel for macOS (.app and .dmg)"
echo "=============================================="

export PYINSTALLER_CONFIG_DIR="$DIR/.pyinstaller_cache"
mkdir -p "$PYINSTALLER_CONFIG_DIR"

if [[ -d ".venv" ]]; then
    # shellcheck disable=SC1091
    source ".venv/bin/activate"
fi

VERSION="$(python3 -c 'from src.utils.version import CURRENT_VERSION; print(CURRENT_VERSION)')"
DMG_PATH="dist/Voxel.dmg"
VERSIONED_DMG="dist/Voxel-${VERSION}.dmg"
DMG_DIR="dist/dmg_staging"

mkdir -p dist
rm -rf "dist/Voxel.app" "$DMG_PATH" "$VERSIONED_DMG" "$DMG_DIR"

echo "1. Building Voxel.app with PyInstaller..."
pyinstaller --noconfirm --windowed \
    --name "Voxel" \
    --icon "assets/icon.icns" \
    --osx-bundle-identifier "com.digimo.voxel" \
    --collect-all edge_tts \
    --collect-all certifi \
    --collect-all pypdf \
    --add-data "assets:assets" \
    --hidden-import pynput.keyboard._darwin \
    --hidden-import pynput.mouse._darwin \
    main.py

APP_PATH="dist/Voxel.app"
PLIST="$APP_PATH/Contents/Info.plist"

if [[ ! -d "$APP_PATH" || ! -f "$PLIST" ]]; then
    echo "ERROR: PyInstaller did not create a valid Voxel.app bundle." >&2
    exit 1
fi

echo "2. Configuring macOS privacy descriptions and app resources..."
/usr/libexec/PlistBuddy -c "Add :NSAccessibilityUsageDescription string 'Voxel requires Accessibility permission to detect selected text across apps.'" "$PLIST" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Set :NSAccessibilityUsageDescription 'Voxel requires Accessibility permission to detect selected text across apps.'" "$PLIST"

/usr/libexec/PlistBuddy -c "Add :NSAppleEventsUsageDescription string 'Voxel uses system events to read selected text.'" "$PLIST" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Set :NSAppleEventsUsageDescription 'Voxel uses system events to read selected text.'" "$PLIST"

/usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string 'Voxel'" "$PLIST" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName 'Voxel'" "$PLIST"

mkdir -p "$APP_PATH/Contents/Resources/screenshots"
cp assets/branding/*.png "$APP_PATH/Contents/Resources/screenshots/" 2>/dev/null || true
cp assets/voxel_mac_preview.png "$APP_PATH/Contents/Resources/screenshots/" 2>/dev/null || true

echo "3. Applying an ad-hoc code signature for local bundle integrity checks..."
# This is NOT a Developer ID signature and does NOT make the app notarised.
# Gatekeeper may still ask users to approve the app on first launch.
codesign --force --deep --sign - "$APP_PATH"
codesign --verify --deep --strict --verbose=2 "$APP_PATH"

if ! command -v hdiutil >/dev/null 2>&1; then
    echo "ERROR: hdiutil is required to create the macOS disk image." >&2
    exit 1
fi

echo "4. Creating the drag-and-drop DMG..."
mkdir -p "$DMG_DIR"
cp -R "$APP_PATH" "$DMG_DIR/"
ln -s /Applications "$DMG_DIR/Applications"

cat > "$DMG_DIR/READ ME - First Launch.txt" <<'EOF'
VOXEL FOR macOS

INSTALL
1. Drag Voxel.app into the Applications shortcut.
2. Eject the Voxel disk image.
3. Open Applications and try to launch Voxel.

FIRST-LAUNCH SECURITY NOTICE
This build is not signed with an Apple Developer ID certificate and has not
been notarised by Apple. macOS may therefore show a warning that Apple cannot
verify the app for malicious software. This warning is about the app's
distribution status; it is not a malware scan result.

Only continue if you downloaded this DMG from the official Digimo Voxel
GitHub Releases page and trust the source.

To approve the first launch:
1. Try opening Voxel once.
2. Open System Settings > Privacy & Security.
3. Find the Voxel security message and choose Open Anyway.
4. Confirm Open in the next prompt.

Do not disable Gatekeeper globally or run scripts that remove quarantine
attributes. If macOS reports that the app is damaged or its contents changed,
stop and download a fresh copy from the official release page.
EOF

hdiutil create -volname "Voxel" -srcfolder "$DMG_DIR" -ov -format UDZO "$DMG_PATH"
hdiutil verify "$DMG_PATH"
rm -rf "$DMG_DIR"

cp "$DMG_PATH" "$VERSIONED_DMG"
(
    cd dist
    shasum -a 256 "Voxel.dmg" "Voxel-${VERSION}.dmg" > "SHA256SUMS.txt"
)

echo "=============================================="
echo " BUILD COMPLETE!"
echo " - macOS Application : $APP_PATH"
echo " - Drag-and-Drop DMG: $DMG_PATH"
echo " - Versioned DMG    : $VERSIONED_DMG"
echo " - SHA-256 checksums: dist/SHA256SUMS.txt"
echo "=============================================="
