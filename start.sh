#!/bin/bash

# Runtime install of Firefox and Geckodriver
apt-get update
apt-get install -y firefox-esr wget tar

wget https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-linux64.tar.gz
tar -xzf geckodriver-linux64.tar.gz
mv geckodriver /usr/bin/geckodriver
chmod +x /usr/bin/geckodriver
rm geckodriver-linux64.tar.gz

# Start app
gunicorn app:app --bind 0.0.0.0:10000
