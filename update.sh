#!/usr/bin/env bash

APPDIR="$HOME/apps"
mkdir -p $APPDIR &> /dev/null
DESTDIR="$APPDIR/massa_acheta"

echo "MASSA Acheta update service"
sudo echo

sudo systemctl stop massa_acheta.service
if [[ $? -eq 0 ]]
then
    echo "✅ Service stopped"
else
    echo
    echo "‼ Some error occured. Please check your settings."
    popd &> /dev/null
    exit 1
fi

pushd $DESTDIR &> /dev/null
if [[ $? -eq 0 ]]
then
    echo "✅ Ready to update"
    rm ./app_stat.json &> /dev/null
else
    echo
    echo "‼ Some error occured. Please check your settings."
    popd &> /dev/null
    exit 1
fi

source ./bin/activate
git pull && ./bin/pip3 install -r ./requirements.txt
if [[ $? -eq 0 ]]
then
    echo "✅ Service updated"
else
    echo
    echo "‼ Some error occured. Please check your settings."
    popd &> /dev/null
    exit 1
fi

sudo systemctl start massa_acheta.service
if [[ $? -eq 0 ]]
then
    echo "✅ Service started"
    echo
else
    echo
    echo "‼ Some error occured. Please check your settings."
    popd &> /dev/null
    exit 1
fi

popd &> /dev/null
exit 0
