#!/bin/bash
echo "=== Starting APK build ==="

# Убедимся что buildozer.spec существует
if [ ! -f "buildozer.spec" ]; then
    echo "Creating buildozer.spec..."
    buildozer init
fi

echo "Cleaning previous builds..."
buildozer android clean

echo "Starting build..."
buildozer android debug

echo "=== Build finished ==="
ls -la bin/ 2>/dev/null || echo "No bin directory found"