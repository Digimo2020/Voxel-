#!/usr/bin/env bash
# Voxel - Build Native macOS Application (.app & .dmg)
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=============================================="
echo " Building Voxel for macOS"
echo "=============================================="

# Activate virtual environment if present
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Ensure icns exists
if [ ! -f "assets/icon.icns" ]; then
    echo "Generating assets/icon.icns..."
    python3 -c "
import os, subprocess, sys
from PyQt6.QtWidgets import QApplication
from assets.icons import create_voxel_icon_pixmap
app = QApplication(sys.argv)
# Generate icns
"
fi

echo "Running PyInstaller..."
pyinstaller --noconfirm --windowed \
    --name "Voxel" \
    --icon "assets/icon.icns" \
    --osx-bundle-identifier "com.digimo.voxel" \
    --collect-all edge_tts \
    --collect-all certifi \
    --hidden-import pynput.keyboard._darwin \
    --hidden-import pynput.mouse._darwin \
    main.py

echo "Configuring Info.plist permissions..."
PLIST="dist/Voxel.app/Contents/Info.plist"

if [ -f "$PLIST" ]; then
    /usr/libexec/PlistBuddy -c "Add :NSAccessibilityUsageDescription string 'Voxel requires accessibility permissions to detect text selection across apps.'" "$PLIST" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Set :NSAccessibilityUsageDescription 'Voxel requires accessibility permissions to detect text selection across apps.'" "$PLIST"

    /usr/libexec/PlistBuddy -c "Add :NSAppleEventsUsageDescription string 'Voxel uses system events to read selected text.'" "$PLIST" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Set :NSAppleEventsUsageDescription 'Voxel uses system events to read selected text.'" "$PLIST"

    /usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string 'Voxel'" "$PLIST" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName 'Voxel'" "$PLIST"
fi

# Package DMG if hdiutil is present
if command -v hdiutil &> /dev/null; then
    echo "Creating Voxel.dmg installer..."
    DMG_DIR="dist/dmg_staging"
    rm -rf "$DMG_DIR" dist/Voxel.dmg
    mkdir -p "$DMG_DIR"
    cp -R "dist/Voxel.app" "$DMG_DIR/"
    ln -s /Applications "$DMG_DIR/Applications"
    hdiutil create -volname "Voxel" -srcfolder "$DMG_DIR" -ov -format UDZO "dist/Voxel.dmg"
    rm -rf "$DMG_DIR"
    echo "=============================================="
    echo " SUCCESS: dist/Voxel.app & dist/Voxel.dmg created!"
    echo "=============================================="
else
    echo "=============================================="
    echo " SUCCESS: dist/Voxel.app created!"
    echo "=============================================="
fi
