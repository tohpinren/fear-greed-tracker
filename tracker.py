#!/usr/bin/env python3
"""
Fear and Greed Index Tracker

Fetches data from CNN Fear and Greed Index and Crypto Fear and Greed Index APIs,
checks for extreme fear conditions, stores historical data, and sends notifications.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests

from email_notifier import EmailNotifier


CNN_GRAPH_DATA_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

CNN_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.cnn.com/",
    "Origin": "https://www.cnn.com",
}


def fetch_cnn_fear_greed() -> Optional[Dict]:
    """
    Fetch CNN Fear and Greed Index data from the API.
    
    Uses browser-like headers to avoid 418 (blocked bot) responses from the API.
    
    Returns:
        Dictionary containing score, rating, and timestamp, or None if fetch fails
    """
    try:
        response = requests.get(
            CNN_GRAPH_DATA_URL,
            headers=CNN_HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        
        fng_data = data.get("fear_and_greed", {})
        return {
            "value": fng_data.get("score"),
            "rating": fng_data.get("rating"),
            "timestamp": fng_data.get("timestamp"),
        }
    except requests.RequestException as e:
        print(f"Error fetching CNN Fear and Greed Index: {e}", file=sys.stderr)
        return None


def fetch_crypto_fear_greed() -> Optional[Dict]:
    """
    Fetch Crypto Fear and Greed Index data from Alternative.me API.
    
    Returns:
        Dictionary containing value, rating, and timestamp, or None if fetch fails
    """
    url = "https://api.alternative.me/fng/?limit=1"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("data") and len(data["data"]) > 0:
            fng_data = data["data"][0]
            timestamp = fng_data.get("timestamp")
            return {
                "value": int(fng_data.get("value", 0)),
                "rating": fng_data.get("value_classification", "").lower().replace(" ", "_"),
                "timestamp": datetime.fromtimestamp(int(timestamp), tz=timezone.utc).isoformat() if timestamp else None,
            }
        return None
    except requests.RequestException as e:
        print(f"Error fetching Crypto Fear and Greed Index: {e}", file=sys.stderr)
        return None


def load_history(file_path: Path) -> Dict:
    """
    Load historical data from JSON file.
    
    Args:
        file_path: Path to the JSON history file
        
    Returns:
        Dictionary with history data, or default structure if file doesn't exist
    """
    if file_path.exists():
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading history from {file_path}: {e}", file=sys.stderr)
    
    return {
        "last_updated": None,
        "history": [],
        "last_notification": None,
    }


def save_history(file_path: Path, history: Dict) -> None:
    """
    Save historical data to JSON file.
    
    Args:
        file_path: Path to the JSON history file
        history: Dictionary with history data to save
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, "w") as f:
            json.dump(history, f, indent=2)
    except IOError as e:
        print(f"Error saving history to {file_path}: {e}", file=sys.stderr)
        raise


def should_send_notification(
    history: Dict,
    threshold: int,
    cooldown_hours: int = 24,
    extreme_fear: bool = True,
) -> bool:
    """
    Determine if a notification should be sent based on threshold and cooldown.
    
    Args:
        history: History dictionary containing last_notification timestamp
        threshold: Value threshold; for extreme fear notify when value <= threshold
        cooldown_hours: Hours to wait before sending another notification (default: 24)
        extreme_fear: If True, notify when value <= threshold; if False, when value >= threshold
        
    Returns:
        True if notification should be sent, False otherwise
    """
    if not history.get("history"):
        return True
    
    latest_entry = history["history"][-1]
    current_value = latest_entry.get("value")
    
    if current_value is None:
        return False
    if extreme_fear:
        if current_value > threshold:
            return False
    else:
        if current_value < threshold:
            return False
    
    last_notification = history.get("last_notification")
    if last_notification is None:
        return True
    
    try:
        last_notification_time = datetime.fromisoformat(last_notification.replace("Z", "+00:00"))
        time_since_notification = datetime.now(timezone.utc) - last_notification_time.replace(tzinfo=timezone.utc)
        
        if time_since_notification.total_seconds() < cooldown_hours * 3600:
            return False
    except (ValueError, AttributeError):
        return True
    
    return True


def update_history(history: Dict, current_data: Dict, index_name: str) -> None:
    """
    Update history with current data point.
    
    Args:
        history: History dictionary to update
        current_data: Current index data with value, rating, timestamp
        index_name: Name of the index (for logging)
    """
    now = datetime.now(timezone.utc).isoformat()
    
    entry = {
        "timestamp": current_data.get("timestamp") or now,
        "value": current_data.get("value"),
        "rating": current_data.get("rating"),
        "notified": False,
    }
    
    history["history"].append(entry)
    history["last_updated"] = now
    
    if len(history["history"]) > 1000:
        history["history"] = history["history"][-1000:]


def log_notification(notifications_log_path: Path, index_name: str, value: float, rating: str) -> None:
    """
    Log a notification to the notifications log file.
    
    Args:
        notifications_log_path: Path to notifications log JSON file
        index_name: Name of the index
        value: Current index value
        rating: Current rating
    """
    log_data = load_history(notifications_log_path)
    
    if "notifications" not in log_data:
        log_data["notifications"] = []
    
    notification_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "index": index_name,
        "value": value,
        "rating": rating,
    }
    
    log_data["notifications"].append(notification_entry)
    
    if len(log_data["notifications"]) > 500:
        log_data["notifications"] = log_data["notifications"][-500:]
    
    save_history(notifications_log_path, log_data)


def track_index(
    index_name: str,
    fetch_func,
    history_path: Path,
    notifications_log_path: Path,
    email_notifier: Optional[EmailNotifier],
    threshold: int = 25,
    dry_run: bool = False,
    extreme_fear: bool = True,
) -> Tuple[bool, Optional[Dict]]:
    """
    Track a single index: fetch data, update history, check threshold, send notification.
    
    Args:
        index_name: Name of the index (e.g., "CNN Fear and Greed Index")
        fetch_func: Function to fetch index data
        history_path: Path to history JSON file
        notifications_log_path: Path to notifications log JSON file
        email_notifier: EmailNotifier instance or None
        threshold: For extreme_fear, notify when value <= threshold (default: 25)
        dry_run: If True, skip sending emails
        extreme_fear: If True, notify on extreme fear (value <= threshold); else extreme greed (value >= threshold)
        
    Returns:
        Tuple of (notification_sent: bool, current_data: Dict or None)
    """
    print(f"Fetching {index_name}...")
    current_data = fetch_func()
    
    if current_data is None:
        print(f"Failed to fetch {index_name}")
        return False, None
    
    value = current_data.get("value")
    rating = current_data.get("rating")
    
    print(f"{index_name}: Value={value}, Rating={rating}")
    
    history = load_history(history_path)
    update_history(history, current_data, index_name)
    
    should_notify = should_send_notification(history, threshold, extreme_fear=extreme_fear)
    triggers = (value is not None and value <= threshold) if extreme_fear else (value is not None and value >= threshold)
    
    if should_notify and triggers:
        if extreme_fear:
            print(f"{index_name} reached extreme fear threshold ({value} <= {threshold})")
        else:
            print(f"{index_name} reached extreme greed threshold ({value} >= {threshold})")
        
        if not dry_run and email_notifier:
            try:
                email_notifier.send_notification(index_name, value, rating, extreme_fear=extreme_fear)
                history["last_notification"] = datetime.now(timezone.utc).isoformat()
                log_notification(notifications_log_path, index_name, value, rating)
                print(f"Notification sent for {index_name}")
                save_history(history_path, history)
                return True, current_data
            except Exception as e:
                print(f"Error sending notification for {index_name}: {e}", file=sys.stderr)
        elif dry_run:
            print(f"[DRY RUN] Would send notification for {index_name}")
            return True, current_data
    else:
        if triggers:
            print(f"{index_name} is at extreme fear but notification cooldown active" if extreme_fear else f"{index_name} is at extreme greed but notification cooldown active")
        else:
            if extreme_fear:
                print(f"{index_name} above fear threshold ({value} > {threshold}); no notification")
            else:
                print(f"{index_name} below greed threshold ({value} < {threshold}); no notification")
    
    save_history(history_path, history)
    return False, current_data


def main():
    """Main entry point for the tracker."""
    dry_run = "--dry-run" in sys.argv
    
    data_dir = Path("data")
    cnn_history_path = data_dir / "cnn_fear_greed_history.json"
    crypto_history_path = data_dir / "crypto_fear_greed_history.json"
    notifications_log_path = data_dir / "notifications_log.json"
    
    threshold = int(os.getenv("THRESHOLD", "25"))
    
    email_notifier = None
    if not dry_run:
        try:
            email_notifier = EmailNotifier()
        except Exception as e:
            print(f"Warning: Email notifier initialization failed: {e}", file=sys.stderr)
            print("Continuing without email notifications...", file=sys.stderr)
    
    print("=" * 60)
    print("Fear and Greed Index Tracker (notify on extreme fear)")
    print(f"Threshold: value <= {threshold} triggers notification")
    print(f"Dry Run: {dry_run}")
    print("=" * 60)
    
    cnn_notified, cnn_data = track_index(
        "CNN Fear and Greed Index",
        fetch_cnn_fear_greed,
        cnn_history_path,
        notifications_log_path,
        email_notifier,
        threshold,
        dry_run,
        extreme_fear=True,
    )
    
    crypto_notified, crypto_data = track_index(
        "Crypto Fear and Greed Index",
        fetch_crypto_fear_greed,
        crypto_history_path,
        notifications_log_path,
        email_notifier,
        threshold,
        dry_run,
        extreme_fear=True,
    )
    
    print("=" * 60)
    print("Tracking complete")
    if cnn_notified or crypto_notified:
        print("Notifications sent!")
    print("=" * 60)


if __name__ == "__main__":
    main()
