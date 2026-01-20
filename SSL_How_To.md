# SSL/HTTPS Setup with Tailscale

This guide covers how to enable SSL/HTTPS for Clear Recipes using Tailscale. There are two approaches depending on your needs:

1. **Tailscale Funnel** - Expose your service to the public internet with automatic HTTPS (recommended for public access)
2. **Tailscale HTTPS Certificates** - Secure access within your tailnet only

---

## Option 1: Tailscale Funnel (Public Internet Access)

Tailscale Funnel exposes your local service to the public internet with automatic HTTPS certificate management. This is the easiest way to get SSL working.

### Prerequisites

- Tailscale v1.38.3 or later
- A Tailscale account (Personal, Personal Plus, Premium, or Enterprise plan)
- MagicDNS enabled in your tailnet

### Step 1: Enable HTTPS in Your Tailnet

1. Go to the [Tailscale Admin Console](https://login.tailscale.com/admin/dns)
2. Navigate to the **DNS** page
3. Ensure **MagicDNS** is enabled
4. Under **HTTPS Certificates**, click **Enable HTTPS**
5. Acknowledge that machine names will be published in a public Certificate Transparency ledger

> **Note:** Do not enable HTTPS if your machine names contain sensitive information. You can rename machines before enabling.

### Step 2: Configure Funnel

On your server (framboise), run:

```bash
# Expose port 8080 (where your Flask app runs) via Funnel
tailscale funnel 8080
```

This will output something like:

```
Available on the internet:

https://framboise.tail-XXXXX.ts.net/
|-- / proxy http://127.0.0.1:8080

Funnel started and running in the background.
Press Ctrl+C to exit.
```

### Step 3: Run Funnel in Background (Persistent)

To keep Funnel running after you log out:

```bash
# Run Funnel in background mode
tailscale funnel --bg 8080
```

Or use `tailscale serve` with Funnel enabled:

```bash
# Serve locally and via Funnel
tailscale serve --bg --https=443 8080
tailscale funnel --bg 443
```

### Step 4: Verify It's Working

Visit your Tailscale URL in a browser:

```
https://framboise.your-tailnet-name.ts.net
```

You should see a valid SSL certificate issued by Let's Encrypt.

### Port Limitations

Funnel can only listen on ports **443**, **8443**, and **10000**. Your Flask app can run on any port internally (e.g., 8080), and Funnel will proxy to it.

### Custom Domain with Funnel

If you want to use a custom domain like `recipes.rybergs.com`:

1. Create a CNAME record pointing to your Tailscale Funnel URL:
   ```
   recipes.rybergs.com -> framboise.your-tailnet-name.ts.net
   ```

2. Note: The SSL certificate will still show the `.ts.net` domain. For a custom domain certificate, you'll need to use a reverse proxy (see Option 3 below).

---

## Option 2: Tailscale HTTPS Certificates (Tailnet Only)

This option provides HTTPS for devices within your tailnet but does not expose services to the public internet.

### Step 1: Enable HTTPS (Same as Above)

Follow Step 1 from Option 1 to enable HTTPS certificates in your tailnet.

### Step 2: Generate Certificates

On your server, generate the TLS certificate:

```bash
sudo tailscale cert framboise.your-tailnet-name.ts.net
```

This creates two files:
- `framboise.your-tailnet-name.ts.net.crt` (certificate)
- `framboise.your-tailnet-name.ts.net.key` (private key)

### Step 3: Move Certificates to a Secure Location

```bash
sudo mkdir -p /etc/ssl/tailscale
sudo mv framboise.*.crt /etc/ssl/tailscale/
sudo mv framboise.*.key /etc/ssl/tailscale/
sudo chmod 600 /etc/ssl/tailscale/*.key
```

### Step 4: Configure Nginx with SSL

Update your Nginx configuration (`/etc/nginx/sites-available/clear-recipes`):

```nginx
server {
    listen 80;
    server_name framboise framboise.your-tailnet-name.ts.net;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name framboise framboise.your-tailnet-name.ts.net;

    ssl_certificate /etc/ssl/tailscale/framboise.your-tailnet-name.ts.net.crt;
    ssl_certificate_key /etc/ssl/tailscale/framboise.your-tailnet-name.ts.net.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Step 5: Set Up Certificate Renewal

Tailscale certificates expire after 90 days. Create a cron job to renew them:

```bash
sudo crontab -e
```

Add this line to renew weekly:

```
0 3 * * 0 tailscale cert framboise.your-tailnet-name.ts.net && systemctl reload nginx
```

---

## Option 3: Nginx + Let's Encrypt (Custom Domain)

If you want a custom domain with its own SSL certificate (not the `.ts.net` domain), use Certbot with Nginx.

### Prerequisites

- A domain pointing to your server (via Tailscale Funnel or direct IP)
- Port 80 accessible for ACME challenge

### Step 1: Install Certbot

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

### Step 2: Obtain Certificate

```bash
sudo certbot --nginx -d recipes.rybergs.com
```

Certbot will:
- Obtain a certificate from Let's Encrypt
- Automatically configure Nginx
- Set up auto-renewal

### Step 3: Verify Auto-Renewal

```bash
sudo certbot renew --dry-run
```

---

## Quick Reference

| Method | Public Access | Custom Domain | Auto-Renewal | Complexity |
|--------|--------------|---------------|--------------|------------|
| Tailscale Funnel | Yes | Partial* | Yes | Low |
| Tailscale Cert + Nginx | Tailnet only | No | Manual | Medium |
| Certbot + Nginx | Yes | Yes | Yes | Medium |

*Funnel uses `.ts.net` domain; CNAME works but cert shows `.ts.net`

---

## Troubleshooting

### "Certificate not valid" error
- Ensure MagicDNS is enabled in your tailnet
- Verify the hostname matches the certificate domain
- Check certificate expiration: `openssl x509 -in cert.crt -noout -dates`

### Funnel not accessible
- Verify Funnel is running: `tailscale status`
- Check allowed ports (443, 8443, 10000 only)
- Ensure Funnel is enabled in your tailnet ACL policy

### Certificate renewal fails
- Check Tailscale is running: `sudo systemctl status tailscaled`
- Verify rate limits aren't exceeded (max 5 certs per domain per week)

---

## Resources

- [Tailscale HTTPS Documentation](https://tailscale.com/kb/1153/enabling-https)
- [Tailscale Serve Documentation](https://tailscale.com/kb/1312/serve)
- [Tailscale Funnel Documentation](https://tailscale.com/kb/1223/funnel)
- [Let's Encrypt + Certbot](https://certbot.eff.org/)
