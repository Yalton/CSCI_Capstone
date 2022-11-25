#!/bin/bash
USRBIN=~/.local/bin/

echo "======================================="
echo "[QUADP] Installation Process started..."
echo "======================================="

# Install Required python libraries 
echo "[QUADP] Installing requirements"
pip3 install -r requirements.txt

#Create .local/bin directory in user's home dir if it does not exist
if [ ! -d "$USRBIN" ]; then
    echo "[QUADP] Creating .local/bin dir"
    mkdir $USRBIN
fi

# Create symlink to quadp program if it does not exist
if [ ! -f "$USRBIN/quadp" ]; then
    echo "[QUADP] Removing old symlink"
    rm ~/.local/bin/quadp
fi
echo "[QUADP] Creating symlink to executable"
ln -s quadp ~/.local/bin/quadp
# if [ ! -f "$USRBIN/quadp" ]; then
#     ln -s quadp ~/.local/bin/quadp
# fi

echo "======================================="
echo "[QUADP] Installation Complete!"
echo "======================================="