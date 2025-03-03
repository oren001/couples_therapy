#!/bin/bash

# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and required system packages
sudo apt-get install -y python3-pip python3-venv nginx supervisor

# Create application directory
sudo mkdir -p /var/www/couples-therapy
sudo chown -R $USER:$USER /var/www/couples-therapy

# Create and activate virtual environment
python3 -m venv /var/www/couples-therapy/venv
source /var/www/couples-therapy/venv/bin/activate

# Install Python packages
pip install -r backend/requirements.txt

# Create supervisor configuration
sudo tee /etc/supervisor/conf.d/couples-therapy.conf << EOF
[program:couples-therapy]
directory=/var/www/couples-therapy
command=/var/www/couples-therapy/venv/bin/gunicorn server:app -w 4 -b 127.0.0.1:8000
user=$USER
autostart=true
autorestart=true
stderr_logfile=/var/log/couples-therapy/err.log
stdout_logfile=/var/log/couples-therapy/out.log
EOF

# Create log directory
sudo mkdir -p /var/log/couples-therapy
sudo chown -R $USER:$USER /var/log/couples-therapy

# Create nginx configuration
sudo tee /etc/nginx/sites-available/couples-therapy << EOF
server {
    listen 80;
    server_name 146.190.123.233;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable nginx site
sudo ln -s /etc/nginx/sites-available/couples-therapy /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Restart services
sudo systemctl restart supervisor
sudo systemctl restart nginx 