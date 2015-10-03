#!/usr/bin/env bash

# MUST COME BEFORE ANY INSTALLS
apt-get -y update

# Ubuntu desktop
apt-get -y install ubuntu-desktop

# Java
apt-get -y install openjdk-7-jre

# Game dependencies
apt-get -y install git
apt-get -y install python-pygame

# Desktop + Editors/IDEs
apt-get -y install vim
apt-get -y install emacs
apt-get -y install eclipse-platform

# Useful dev tools
apt-get -y install python-pip
pip install flake8

# Game itself
mkdir ~/Desktop/mm21 && cd ~/Desktop/mm21
git clone https://github.com/acm-uiuc/mm21

# Go!
startx
