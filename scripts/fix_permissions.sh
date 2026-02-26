#!/bin/bash
# Fix file permissions for deployment scripts

echo "Fixing script permissions..."

# Make all shell scripts executable
chmod +x scripts/*.sh
chmod +x backend/run.py
chmod +x scripts/*.py

echo "✅ Permissions fixed"
echo ""
echo "Executable scripts:"
ls -la scripts/*.sh scripts/*.py
