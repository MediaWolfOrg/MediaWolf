#!/bin/sh
echo -e "\033[1;32mMedaiWolf\033[0m"
echo "Initializing app..."

puid=${puid:-1000}
pgid=${pgid:-1000}

echo "-----------------"
echo -e "\033[1mRunning with:\033[0m"
echo "puid=${puid}"
echo "pgid=${pgid}"
echo "-----------------"

# Create the required directories with the correct permissions
echo "Setting up directories.."
mkdir -p /config /downloads
chown -R ${puid}:${pgid} /config /downloads

# Start the application with the specified user permissions
echo "Starting MediaWolf..."
exec su-exec ${puid}:${pgid} gunicorn backend.main:app -c /mediawolf/gunicorn_config.py 
