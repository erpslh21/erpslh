#!/bin/bash
set -e

echo "Starting deployment process..."

# 1. Pull the latest code from git
echo "Pulling latest code from git..."
/usr/bin/git pull origin main

# 2. Apply database migrations
echo "Running database migrations..."
flask db upgrade

# 3. Reload the web workers securely by touching the WSGI file
echo "Reloading web workers..."
touch /var/www/syabiladham_pythonanywhere_com_wsgi.py

echo "Deployment complete!"
