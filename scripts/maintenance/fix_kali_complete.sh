#!/bin/bash
# Complete Kali Linux Repository Fix
# Run with: sudo bash fix_kali_complete.sh

set -e

echo "🔧 Complete Kali Linux Repository Fix"
echo "═══════════════════════════════════════"
echo ""

# Step 1: Fix repository URLs
echo "Step 1: Updating repository URLs..."
if [ -f /etc/apt/sources.list ]; then
    sed -i 's|http://http\.kali\.org/kali|https://kali.download/kali|g' /etc/apt/sources.list
    sed -i 's|http://kali\.download/kali|https://kali.download/kali|g' /etc/apt/sources.list
    echo "✅ Updated /etc/apt/sources.list"
fi

if [ -d /etc/apt/sources.list.d ]; then
    for file in /etc/apt/sources.list.d/*; do
        if [ -f "$file" ]; then
            sed -i 's|http://http\.kali\.org/kali|https://kali.download/kali|g' "$file"
            sed -i 's|http://kali\.download/kali|https://kali.download/kali|g' "$file"
            echo "✅ Updated $(basename $file)"
        fi
    done
fi

# Step 2: Add GPG key
echo ""
echo "Step 2: Adding GPG key..."
echo "Trying method 1: keyserver..."
if apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ED65462EC8D5E4C5 2>/dev/null; then
    echo "✅ GPG key added via keyserver"
else
    echo "Method 1 failed, trying method 2: direct download..."
    if wget -q -O - https://archive.kali.org/archive-key.asc | apt-key add - 2>/dev/null; then
        echo "✅ GPG key added via archive.kali.org"
    else
        echo "Method 2 failed, trying method 3: hkp protocol..."
        if apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys ED65462EC8D5E4C5 2>/dev/null; then
            echo "✅ GPG key added via hkp protocol"
        else
            echo "⚠️  All GPG key methods failed. Trying manual import..."
            # Try downloading and importing manually
            TEMP_KEY=$(mktemp)
            if wget -q -O "$TEMP_KEY" https://archive.kali.org/archive-key.asc 2>/dev/null; then
                apt-key add "$TEMP_KEY" 2>/dev/null && echo "✅ GPG key added via manual import" || echo "⚠️  Manual import also failed"
                rm -f "$TEMP_KEY"
            else
                echo "⚠️  Could not download GPG key. You may need to add it manually."
                echo "   Run: sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ED65462EC8D5E4C5"
            fi
        fi
    fi
fi

# Step 3: Update package lists
echo ""
echo "Step 3: Updating package lists..."
if apt-get update; then
    echo ""
    echo "✅ Package lists updated successfully!"
    echo ""
    echo "Repository fix complete! You can now install packages."
else
    echo ""
    echo "⚠️  Package list update had errors. Checking status..."
    apt-get update 2>&1 | grep -i "gpg\|signed" | head -3 || echo "Update completed with warnings"
    echo ""
    echo "If you still see GPG errors, try:"
    echo "  sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ED65462EC8D5E4C5"
    echo "  sudo apt-get update"
fi

echo ""
echo "═══════════════════════════════════════"
echo "✅ Fix script completed!"
echo ""
echo "Current repository configuration:"
grep -h "^deb\|^deb-src" /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null | grep kali | head -2

