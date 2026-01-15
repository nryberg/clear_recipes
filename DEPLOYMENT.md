# Deployment Guide

## Auto-Start on Boot

The application is configured to automatically start when the server reboots using systemd.

### How It Works

1. **Systemd Service File** (`clear-recipes.service`)
   - Defines the service configuration
   - Sets working directory and Python path
   - Configures automatic restart on failure
   - Enables start on boot

2. **Deployment Script** (`deploy.sh`)
   - Copies files to the server
   - Installs the systemd service
   - Enables the service for auto-start
   - Starts the service immediately

### Deployment

Run the deployment script:
```bash
./deploy.sh
```

The script will:
- Sync all files to framboise
- Set up Python virtual environment
- Install dependencies
- Install and enable the systemd service
- Start the application

### Service Management

**View logs (live):**
```bash
ssh nick@framboise 'sudo journalctl -u clear-recipes -f'
```

**View recent logs:**
```bash
ssh nick@framboise 'sudo journalctl -u clear-recipes -n 50'
```

**Check status:**
```bash
ssh nick@framboise 'sudo systemctl status clear-recipes'
```

**Stop service:**
```bash
ssh nick@framboise 'sudo systemctl stop clear-recipes'
```

**Start service:**
```bash
ssh nick@framboise 'sudo systemctl start clear-recipes'
```

**Restart service:**
```bash
ssh nick@framboise 'sudo systemctl restart clear-recipes'
```

**Disable auto-start:**
```bash
ssh nick@framboise 'sudo systemctl disable clear-recipes'
```

**Re-enable auto-start:**
```bash
ssh nick@framboise 'sudo systemctl enable clear-recipes'
```

### Manual Service Installation

If you need to manually install the service:

1. Copy service file:
```bash
sudo cp clear-recipes.service /etc/systemd/system/
```

2. Reload systemd:
```bash
sudo systemctl daemon-reload
```

3. Enable service:
```bash
sudo systemctl enable clear-recipes
```

4. Start service:
```bash
sudo systemctl start clear-recipes
```

### Troubleshooting

**Service won't start:**
```bash
# Check logs for errors
sudo journalctl -u clear-recipes -n 50 --no-pager

# Check service status
sudo systemctl status clear-recipes

# Test running manually
cd /home/nick/clear_recipes
source venv/bin/activate
python app.py --port 8080
```

**Service starts but crashes:**
```bash
# View recent crash logs
sudo journalctl -u clear-recipes -n 100 --no-pager

# Check Python dependencies
cd /home/nick/clear_recipes
source venv/bin/activate
pip list
```

**Port already in use:**
```bash
# Check what's using port 8080
sudo lsof -i :8080

# Kill the process if needed
sudo kill <PID>
```

### Configuration

To change the port or other settings:

1. Edit `clear-recipes.service`:
```bash
sudo nano /etc/systemd/system/clear-recipes.service
```

2. Update the `ExecStart` line to change the port:
```
ExecStart=/home/nick/clear_recipes/venv/bin/python /home/nick/clear_recipes/app.py --port 9000
```

3. Reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart clear-recipes
```

## Security Notes

- The service runs as user `nick` (not root) for security
- Logs are stored in systemd journal (use `journalctl` to view)
- The service automatically restarts if it crashes
- Startup is delayed until network is available (`After=network.target`)
