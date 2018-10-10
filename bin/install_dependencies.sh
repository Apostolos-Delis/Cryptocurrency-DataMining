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
