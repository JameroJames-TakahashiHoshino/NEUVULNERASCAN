# NeuVulneraScan

NeuVulneraScan is a Flask-based vulnerability scanning application that I created as a personal cybersecurity-related project during my 3rd year. I made this project to enhance my knowledge and hands-on skills in vulnerability scanning, especially in using Nmap and understanding how different scanning modules work.

This project includes a web dashboard, user accounts, scan report history, and a CLI-based scanner.

## What It Does

* Provides a web UI for logging in, starting scans, and reviewing reports
* Supports CLI scanning through `scan.py`
* Generates scan reports in JSON and TXT format
* Includes scanning modules for:

  * DNS checking
  * SSL checking
  * HTTP security headers
  * Directory scanning
  * SQL injection testing
  * Port scanning using Nmap

## Project Structure

```text
app.py          - Flask development entry point
web/            - Flask app, routes, templates, forms, and models
src/scanner/    - Scanning engine and scanner modules
reports/        - Generated scan reports
instance/       - Local database and runtime files
```

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Nmap on your machine and make sure `nmap` is available in your system PATH.

Start the web app:

```bash
python app.py
```

Open the app in your browser:

```text
http://127.0.0.1:5000
```

## How to Use

1. Register a user at `/auth/register`.
2. Log in at `/auth/login`.
3. Go to the dashboard and start a scan.
4. Review the generated JSON and TXT reports in the dashboard or inside the `reports/` folder.

## CLI Usage

You can also run a scan from the terminal:

```bash
python scan.py --target example.com --json --txt
```

## Uploading to GitHub

If this is not already a Git repository, initialize it first:

```bash
git init
git add .
git commit -m "Initial commit"
```

Then create a new repository on GitHub and push your code:

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## Running Online

This project can be hosted online, but there is an important limitation. Since it uses Nmap and other active scanning techniques, the hosting provider must allow outbound network access and installation of system packages.

Recommended hosting options:

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

## Important Note

This project is for educational and personal learning purposes only. Only scan systems, websites, or networks that you own or have permission to test. Unauthorized scanning may be illegal or against the rules of the target system.

## Notes

* Do not commit your virtual environment folder.
* Avoid committing the local SQLite database inside `instance/`.
* Generated reports can be committed if you want to provide samples, but most projects keep them out of Git.
