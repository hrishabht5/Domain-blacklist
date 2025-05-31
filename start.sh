#!/bin/bash

# Install Firefox ESR and Geckodriver at runtime
apt-get update
apt-get install -y firefox-esr wget tar

wget https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-linux64.tar.gz
tar -xzf geckodriver-linux64.tar.gz
mv geckodriver /usr/bin/geckodriver
chmod +x /usr/bin/geckodriver
rm geckodriver-linux64.tar.gz

# Start the Flask app with Gunicorn
gunicorn app:app --bind 0.0.0.0:10000

