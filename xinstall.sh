#!/bin/bash

# Ensure the script is run with sudo or as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root or with sudo"
  exit
fi

echo "Starting the X11 Forwarding setup..."

# 1. Update system packages
echo "Updating system packages..."
yum update -y

# 2. Install X11 and necessary utilities
echo "Installing X11 and required utilities..."
yum groupinstall "X Window System" -y
yum install xorg-x11-xauth xorg-x11-apps -y

# 3. Modify SSH configuration to enable X11 Forwarding
echo "Enabling X11 Forwarding in SSH configuration..."
SSH_CONFIG="/etc/ssh/sshd_config"

if grep -q "^X11Forwarding" $SSH_CONFIG; then
  sed -i 's/^X11Forwarding.*/X11Forwarding yes/' $SSH_CONFIG
else
  echo "X11Forwarding yes" >> $SSH_CONFIG
fi

if grep -q "^X11UseLocalhost" $SSH_CONFIG; then
  sed -i 's/^X11UseLocalhost.*/X11UseLocalhost no/' $SSH_CONFIG
else
  echo "X11UseLocalhost no" >> $SSH_CONFIG
fi

# 4. Restart SSH service to apply changes
echo "Restarting SSH service to apply changes..."
systemctl restart sshd

# 5. Verify installation and check if xauth and X11 apps work
echo "Verifying X11 setup by running 'xclock'..."
if command -v xclock &> /dev/null
then
    echo "xclock installed. You can test X11 forwarding by running it after SSH connection."
else
    echo "xclock is not installed properly. Check for issues."
fi

echo "X11 Forwarding setup completed. Please SSH into the server with X11 forwarding enabled (ssh -X opc@129.146.166.207) and test with 'xclock'."
