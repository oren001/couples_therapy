#!/bin/bash

set -e  # Exit on any error

echo "Starting deployment process..."

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and required system packages
echo "Installing required packages..."
sudo apt-get install -y python3-pip python3-venv nginx supervisor

# Create application directory
echo "Setting up application directory..."
sudo mkdir -p /var/www/couples-therapy
sudo chown -R $USER:$USER /var/www/couples-therapy

# Create and activate virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv /var/www/couples-therapy/venv
source /var/www/couples-therapy/venv/bin/activate

# Install Python packages
echo "Installing Python dependencies..."
cd /var/www/couples-therapy
pip install -r backend/requirements.txt

# Create supervisor configuration
echo "Configuring supervisor..."
sudo tee /etc/supervisor/conf.d/couples-therapy.conf << EOF
[program:couples-therapy]
directory=/var/www/couples-therapy/backend
command=/var/www/couples-therapy/venv/bin/gunicorn server:app -w 4 -b 127.0.0.1:8000
user=$USER
autostart=true
autorestart=true
stderr_logfile=/var/log/couples-therapy/err.log
stdout_logfile=/var/log/couples-therapy/out.log
EOF

# Create log directory
echo "Setting up log directory..."
sudo mkdir -p /var/log/couples-therapy
sudo chown -R $USER:$USER /var/log/couples-therapy

# Create nginx configuration
echo "Configuring nginx..."
sudo tee /etc/nginx/sites-available/couples-therapy << EOF
server {
    listen 80;
    server_name 146.190.123.233;

    location / {
        root /var/www/couples-therapy/frontend;
        index simple-test.html advanced-test.html;
        try_files \$uri \$uri/ =404;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable nginx site
echo "Enabling nginx site..."
sudo ln -sf /etc/nginx/sites-available/couples-therapy /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
echo "Testing nginx configuration..."
sudo nginx -t

# Restart services
echo "Restarting services..."
sudo systemctl restart supervisor
sudo systemctl restart nginx

# Check services status
echo "Checking services status..."
sudo systemctl status nginx --no-pager
sudo systemctl status supervisor --no-pager
sudo supervisorctl status couples-therapy

echo "Deployment complete! The application should be running at http://146.190.123.233" 