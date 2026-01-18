# Deploying Clear Recipes on Framboise

## 1. Install nginx

```bash
sudo apt update
sudo apt install nginx
```

## 2. Copy the nginx config

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/recipes
sudo ln -s /etc/nginx/sites-available/recipes /etc/nginx/sites-enabled/
sudo nginx -t  # Test config
sudo systemctl reload nginx
```

## 3. Run the app on port 8080

```bash
# Install dependencies
pip install -r requirements.txt

# Run (in background with nohup, or use systemd)
nohup python app.py --port 8080 &
```

## 4. (Optional) Create a systemd service

Create `/etc/systemd/system/recipes.service`:

```ini
[Unit]
Description=Clear Recipes App
After=network.target

[Service]
User=pi
WorkingDirectory=/path/to/clear_recipes
ExecStart=/usr/bin/python3 app.py --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable recipes
sudo systemctl start recipes
```

## 5. Access the app

- Local: http://framboise
- External: http://recipes.rybergs.com (after DNS setup)
