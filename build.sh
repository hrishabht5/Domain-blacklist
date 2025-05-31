#!/usr/bin/env bash
apt-get update && apt-get install -y firefox-esr wget
wget https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-linux64.tar.gz
tar -xvzf geckodriver-linux64.tar.gz
mv geckodriver /usr/bin/geckodriver
