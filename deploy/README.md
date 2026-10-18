# Ubuntu / AWS EC2 deployment

Use a NEW hostname (for example `studio.avitechno.in`) and port 8001 for this application. The example hostname is not configured. Do not overwrite the Helpdesk service or Nginx host. DNS and TLS must be set up separately.

After uploading the repository to GitHub, on Ubuntu:

```bash
sudo apt update
sudo apt install -y python3-venv nginx git
sudo git clone https://github.com/Avinashsingh011/avitechno-ai-studio.git /opt/avitechno-ai-studio
sudo python3 -m venv /opt/avitechno-ai-studio/.venv
sudo /opt/avitechno-ai-studio/.venv/bin/pip install -r /opt/avitechno-ai-studio/requirements.txt
sudo cp /opt/avitechno-ai-studio/.env.example /opt/avitechno-ai-studio/.env
sudo nano /opt/avitechno-ai-studio/.env
```

Set the API key, model IDs, username and a strong password. Set `STUDIO_ORIGIN=https://YOUR_STUDIO_DOMAIN` using the exact hostname visitors will use. This must match the browser Origin. Protect the environment file:

```bash
sudo chown root:www-data /opt/avitechno-ai-studio/.env
sudo chmod 640 /opt/avitechno-ai-studio/.env
sudo cp /opt/avitechno-ai-studio/deploy/avitechno-ai-studio.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now avitechno-ai-studio
sudo systemctl status avitechno-ai-studio
sudo cp /opt/avitechno-ai-studio/deploy/nginx.conf /etc/nginx/sites-available/avitechno-ai-studio
sudo nano /etc/nginx/sites-available/avitechno-ai-studio
```

Replace `YOUR_STUDIO_DOMAIN` in the Nginx file. Point that hostname's DNS to the instance. Ensure Security Groups allow HTTP/HTTPS; keep port 8001 private. Enable the new host:

```bash
sudo ln -s /etc/nginx/sites-available/avitechno-ai-studio /etc/nginx/sites-enabled/avitechno-ai-studio
sudo nginx -t
sudo systemctl reload nginx
```

Provision a valid TLS certificate for this hostname using your server's certificate process BEFORE entering credentials or making AI requests. The supplied Nginx file is an HTTP bootstrap, not a completed TLS deployment. Basic authentication requires HTTPS in production. Add proxy-level request limits according to your expected usage and provider budget before opening wider access. This is a personal password-protected application, not a multi-tenant SaaS.

Troubleshooting:

```bash
sudo journalctl -u avitechno-ai-studio -n 50 --no-pager
sudo nginx -t
```

The authenticated `/healthz` endpoint returns JSON. A 401 without credentials is expected once the password is set. A 403 generation response usually means `STUDIO_ORIGIN` does not match the exact browser origin. A provider error requires checking model access, key validity and account limits; the UI does not reveal secrets.

Rollback: disable only the new Studio Nginx symlink and stop `avitechno-ai-studio`. Leave the Helpdesk configuration untouched.
