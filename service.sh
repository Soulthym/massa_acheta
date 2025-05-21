#!/usr/bin/env bash

APPDIR="$HOME/apps"
mkdir -p $APPDIR &> /dev/null
DESTDIR="$APPDIR/massa_acheta"

pushd $DESTDIR &> /dev/null

echo "MASSA Acheta install service unit"
sudo echo

echo -n "Generating service file... "

echo "
[Unit]
Description=MASSA Acheta
Wants=network.target
After=network.target

[Service]
Type=idle
User=$USER
WorkingDirectory=$DESTDIR
ExecStart=$DESTDIR/bin/python3 main.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
" > ./massa_acheta.service

if [[ $? -eq 0 ]]
then
        echo "Done!"
else
        echo "Error!"
        popd &> /dev/null
        exit 1
fi


echo -n "Copying service file to /etc/systemd/system/massa_acheta.service... "
sudo cp ./massa_acheta.service /etc/systemd/system/massa_acheta.service

if [[ $? -eq 0 ]]
then
        echo "Done!"
else
        echo "Error!"
        popd &> /dev/null
        exit 1
fi


echo -n "Reloading systemd daemon configuration... "
sudo systemctl daemon-reload

if [[ $? -eq 0 ]]
then
        echo "Done!"
else
        echo "Error!"
        popd &> /dev/null
        exit 1
fi

popd &> /dev/null
exit 0
