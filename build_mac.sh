#!/usr/bin/env bash
# Voxel - Build Native macOS Application (.app, .dmg & .pkg)
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=============================================="
echo " Building Voxel for macOS (.app, .dmg & .pkg)"
echo "=============================================="

export PYINSTALLER_CONFIG_DIR="$DIR/.pyinstaller_cache"
mkdir -p "$PYINSTALLER_CONFIG_DIR"

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 1. Run PyInstaller
echo "1. Running PyInstaller..."
pyinstaller --noconfirm --windowed \
    --name "Voxel" \
    --icon "assets/icon.icns" \
    --osx-bundle-identifier "com.digimo.voxel" \
    --collect-all edge_tts \
    --collect-all certifi \
    --hidden-import pynput.keyboard._darwin \
    --hidden-import pynput.mouse._darwin \
    main.py

# 2. Configure Info.plist & bundle screenshots
echo "2. Configuring Info.plist & embedding UX design screenshots..."
PLIST="dist/Voxel.app/Contents/Info.plist"

if [ -f "$PLIST" ]; then
    /usr/libexec/PlistBuddy -c "Add :NSAccessibilityUsageDescription string 'Voxel requires accessibility permissions to detect text selection across apps.'" "$PLIST" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Set :NSAccessibilityUsageDescription 'Voxel requires accessibility permissions to detect text selection across apps.'" "$PLIST"

    /usr/libexec/PlistBuddy -c "Add :NSAppleEventsUsageDescription string 'Voxel uses system events to read selected text.'" "$PLIST" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Set :NSAppleEventsUsageDescription 'Voxel uses system events to read selected text.'" "$PLIST"

    /usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string 'Voxel'" "$PLIST" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName 'Voxel'" "$PLIST"
fi

mkdir -p "dist/Voxel.app/Contents/Resources/screenshots"
cp assets/branding/*.png "dist/Voxel.app/Contents/Resources/screenshots/" 2>/dev/null || true
cp assets/voxel_mac_preview.png "dist/Voxel.app/Contents/Resources/screenshots/" 2>/dev/null || true

# 3. Build .pkg installer (targeting /Applications for all users)
echo "3. Building installable .pkg for /Applications..."
PKG_ROOT="build/pkg_root"
PKG_RESOURCES="build/pkg_resources"
mkdir -p "$PKG_ROOT" "$PKG_RESOURCES"

rm -rf "$PKG_ROOT"/*
cp -R "dist/Voxel.app" "$PKG_ROOT/"

# Embed preview image as Base64 into welcome.html
python3 -c "
import base64
with open('assets/voxel_mac_preview.png', 'rb') as f:
    b64_img = base64.b64encode(f.read()).decode('utf-8')

html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset=\"utf-8\">
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif;
    color: #1E293B;
    padding: 14px 20px;
    line-height: 1.45;
  }}
  h1 {{ color: #0084FF; font-size: 22px; margin: 0 0 2px 0; }}
  .tagline {{ color: #64748B; font-size: 11px; font-weight: 700; letter-spacing: 0.8px; margin-bottom: 12px; }}
  .screenshot-box {{
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid rgba(0, 132, 255, 0.35);
    margin: 10px 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  }}
  img {{ width: 100%; height: auto; display: block; }}
  .features {{ font-size: 12px; margin-top: 12px; }}
  .item {{ margin-bottom: 6px; }}
</style>
</head>
<body>
  <h1>🎙 Voxel</h1>
  <div class=\"tagline\">TEXT TO SPEECH, ANYWHERE</div>
  <p>Welcome to <b>Voxel for macOS</b>. This package installs Voxel into your <b>/Applications</b> folder for all users.</p>
  <div class=\"screenshot-box\">
    <img src=\"data:image/png;base64,{b64_img}\" alt=\"Voxel macOS UX Design\">
  </div>
  <div class=\"features\">
    <div class=\"item\">✨ <b>Voice-Reactive Animated Mic</b>: 3 equalizer lines pulse dynamically during speech.</div>
    <div class=\"item\">🫧 <b>Smooth Floating Trigger</b>: Appears near any selected text with fade-in animation.</div>
    <div class=\"item\">💊 <b>Frosted Glass Capsule Player</b>: Slide-up player with glowing play button and speed regulation.</div>
  </div>
</body>
</html>'''

with open('build/pkg_resources/welcome.html', 'w', encoding='utf-8') as f:
    f.write(html)
"

VERSION=$(python3 -c "from src.utils.version import CURRENT_VERSION; print(CURRENT_VERSION)" 2>/dev/null || echo "v1.0.05")
PLAIN_VER="${VERSION#v}"

# Generate Distribution.xml dynamically for productbuild
cat << EOF > build/Distribution.xml
<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="1">
    <title>Voxel</title>
    <welcome file="welcome.html"/>
    <options customize="never" require-scripts="false"/>
    <choices-outline>
        <line choice="default">
            <line choice="com.digimo.voxel.app"/>
        </line>
    </choices-outline>
    <choice id="default"/>
    <choice id="com.digimo.voxel.app" visible="false">
        <pkg-ref id="com.digimo.voxel.app"/>
    </choice>
    <pkg-ref id="com.digimo.voxel.app" version="${PLAIN_VER}" onConclusion="none">VoxelComponent.pkg</pkg-ref>
</installer-gui-script>
EOF

# Component package installed to /Applications
pkgbuild --root "$PKG_ROOT" \
         --identifier "com.digimo.voxel.app" \
         --version "${PLAIN_VER}" \
         --install-location "/Applications" \
         "dist/VoxelComponent.pkg"

# Product installer with Distribution.xml & embedded UX screenshots
productbuild --distribution "build/Distribution.xml" \
             --resources "$PKG_RESOURCES" \
             --package-path "dist" \
             "dist/Voxel.pkg"

rm -f "dist/VoxelComponent.pkg"
rm -rf "$PKG_ROOT"

# 4. Package DMG installer
if command -v hdiutil &> /dev/null; then
    echo "4. Creating Voxel.dmg installer..."
    DMG_DIR="dist/dmg_staging"
    rm -rf "$DMG_DIR" dist/Voxel.dmg
    mkdir -p "$DMG_DIR"
    cp -R "dist/Voxel.app" "$DMG_DIR/"
    ln -s /Applications "$DMG_DIR/Applications"
    hdiutil create -volname "Voxel" -srcfolder "$DMG_DIR" -ov -format UDZO "dist/Voxel.dmg" 2>/dev/null || true
    rm -rf "$DMG_DIR"
fi

VERSION=$(python3 -c "from src.utils.version import CURRENT_VERSION; print(CURRENT_VERSION)" 2>/dev/null || echo "v1.0.05")
cp dist/Voxel.pkg "dist/Voxel-${VERSION}.pkg" 2>/dev/null || true
cp dist/Voxel.dmg "dist/Voxel-${VERSION}.dmg" 2>/dev/null || true

echo "=============================================="
echo " BUILD COMPLETE!"
echo " - Standalone App Bundle : dist/Voxel.app"
echo " - System-wide Installer : dist/Voxel.pkg"
[ -f "dist/Voxel.dmg" ] && echo " - Drag & Drop Disk Image: dist/Voxel.dmg"
echo "=============================================="
