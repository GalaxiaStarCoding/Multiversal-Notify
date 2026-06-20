"""
examples/teamtalk_bot.py

Example TeamTalk-side script that forwards TeamTalk events to a Prowl-compatible
Multiversal-Notify server (or any Prowl-like endpoint).

How it works:
- Replace the `integrate_with_teamtalk()` stub with your TeamTalk bot's event
  hooks. Whenever an event happens (user joins, text message, etc.) call the
  provided handlers (handle_user_join, handle_text_message) which will POST to
  the notify endpoint using the Prowl-compatible parameters: apikey, application,
  event, description, priority.

This script is intentionally dependency-light: it uses `requests` to POST the
notification. For real integration, use the TeamTalk SDK / binding for your
language and call `send_notification()` in the event callbacks.

Usage:
- Copy this file into your bot environment.
- pip install requests
- Edit NOTIFY_ENDPOINT and API_KEY.
- Integrate handlers into your TeamTalk client.

Author: GitHub Copilot (example)
"""

import requests
import time
import threading
import os
from typing import Optional

# Configuration: update these for your Multiversal-Notify server
NOTIFY_ENDPOINT = os.environ.get("M_NOTIFY_ENDPOINT", "https://your-server.example.com/publicapi/add")
API_KEY = os.environ.get("M_NOTIFY_APIKEY", "PUT_YOUR_API_KEY_HERE")
DEFAULT_APPLICATION = "TeamTalk"
DEFAULT_PRIORITY = 0  # Prowl priorities range from -2 .. 2 (optional)


def send_notification(apikey: str, application: str, event: str, description: str, priority: int = DEFAULT_PRIORITY, timeout: float = 5.0) -> bool:
    """Send a Prowl-compatible POST to the notification server.

    Returns True on success (HTTP 200/201), False otherwise.
    """
    data = {
        "apikey": apikey,
        "application": application,
        "event": event,
        "description": description,
        "priority": str(priority),
    }

    try:
        resp = requests.post(NOTIFY_ENDPOINT, data=data, timeout=timeout)
        resp.raise_for_status()
        print(f"[notify] Sent: {event} -> {resp.status_code}")
        return True
    except Exception as e:
        print(f"[notify] Failed to send notification: {e}")
        return False


# Example event handlers that would be invoked from your TeamTalk integration

def handle_user_join(nickname: str, channel: str):
    """Called when a user joins a channel."""
    event = "User joined"
    description = f"{nickname} joined {channel}"
    send_notification(API_KEY, DEFAULT_APPLICATION, event, description)


def handle_user_leave(nickname: str, channel: str):
    """Called when a user leaves a channel."""
    event = "User left"
    description = f"{nickname} left {channel}"
    send_notification(API_KEY, DEFAULT_APPLICATION, event, description)


def handle_text_message(sender: str, message: str, channel: Optional[str] = None):
    """Called when a text message is received.

    channel may be None for private messages.
    """
    event = "Text message"
    if channel:
        description = f"{sender} in {channel}: {message}"
    else:
        description = f"Private from {sender}: {message}"

    send_notification(API_KEY, DEFAULT_APPLICATION, event, description)


# This function is a placeholder showing where you'd hook into TeamTalk.
# Replace or extend it with the actual TeamTalk SDK or bot framework calls.

def integrate_with_teamtalk():
    """Pseudo-code / integration stub.

    Replace this function with real event registration using your preferred
    TeamTalk library. Example patterns:

    - Register callbacks with the TeamTalk client object (e.g. on_user_join,
      on_text_message).
    - Run a loop that polls a TeamTalk API or listens on a socket for events.

    Below is a simulated generator that fires sample events so you can test the
    notification path without a real TeamTalk server.
    """

    def simulator():
        users = ["Alice", "Bob", "Carol"]
        channels = ["General", "Support"]
        i = 0
        while True:
            # Simulate a user join
            user = users[i % len(users)]
            ch = channels[i % len(channels)]
            print(f"[sim] {user} joins {ch}")
            handle_user_join(user, ch)
            time.sleep(2)

            # Simulate a message
            msg = f"Hello from {user} ({i})"
            print(f"[sim] {user} says in {ch}: {msg}")
            handle_text_message(user, msg, ch)
            time.sleep(3)

            # Simulate a user leaving every few loops
            if i % 3 == 2:
                print(f"[sim] {user} leaves {ch}")
                handle_user_leave(user, ch)
                time.sleep(1)

            i += 1

    t = threading.Thread(target=simulator, daemon=True)
    t.start()


if __name__ == "__main__":
    print("TeamTalk -> Multiversal-Notify example bot")
    print("Edit NOTIFY_ENDPOINT and API_KEY or set env vars M_NOTIFY_ENDPOINT and M_NOTIFY_APIKEY.")
    # Start the integration (simulator by default)
    integrate_with_teamtalk()

    # Keep the main thread alive so background simulator / callbacks run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
