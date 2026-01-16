from app.freshservice.conversations import get_ticket_conversations, get_latest_conversation, place_on_hold
from app.sql.tickets import query_open_tickets, update_ticket_table
from app.freshservice.tickets import get_one_ticket, set_ticket_on_hold
from app.logs import logs
from app.redis.queue import rpop, hget

import time

def main() -> None:
    while True:
        ticket_id = rpop()
        job_type = hget(ticket_id)

        if not ticket_id:
            logs("No rows in queue")
            tickets = query_open_tickets()

            if not tickets:
                logs("All tickets have either been updating or do not require updating at this time.")
                logs("Sleeping for 5 minutes")

                #5 Minutes
                time.sleep(300)

        else:
            ticket = get_one_ticket(ticket_id)
            time.sleep(1)
                    
            if not ticket:
                continue

            conversations = get_ticket_conversations(ticket)
            time.sleep(1)

            match job_type:
                case "normal":
                    update_ticket_table(ticket, conversations)

                case "on_hold":
                    last_message = get_latest_conversation(conversations)
                    if last_message:
                        on_hold = place_on_hold(last_message)
                        if on_hold is True:
                            ticket = set_ticket_on_hold(ticket_id)
                            update_ticket_table(ticket, conversations)

                        elif on_hold is False:
                            update_ticket_table(ticket, conversations)
                    else:
                        update_ticket_table(ticket, conversations)
                
                case _:
                    pass
            
            time.sleep(2)

def runner() -> None:
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
