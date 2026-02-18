#!/bin/bash
# Fix Kali Linux Repository URLs
# Run with: sudo bash fix_kali_sources.sh

set -e

echo "🔧 Fixing Kali Linux Repository Sources..."
echo ""

# Function to update sources file
update_sources_file() {
    local file=$1
    if [ -f "$file" ]; then
        echo "Updating $file..."
        # Replace http://http.kali.org with https://kali.download
        sed -i 's|http://http\.kali\.org/kali|https://kali.download/kali|g' "$file"
        sed -i 's|http://kali\.download/kali|https://kali.download/kali|g' "$file"
        echo "✅ Updated $file"
        return 0
    fi
    return 1
}

# Update sources.list
if update_sources_file /etc/apt/sources.list; then
    echo ""
fi

# Update sources.list.d files
if [ -d /etc/apt/sources.list.d ]; then
    for file in /etc/apt/sources.list.d/*; do
        if [ -f "$file" ]; then
            update_sources_file "$file"
        fi
    done
fi

echo ""
echo "📋 Updated repository sources:"
grep -h "^deb\|^deb-src" /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null | grep kali | head -3

echo ""
echo "🔑 Adding GPG key..."
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ED65462EC8D5E4C5 2>/dev/null || {
    echo "⚠️  GPG key command failed, trying alternative..."
    wget -q -O - https://archive.kali.org/archive-key.asc | apt-key add - 2>/dev/null || {
        echo "⚠️  Alternative GPG method also failed, but continuing..."
    }
}

echo ""
echo "🔄 Updating package lists..."
apt-get update

echo ""
echo "✅ Repository sources fixed!"
echo ""
if apt-get update 2>&1 | grep -q "GPG error\|not signed"; then
    echo "⚠️  GPG key issue detected. Run this manually:"
    echo "   sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ED65462EC8D5E4C5"
    echo "   sudo apt-get update"
else
    echo "You can now install packages without 404 errors."
fi

