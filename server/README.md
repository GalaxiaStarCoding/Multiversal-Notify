# Multiversal-Notify — Server example

This folder contains a minimal example Flask server that implements a
Prowl-compatible receiver and device registration for the Multiversal-Notify
project.

Features
- POST /publicapi/add — accepts apikey/application/event/description/priority
- POST /devices/register — register an Android FCM device token to an apikey
- POST /devices/unregister — remove a registered token
- GET /devices/<apikey> — admin-protected listing of tokens for debugging
- SQLite-backed device storage (multiversal_notify.db by default)
- Optional FCM forwarding using legacy server key (set FCM_SERVER_KEY env var)

Getting started (quick)

1. Create a Python venv and install dependencies:

   python -m venv venv
   source venv/bin/activate
   pip install -r server/requirements.txt

2. Run the server locally:

   export FLASK_APP=server/app.py
   export ADMIN_TOKEN=change-me
   flask run --host=0.0.0.0 --port=5000

3. Register a device (example):

   curl -X POST http://localhost:5000/devices/register \
     -d "apikey=my-team-apikey" \
     -d "device_token=example_device_token"

4. Send a Prowl-style notification (example):

   curl -X POST http://localhost:5000/publicapi/add \
     -d "apikey=my-team-apikey" \
     -d "application=TeamTalk" \
     -d "event=User joined" \
     -d "description=Alice joined General"

If you set FCM_SERVER_KEY in the environment, the server will attempt to
forward the notification to the registered device tokens using the legacy FCM
HTTP API. For production use, migrate to the HTTP v1 API and service account
credentials or use the Firebase Admin SDK.
