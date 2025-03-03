#!/bin/bash

set -e  # Exit on any error

echo "Starting deployment process..."

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and required system packages
echo "Installing required packages..."
sudo apt-get install -y python3-pip python3-venv nginx supervisor ufw

# Configure firewall
echo "Configuring firewall..."
sudo ufw allow 80/tcp
sudo ufw allow 22/tcp
sudo ufw --force enable

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
environment=PATH="/var/www/couples-therapy/venv/bin"
EOF

# Create log directory
echo "Setting up log directory..."
sudo mkdir -p /var/log/couples-therapy
sudo chown -R $USER:$USER /var/log/couples-therapy

# Create nginx configuration
echo "Configuring nginx..."
sudo tee /etc/nginx/sites-available/couples-therapy << EOF
server {
    listen 80 default_server;
    server_name 146.190.123.233;

    access_log /var/log/nginx/couples-therapy-access.log;
    error_log /var/log/nginx/couples-therapy-error.log;

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
        proxy_read_timeout 90;
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

# Ensure services are enabled
echo "Enabling services..."
sudo systemctl enable nginx
sudo systemctl enable supervisor

# Stop services before restarting
echo "Stopping services..."
sudo systemctl stop nginx
sudo systemctl stop supervisor

# Start services fresh
echo "Starting services..."
sudo systemctl start supervisor
sudo systemctl start nginx

# Check services status
echo "Checking services status..."
echo "Nginx status:"
sudo systemctl status nginx --no-pager
echo "Supervisor status:"
sudo systemctl status supervisor --no-pager
echo "Application status:"
sudo supervisorctl status couples-therapy

# Verify ports are listening
echo "Checking listening ports..."
sudo netstat -tulpn | grep -E ':80|:8000'

echo "Deployment complete! The application should be running at http://146.190.123.233"
echo "To check logs:"
echo "  Nginx error log: sudo tail -f /var/log/nginx/couples-therapy-error.log"
echo "  Application log: tail -f /var/log/couples-therapy/err.log" 