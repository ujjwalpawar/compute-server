#!/bin/bash

# Installing dependencies
sudo apt-get update
sudo apt-get -y install build-essential pkg-config git ruby ant
sudo apt-get -y install autoconf automake zlib1g-dev libtool
sudo apt-get -y install bison byacc flex ccache libffi-dev
if [[ "$*" == "gui" ]]
then
	sudo apt-get -y install openjdk-8-jdk openjdk-8-jre
	sudo update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java
fi
sudo apt-get -y install python-dev python-setuptools python-wxgtk3.0
sudo apt-get -y install python3-dev python3-setuptools python3-pip
sudo apt-get -y install libc6:i386 libncurses5:i386 libstdc++6:i386 lib32z1 libbz2-1.0:i386
sudo apt-get -y install libgtk-3-dev libpulse-dev

if [[ "$*" == "gui" ]]
then
	gem install android-sdk-installer
fi

# Install Python3.7
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get -y install python3.7
alias python=python3

# Install Python dependencies
pip3 install --upgrade pip
pip3 install cython
pip3 install pyyaml
pip3 install xmltodict
pip3 install pyserial
pip3 install virtualenv
pip3 install virtualenvwrapper
pip3 install Jinja2
pip3 install colorama
pip3 install sh==1.12.1

# Download MobileInsight 6.0.0 beta
wget https://github.com/mobile-insight/mobileinsight-core/releases/download/6.0.0-beta/MobileInsight-6.0.0-beta.tar.gz
tar -xvf MobileInsight-6.0.0-beta.tar.gz
cd MobileInsight-6.0.0b0/
if [[ "$*" == "gui" ]]
then
	pip3 install wxpython
else
	sudo sed -i 's/echo "Installing GUI for MobileInsight..."/exit 0\necho "Installing GUI for MobileInsight..."/g' install-ubuntu.sh
fi
./install-ubuntu.sh