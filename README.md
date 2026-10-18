# AVI TECHNO AI Studio

![AVI TECHNO](web/brand/logo.webp)

A branded personal AI workspace by Avinash Kumar Singh. Standalone Python 3.11+ WSGI backend with a responsive HTML/CSS/JavaScript frontend. Deploy using Gunicorn + Nginx on Ubuntu AWS EC2, alongside the existing IT Helpdesk as a separate service.

## Included

12 tools: Book Cover Creator, Text to Image, Poster Studio, Product Shots, Social Content Studio, Amazon Listing Assistant, AI IT Helpdesk, Cloud & DevOps Copilot, Document Q&A, Resume & Interview Coach, Decision Planner and Idea Deconstructor.

Search, category filters, favourites, prompt building, TXT/Markdown reference input, copy/export, ChatGPT handoff, browser-local history, tiger logo, favicon and circuit wallpaper are included. Direct text/image generation uses the OpenAI API when server configuration is supplied. Text generation uses the Responses API; image generation expects a model returning `b64_json`.

## Run on Windows

Install Python 3.11 or newer. Extract the ZIP. Open PowerShell inside this folder:

```powershell
Copy-Item .env.example .env
notepad .env
py -3 app.py
```

Alternatively double-click `start.bat`. Open **http://localhost:8000**. No Python packages are needed for local use. Set your own `STUDIO_PASSWORD` to require login (username defaults to `avi`). AI remains disabled without credentials and an API key. Select model IDs available in your API account. Never paste secrets into GitHub or the browser UI.

## Upload to your GitHub

1. Create an empty repository named **avitechno-ai-studio** under **Avinashsingh011**. Leave README, license and .gitignore unchecked during creation.
2. Open PowerShell in the extracted project folder and run:

```powershell
git init
git add .
git status
git commit -m "Add branded AVI TECHNO AI Studio"
git branch -M main
git remote add origin https://github.com/Avinashsingh011/avitechno-ai-studio.git
git push -u origin main
```

Review `git status` before committing: `.env` must not appear. Git uses your normal GitHub sign-in. If Git is unavailable, GitHub's **Add file → Upload files** also works; upload the extracted contents including `.gitignore`, `.env.example` and `.github`, never `.env` or the ZIP itself.

Expected repository URL after you create/upload it: https://github.com/Avinashsingh011/avitechno-ai-studio

GitHub Pages serves static pages only and cannot run this Python AI backend. See `deploy/README.md` for AWS. GitHub Actions runs basic checks; it does not deploy to AWS.

## Project files

- `app.py`: WSGI API, protected access and static files
- `tools.json`: tool definitions and server instructions
- `web/`: dashboard and branded assets
- `passenger_wsgi.py`: cPanel Passenger entrypoint (hosting support required)
- `deploy/`: Gunicorn/systemd/Nginx examples
- `tests/`: routing, access and mocked AI response checks

```bash
python -m unittest discover -s tests -v
```

## Current boundaries

This is a standalone export of the Studio, not a modification to the live Helpdesk. Favourites/history remain in each browser. There is no SQLite ticket database, multi-user account system, subscription billing, vector retrieval, image editing or background agent. Document Q&A sends supplied text as context rather than creating a persistent RAG index. Product shots use descriptions rather than uploaded product-image editing. API usage is billed by your provider. Prompt building and handoff work without an API key. The UI connection badge means configuration is present, not verified provider access.

Tests use mocked provider responses. Real API generation and deployment on your EC2 server have not been tested. Brand assets remain the owner's property; no open-source license is assigned automatically.
