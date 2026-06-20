"""
server/app.py

Minimal Flask server implementing Prowl-compatible /publicapi/add and
device registration endpoints for Multiversal-Notify. Uses a simple SQLite
store for device registrations and a small FCM forwarder (legacy HTTP key
mode) if FCM_SERVER_KEY is provided via env var.

Endpoints:
- POST /publicapi/add
    required form fields: apikey, application, event, description
    optional: priority
- POST /devices/register
    required form/json: apikey, device_token
- POST /devices/unregister
    required form/json: apikey, device_token
- GET /devices/<apikey> (admin-protected via ADMIN_TOKEN env var)

Run:
- pip install -r server/requirements.txt
- export FLASK_APP=server/app.py; flask run --host=0.0.0.0 --port=5000
  (or python -m flask run ...)

Configuration via env vars:
- DATABASE_URL (default: sqlite:///multiversal_notify.db)
- FCM_SERVER_KEY (optional; if set, server will forward to FCM legacy API)
- ADMIN_TOKEN (optional; required to view device list)

Author: GitHub Copilot (example)
"""

from flask import Flask, request, jsonify, g
import os
import sqlite3
import time
from datetime import datetime
from typing import List

import server.fcm as fcm_forwarder

DATABASE = os.environ.get('DATABASE_PATH', 'multiversal_notify.db')
FCM_SERVER_KEY = os.environ.get('FCM_SERVER_KEY')
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'CHANGE_ME')

app = Flask(__name__)

# Database helpers

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            apikey TEXT NOT NULL,
            device_token TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(apikey, device_token)
        )
        '''
    )
    db.commit()
    db.close()


init_db()


# Utility
def find_devices_for_apikey(apikey: str) -> List[str]:
    db = get_db()
    cur = db.execute('SELECT device_token FROM devices WHERE apikey = ?', (apikey,))
    rows = cur.fetchall()
    return [r['device_token'] for r in rows]


# Routes
@app.route('/publicapi/add', methods=['POST'])
def publicapi_add():
    apikey = request.form.get('apikey') or request.json and request.json.get('apikey')
    application = request.form.get('application') or request.json and request.json.get('application')
    event = request.form.get('event') or request.json and request.json.get('event')
    description = request.form.get('description') or request.json and request.json.get('description')
    priority = request.form.get('priority') or (request.json and request.json.get('priority')) or 0

    if not all([apikey, application, event, description]):
        return jsonify({'error': 'missing required fields (apikey, application, event, description)'}), 400

    payload = {
        'application': application,
        'event': event,
        'description': description,
        'priority': int(priority),
        'received_at': datetime.utcnow().isoformat() + 'Z'
    }

    tokens = find_devices_for_apikey(apikey)
    if not tokens:
        app.logger.info('No registered devices for apikey %s. Dropping or storing notification.' % apikey)
        # For now, return 200 so senders like TeamTalk consider it accepted.
        return jsonify({'status': 'no_devices', 'message': 'No registered devices for this apikey'}), 200

    # Forward to FCM if configured, otherwise log
    if FCM_SERVER_KEY:
        success, results = fcm_forwarder.send_to_fcm(FCM_SERVER_KEY, tokens, payload['event'], payload['description'], data=payload)
        return jsonify({'status': 'forwarded', 'success': success, 'results': results}), 200
    else:
        app.logger.info('FCM_SERVER_KEY not configured; would forward to tokens: %s' % tokens)
        return jsonify({'status': 'noop', 'message': 'FCM not configured', 'tokens': tokens}), 200


@app.route('/devices/register', methods=['POST'])
def devices_register():
    if request.is_json:
        body = request.get_json()
        apikey = body.get('apikey')
        device_token = body.get('device_token')
    else:
        apikey = request.form.get('apikey')
        device_token = request.form.get('device_token')

    if not apikey or not device_token:
        return jsonify({'error': 'missing apikey or device_token'}), 400

    db = get_db()
    try:
        db.execute('INSERT OR IGNORE INTO devices (apikey, device_token) VALUES (?, ?)', (apikey, device_token))
        db.commit()
    except Exception as e:
        app.logger.exception('Failed to register device')
        return jsonify({'error': 'db_error', 'message': str(e)}), 500

    return jsonify({'status': 'registered', 'apikey': apikey, 'device_token': device_token}), 201


@app.route('/devices/unregister', methods=['POST'])
def devices_unregister():
    if request.is_json:
        body = request.get_json()
        apikey = body.get('apikey')
        device_token = body.get('device_token')
    else:
        apikey = request.form.get('apikey')
        device_token = request.form.get('device_token')

    if not apikey or not device_token:
        return jsonify({'error': 'missing apikey or device_token'}), 400

    db = get_db()
    cur = db.execute('DELETE FROM devices WHERE apikey = ? AND device_token = ?', (apikey, device_token))
    db.commit()

    if cur.rowcount == 0:
        return jsonify({'status': 'not_found'}), 404

    return jsonify({'status': 'unregistered'}), 200


@app.route('/devices/<apikey>', methods=['GET'])
def devices_list(apikey):
    token = request.args.get('admin_token') or request.headers.get('X-ADMIN-TOKEN')
    if not token or token != ADMIN_TOKEN:
        return jsonify({'error': 'unauthorized'}), 401

    db = get_db()
    cur = db.execute('SELECT device_token, created_at FROM devices WHERE apikey = ?', (apikey,))
    rows = cur.fetchall()
    devices = [{'device_token': r['device_token'], 'created_at': r['created_at']} for r in rows]
    return jsonify({'apikey': apikey, 'devices': devices}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')))
