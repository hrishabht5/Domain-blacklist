# Use an official Python base image
FROM python:3.11-slim

# Install Firefox, wget, and other dependencies
RUN apt-get update && \
    apt-get install -y firefox-esr wget gnupg2 libdbus-glib-1-2 libgtk-3-0 libxt6 libxrender1 libx11-xcb1 libxcomposite1 libasound2 xvfb && \
    rm -rf /var/lib/apt/lists/*

# Install geckodriver (version 0.33.0)
ENV GECKODRIVER_VERSION=v0.33.0
RUN wget -qO- https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz | tar xz -C /usr/local/bin

# Create app directory
WORKDIR /app

# Copy requirements file and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port 10000 (matches your gunicorn bind)
EXPOSE 10000

# Run gunicorn with your Flask app binding to port 10000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
