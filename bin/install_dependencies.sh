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
    read -p "Docker Requires 4 gb to run a sql server. Have your docker preferences allowed for ths much memory? " yn
    case $yn in
        #install microsoft sql server for unix systems
        [Yy]* ) docker pull microsoft/mssql-server-linux; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer y or n.";;
    esac
done


#create an sql server
docker run -d --name sql_server_demo -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=reallyStrongPwd123' -p 1433:1433 microsoft/mssql-server-linuxjkk

command_exists npm

#update npm
npm install npm@latest -g

#install the sql command line interface
npm install -g sql-cli
