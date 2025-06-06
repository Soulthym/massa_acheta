#!/usr/bin/env bash

APPDIR="$HOME/apps"
mkdir -p $APPDIR &> /dev/null
DESTDIR="$APPDIR/massa_acheta"

function rollback {
    sudo systemctl stop massa_acheta.service &> /dev/null
    sudo systemctl disable massa_acheta.service &> /dev/null

    rm -rf $DESTDIR &> /dev/null

    sudo rm /etc/systemd/system/massa_acheta.service &> /dev/null
    sudo systemctl daemon-reload &> /dev/null
}



# Check OS distro
hostnamectl | grep -i "ubuntu" > /dev/null
if [[ $? -ne 0 ]]
then
    echo
    echo "Error: this installation uses Ubuntu-compatible commands and cannot be used in other Linux distros."
    echo "You can try to install service manually using this scenario: https://github.com/Soulthym/massa_acheta/"
    popd &> /dev/null
    exit 1
fi



pushd $APPDIR &> /dev/null
clear
echo
echo "::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
echo "::'##::::'##::::'###:::::'######:::'######:::::'###:::::"
echo ":::###::'###:::'## ##:::'##... ##:'##... ##:::'## ##::::"
echo ":::####'####::'##:. ##:: ##:::..:: ##:::..:::'##:. ##:::"
echo ":::## ### ##:'##:::. ##:. ######::. ######::'##:::. ##::"
echo ":::##. #: ##: #########::..... ##::..... ##: #########::"
echo ":::##:.:: ##: ##.... ##:'##::: ##:'##::: ##: ##.... ##::"
echo ":::##:::: ##: ##:::: ##:. ######::. ######:: ##:::: ##::"
echo "::..:::::..::..:::::..:::......::::......:::..:::::..:::"
echo "::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
echo
echo "[ MASSA 🦗 Acheta Telebot ] -- https://github.com/Soulthym/massa_acheta/"
echo
echo "This script will configure your system and install all neccessary software:"
echo "  - python3"
echo "  - python3-venv"
echo "  - python3-pip"
echo "  - git"
echo
echo "New Python virtual environment will be deployed in '$DESTDIR' and new systemd unit 'massa_acheta.service' will be created."
echo -n "If you are ok with this please hit Enter, otherwise Ctrl+C to quit the installation... "
read _
sudo echo



echo -n " → Ready to update your repository and install all packages. Press Enter to continue... "
read _
echo

sudo apt-get update
if [[ $? -eq 0 ]]
then
    echo "✅ Updating finished!"
    echo
else
    echo
    echo "‼ Some error occured. Please check your settings."
    popd &> /dev/null
    exit 1
fi

sudo apt-get -y install git python3 python3-venv python3-pip
if [[ $? -eq 0 ]]
then
    echo "✅ All dependecies installed!"
    echo
else
    echo
    echo "‼ Some error occured. Please check your settings."
    popd &> /dev/null
    exit 1
fi




echo -n " → Ready to clone repo to download service software. Press Enter to continue... "
read _
echo

git clone https://github.com/Soulthym/massa_acheta.git
if [[ $? -eq 0 ]]
then
    echo "✅ Repo cloned successfully!"
    echo
else
    echo
    echo "‼ Some error occured. Please check your settings."
    rollback
    popd &> /dev/null
    exit 1
fi




echo -n " →  Ready to create and configure Python virtual environment. Press Enter to continue... "
read _
echo

echo -n "Creating Python venv in $DESTDIR... "
cd $DESTDIR && python3 -m venv .
if [[ $? -eq 0 ]]
then
    echo "Done!"
else
    echo
    echo "‼ Some error occured. Please check your settings."
    rollback
    popd &> /dev/null
    exit 1
fi

source ./bin/activate && ./bin/pip3 install pip --upgrade && ./bin/pip3 install -r ./requirements.txt
if [[ $? -eq 0 ]]
then
    echo "✅ Python virtual environment created and configured successfully!"
    echo
else
    echo
    echo "‼ Some error occured. Please check your settings."
    rollback
    popd &> /dev/null
    exit 1
fi



echo -n " →  Ready to create systemd unit. Press Enter to continue... "
read _
echo

./service.sh
if [[ $? -eq 0 ]]
then
    echo "✅ Service daemon configured successfully!"
    echo
else
    echo
    echo "‼ Some error occured. Please check your settings."
    rollback
    popd &> /dev/null
    exit 1
fi



echo -n " →  Ready to configure your Telegram bot. Press Enter to continue... "
read _
echo

./setkey.sh
if [[ $? -eq 0 ]]
then
    echo "✅ Telegram bot configured successfully!"
    echo
else
    echo
    echo "‼ Some error occured. Please check your settings."
    rollback
    popd &> /dev/null
    exit 1
fi



echo -n " →  Ready to start and enable the service. Press Enter to continue... "
read _

sudo systemctl start massa_acheta.service
if [[ $? -eq 0 ]]
then
    echo "✅ Service started successfully!"
else
    echo
    echo "‼ Some error occured. Please check your settings."
    rollback
    popd &> /dev/null
    exit 1
fi

sudo systemctl enable massa_acheta.service
if [[ $? -eq 0 ]]
then
    echo "✅ Service enabled successfully!"
    echo
else
    echo
    echo "‼ Some error occured. Please check your settings."
    rollback
    popd &> /dev/null
    exit 1
fi

echo "✅ Installation done!"
echo
echo -n "Press Enter to continue... "
read _


clear
echo
echo
echo "Please note if you watch remote MASSA node you MUST open firewall on your MASSA node host."
echo "You can do it with command 'sudo ufw allow 33035/tcp'. If your firewall is closed for 33035/tcp port - your node will be unavailable for monitoring service."
echo "You don't need to open firewall if you watch localhost (127.0.0.1)."
echo
echo "More information here: https://github.com/Soulthym/massa_acheta/"
echo
