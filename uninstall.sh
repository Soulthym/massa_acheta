#!/usr/bin/env bash

APPDIR="$HOME/apps"
mkdir -p $APPDIR &> /dev/null
DESTDIR="$APPDIR/massa_acheta"

echo "MASSA Acheta uninstall service"
sudo echo

sudo systemctl stop massa_acheta.service &> /dev/null
sudo systemctl disable massa_acheta.service &> /dev/null

rm -rf "$DEST_DIR" &> /dev/null

sudo rm /etc/systemd/system/massa_acheta.service &> /dev/null
sudo systemctl daemon-reload &> /dev/null

echo
echo "MASSA Acheta service uninstalled!"
echo
