ExpenseMaster - Final Build
===========================

Embedded keys / URLs:
- SUPABASE_URL: https://gtgevicljoorjlyldtjy.supabase.co
- SUPABASE_ANON_KEY: (embedded in app/.env)
- Gmail (for Supabase SMTP): manojdaniel0@gmail.com (configure in Supabase dashboard with App Password)
- CurrencyFreaks API key: stored in server/.env

Important: Google OAuth requires you to enable the Google provider in Supabase Auth and add
the redirect URI http://127.0.0.1:8910/callback in your Google Cloud Console OAuth client.
Supabase will handle the provider client id/secret in the dashboard (do that step).

Quick start (local development):
1) Supabase: run the SQL in 01_schema.sql in your Supabase SQL editor. Enable Auth -> Email confirmations.
2) Server (FX):
   cd server
   python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
3) App (Kivy):
   cd app
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   python main.py

Builds:
- Android APK: use Buildozer with the included spec (edit if needed).
- Windows EXE: use PyInstaller as per BUILD_DESKTOP.md

Security: remove secrets before pushing to public repos. Keep server/.env and app/.env private.
