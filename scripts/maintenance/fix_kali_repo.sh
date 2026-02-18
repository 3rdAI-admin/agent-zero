#!/bin/bash
# Fix Kali Linux Repository Issues
# Run with: sudo bash fix_kali_repo.sh

set -e

echo "🔧 Fixing Kali Linux Repository Issues..."
echo ""

# Step 1: Fix GPG Key
echo "Step 1: Adding GPG key..."
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ED65462EC8D5E4C5 || {
    echo "⚠️  GPG key command failed, trying alternative method..."
    wget -q -O - https://archive.kali.org/archive-key.asc | apt-key add - || {
        echo "⚠️  Alternative method also failed, continuing..."
    }
}

# Step 2: Update repository sources
echo ""
echo "Step 2: Updating repository sources..."

if [ -f /etc/apt/sources.list.d/kali.sources ]; then
    echo "Found kali.sources file, updating..."
    sed -i 's|http://http.kali.org/kali|http://kali.download/kali|g' /etc/apt/sources.list.d/kali.sources
    sed -i 's|http://kali.download/kali|https://kali.download/kali|g' /etc/apt/sources.list.d/kali.sources
    echo "✅ Updated kali.sources"
elif [ -f /etc/apt/sources.list ]; then
    echo "Found sources.list file, updating..."
    sed -i 's|http://http.kali.org/kali|http://kali.download/kali|g' /etc/apt/sources.list
    sed -i 's|http://kali.download/kali|https://kali.download/kali|g' /etc/apt/sources.list
    echo "✅ Updated sources.list"
else
    echo "⚠️  No repository configuration files found"
fi

# Step 3: Update package lists
echo ""
echo "Step 3: Updating package lists..."
apt-get update

echo ""
echo "✅ Repository fix complete!"
echo ""
echo "Note: Agent Zero doesn't require Node.js/npm."
echo "These errors were from a system update, not Agent Zero dependencies."

