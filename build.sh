#!/usr/bin/env bash

# Install Firefox (headless)
apt-get update && apt-get install -y firefox-esr wget bzip2

# Download a known working version of geckodriver
GECKO_VERSION=v0.34.0
wget https://github.com/mozilla/geckodriver/releases/download/$GECKO_VERSION/geckodriver-$GECKO_VERSION-linux64.tar.gz

# Extract and move to a known location
tar -xvzf geckodriver-$GECKO_VERSION-linux64.tar.gz
mv geckodriver /usr/bin/geckodriver
chmod +x /usr/bin/geckodriver

# Clean up
rm geckodriver-$GECKO_VERSION-linux64.tar.gz
