# NeuVulneraScan

NeuVulneraScan is a Flask-based vulnerability scanning app with a web dashboard, user accounts, report history, and a CLI scanner.

## What it does

- Web UI for logging in, starting scans, and reviewing reports
- CLI scanning through `scan.py`
- JSON and TXT report generation
- DNS, SSL, header, directory, SQLi, and port scanning modules

## Project Structure

- `app.py` - Flask development entrypoint
- `web/` - Flask app, routes, templates, forms, and models
- `src/scanner/` - scanning engine and scanner modules
- `reports/` - generated scan reports
- `instance/` - local database and runtime files

## Local Setup

1. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Install Nmap on your machine and make sure `nmap` is available in your PATH.

4. Start the web app:

```powershell
python app.py
```

5. Open the app in your browser at `http://127.0.0.1:5000`.

## How to Use

1. Register a user at `/auth/register`.
2. Log in at `/auth/login`.
3. Go to the dashboard and start a scan.
4. Review the generated JSON and TXT reports in the dashboard and in `reports/`.

## CLI Usage

Run a scan from the terminal:

```powershell
python scan.py --target example.com --json --txt
```

## Upload to GitHub

If this is not already a Git repo, initialize it first:

```powershell
git init
git add .
git commit -m "Initial commit"
```

Then create a new repository on GitHub and push your code:

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## Run Online

Yes, you can run this online, but there is one important limitation: this project uses Nmap and other active scanners, so the hosting provider must allow outbound network access and system packages.

Recommended options:

- A VPS or cloud server where you can install Nmap
- Render or another Docker host that supports system packages

For production hosting:

- Set environment variables like `NEU_SECRET`, `NEU_ADMIN_PASSWORD`, and `FLASK_DEBUG=0`
- Install Nmap on the server
- Use a production WSGI server such as Gunicorn
- Bind to `0.0.0.0` instead of `127.0.0.1`
- Set `DATABASE_URL` if you want a hosted PostgreSQL database

Docker deployment:

```bash
docker build -t neuvulnerascan .
docker run -p 8000:8000 -e NEU_SECRET=your-secret -e NEU_ADMIN_PASSWORD=your-admin-password neuvulnerascan
```

Render deployment:

1. Push this repo to GitHub.
2. Create a new Render Web Service.
3. Choose this repository and let Render use the `Dockerfile`.
4. Add `NEU_ADMIN_PASSWORD` in the Render environment variables.
5. Deploy.

If you use Render's PostgreSQL, connect it by setting `DATABASE_URL` from the database service.

Example start command for non-Docker Linux hosting:

```bash
gunicorn wsgi:app
```

## Notes

- Do not commit your virtual environment.
- Avoid committing the local SQLite database in `instance/`.
- Generated reports can be committed if you want samples, but most projects keep them out of Git.
