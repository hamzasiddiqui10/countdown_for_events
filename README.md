# Countdown to Events

Simple Flask app to store events (name & time) and display a live countdown for each event.

Features
- Sign up and sign in (users stored in SQLite)
- Create, edit, delete events
- Live countdown timers in the browser

Quick start

1. Create a virtualenv and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Initialize database and run the app:

```bash
python app.py
```

3. Open http://127.0.0.1:5000 in your browser, register an account, and create events.

Notes
- The app uses a local SQLite database file `events.db` created next to `app.py`.
- Event times are entered using the browser `datetime-local` input. Times are stored as naive datetimes.
# countdown_for_events