#!/bin/bash
# Production deployment script

echo "Setting up BookIt API for production..."

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+ if not available
echo "Installing Python..."
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Install PostgreSQL
echo "Installing PostgreSQL..."
sudo apt install postgresql postgresql-contrib -y

# Create database and user
echo "Setting up database..."
sudo -u postgres psql -c "CREATE DATABASE bookit;"
sudo -u postgres psql -c "CREATE USER bookit_user WITH PASSWORD 'secure_production_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE bookit TO bookit_user;"

# Clone repository (replace with your actual repo URL)
echo "Cloning repository..."
git clone https://github.com/yourusername/BookIt.git
cd BookIt

# Create virtual environment
echo "Setting up Python environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment variables
echo "Setting up environment variables..."
cat > .env << EOF
DATABASE_URL=postgresql://bookit_user:secure_production_password@localhost:5432/bookit
JWT_SECRET=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/bookit.service > /dev/null << EOF
[Unit]
Description=BookIt API
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "Starting BookIt service..."
sudo systemctl daemon-reload
sudo systemctl enable bookit
sudo systemctl start bookit

# Install and configure Nginx
echo "Installing Nginx..."
sudo apt install nginx -y

# Configure Nginx
sudo tee /etc/nginx/sites-available/bookit > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/bookit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Install SSL certificate (optional)
echo "Installing SSL certificate..."
sudo apt install certbot python3-certbot-nginx -y
# sudo certbot --nginx -d your-domain.com

echo "BookIt API deployment complete!"
echo "API available at: http://your-domain.com"
echo "Documentation: http://your-domain.com/docs"