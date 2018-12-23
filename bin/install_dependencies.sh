#!/usr/bin/env bash

#Install the necessary third party python libraries used in this project
#Note: pip is required to be installed.
#To install pip run these commands depending on your operating system
#
#   MacOS: Install homebrew first and then run:
#           sudo brew install python3-pip
#
#   Ubuntu: Run sudo apt-get python3-pip
#   
#   Arch: sudo pacman -S python-pip
#
#   Debian: sudo apt-get python3-pip
#
#   Fedora: sudo dnf install python3

errormsg(){
    >&2 echo -e "\e[31m$1\e[0m"
}

command_exists(){
    command -v $1 >/dev/null 2>&1 || { 
        errormsg "$1 needs to be installed. Aborting."; exit 1; 
    }
}

printf "NOTE: This script will require sudo to run\n"
IFS= read -rsp 'Please your sudo password: ' password

command_exists pip

#Update pip
pip install --upgrade pip

#install the python twitter api
pip install twitter

#install Orator for sql data management
pip install orator

#install lxml
pip install lxml

#install Pyquery
pip install pyquery

command_exists docker

while true; do
    read -p "Docker Requires 4 gb to run a sql server. Have your docker preferences allowed for ths much memory? [Y/n] " yn
    case $yn in
        #install microsoft sql server for unix systems
        [Yy]* ) docker pull microsoft/mssql-server-linux; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer y or n.";;
    esac
done


SERVER=$(docker ps | grep "cryptocurrency_data")
if [[ -z $SERVER ]]
then
    echo -n "Insert a password for sql server: " 
    read -s PASSWORD
    echo
    #create an sql server
    echo "Creating SQL server locally called cryptocurrency_data"
    docker run -d --name cryptocurrency_data -e 'ACCEPT_EULA=Y' -e "SA_PASSWORD=$PASSWORD" -p 1433:1433 microsoft/mssql-server-linux
fi

command_exists npm

#update npm
sudo -S npm install npm@latest -g <<<$password

#install the sql command line interface
sudo -S npm install -g sql-cli <<<$password

