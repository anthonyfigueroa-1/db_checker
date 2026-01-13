import requests, os, time, json
from requests.auth import HTTPBasicAuth
from app.logs import logs

key = os.environ["FSKEY"]

def get_one_ticket(ticket_id: int) -> dict | None:
    url = f"https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}?include=tags"

    while True:
        try:
            response = requests.get(url, auth=HTTPBasicAuth(key, "x"), timeout=(5,20))

            if response.status_code not in (200, 429):
                logs(f"Failed to fetch ticket ID# {ticket_id} with code {response.status_code}") 
                return

            elif response.status_code == 429:
                logs(f"Made too many requests. Will wait 10 seconds to retry this request again.")
                time.sleep(10)

            else:
                ticket = response.json()["ticket"]

                return ticket

        except requests.exceptions.Timeout:
            logs(f"Timeout error for ticket ID# {ticket_id}")
            return

def set_ticket_on_hold(ticket_id: int):
    url = f"https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}?include=tags"
    payload = {
            "status": 9
            }

    while True:
        try:
            response = requests.put(url, json=payload, auth=HTTPBasicAuth(key, "x"), timeout=(5,20))


            if response.status_code not in (200, 429):
                logs(f"Failed to PUT ticket ID# {ticket_id} on-hold with code {response.status_code}") 
                return

            elif response.status_code == 429:
                logs(f"Made too many requests. Will wait 10 seconds to retry this request again.")
                time.sleep(10)

            else:
                ticket = response.json()["ticket"]
                logs(f"Placed ticket ID# {ticket_id} on-hold")
                return ticket

        except requests.exceptions.Timeout:
            logs(f"Timeout error for PUTing ticket ID# {ticket_id} on-hold")
            return
