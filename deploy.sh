#!/bin/bash
set -e

echo "Starting deployment process..."

# 1. Fetch the latest code (No Vim, No Merges!)
echo "Fetching latest code from git..."
/usr/bin/git fetch origin

# 2. Activate virtual environment if available
VENV_ACTIVATE="/home/$USER/.virtualenvs/dev-venv/bin/activate"
if [ -f "$VENV_ACTIVATE" ]; then
    echo "Activating virtual environment..."
    source "$VENV_ACTIVATE"
fi

# 3. Detect Environment and Deploy
if [ "$USER" == "slhop" ]; then
    echo "Staging Environment Detected (slhop)..."
    /usr/bin/git reset --hard origin/develop
    echo "Running database migrations..."
    if [ -f "/home/$USER/.virtualenvs/dev-venv/bin/flask" ]; then
        /home/$USER/.virtualenvs/dev-venv/bin/flask db upgrade
    else
        flask db upgrade
    fi
    echo "Reloading Staging web workers..."
    touch /var/www/slhop_pythonanywhere_com_wsgi.py

elif [ "$USER" == "syabiladham" ]; then
    echo "Production Environment Detected (syabiladham)..."
    /usr/bin/git reset --hard origin/main
    echo "Running database migrations..."
    if [ -f "/home/$USER/.virtualenvs/dev-venv/bin/flask" ]; then
        /home/$USER/.virtualenvs/dev-venv/bin/flask db upgrade
    else
        flask db upgrade
    fi
    echo "Reloading Production web workers..."
    touch /var/www/syabiladham_pythonanywhere_com_wsgi.py

else
    echo "Unknown environment! Deployment aborted."
    exit 1
fi

echo "Deployment complete!"
