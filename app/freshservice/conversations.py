import requests, os, time
from requests.auth import HTTPBasicAuth
from app.logs import logs
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def get_ticket_conversations(ticket: dict) -> dict | None:
    key = os.environ["FSKEY"]
    id = ticket.get("id")
    url = f"https://eastwest.freshservice.com/api/v2/tickets/{id}/conversations"

    while True:
        try:
            response = requests.get(url, auth=HTTPBasicAuth(key, 'x'), timeout=(20,20))

            if response.status_code not in (200, 429):
                logs(f"Failed to fetch conversation for ticket ID# {id} with code {response.status_code}") 
                return

            if response.status_code == 429:
                logs(f"Made too many requests. Will wait 10 seconds to retry this request again.")

            else:
                conversation = response.json()["conversations"]
                return conversation

        except requests.exceptions.Timeout:
            logs(f"Timeout error for gettting conversations for ticket ID# {id}")
            return

def get_latest_conversation(conversations):
    last_message = None
    for message in conversations:
        current_message_timestamp = datetime.strptime(message.get("created_at"), "%Y-%m-%dT%H:%M:%SZ").timestamp()

        if last_message:
            last_message_timestamp = datetime.strptime(message.get("created_at"), "%Y-%m-%dT%H:%M:%SZ").timestamp()
        else:
            last_message_timestamp = 0
        
            if last_message_timestamp < current_message_timestamp:
                last_message = message

    return last_message

def place_on_hold(last_message) -> bool:
    now_timestamp = time.time()
    
    last_message_timestamp = datetime.strptime(last_message.get("created_at"), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    last_message_timestamp = last_message_timestamp.timestamp()

    difference = now_timestamp - last_message_timestamp

    if difference >= 86400:
        return True
    else:
        return False
