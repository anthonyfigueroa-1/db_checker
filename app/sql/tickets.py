import psycopg, os, json

from psycopg.types.json import Jsonb

from app.logs import logs
from app.redis.enque_rows import send_rows_to_queue

db = os.environ["DB"]

def query_open_tickets() -> list:
    with psycopg.connect(db) as con:
        with con.cursor() as cur:
            cur.execute("""SELECT id::BIGINT, status 
                        FROM tickets 
                        WHERE status != 5 OR status is null""")
            tickets = cur.fetchall()

            send_rows_to_queue(tickets)

    return tickets

def query_one_ticket(id: int):
    with psycopg.connect(db) as con:
        with con.cursor() as cur:
            cur.execute("""SELECT row_to_json(t) FROM tickets
                        AS t
                        WHERE id = %s""",
                        (id,))

            row = cur.fetchone()

    if row:
        row = row[0]

        return row

def update_ticket_table(ticket: dict, conversations: dict | None) -> None:
    id = ticket.get("id")
    status = ticket.get("status")
    priority = ticket.get("priority")
    with psycopg.connect(db) as con:
        with con.cursor() as cur:
            cur.execute("""UPDATE tickets
                        SET conversations = %s, status = %s, priority = %s
                        WHERE id = %s
                        """,
                        (Jsonb(conversations), status, priority, id)
                        )
    if status == 4:
        logs(f"Successfully updated conversations and resolved ticket ID# {id} in database")
    elif status == 5:
        logs(f"Successfully updated conversations and closed ticket ID# {id} in database")
    else:
        logs(f"Successfully updated ticket ID# {id} in database")

def add_resolution_note(ticket: dict, resolution_note: str) -> None:
    id = ticket.get("id")

    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        UPDATE tickets
                        SET resolution_note = %s
                        WHERE id = %s
                        AND resolution_note is NULL
                        RETURNING id
                        """,
                        (resolution_note, id))

            result = cur.fetchone()

            if not result:
                logs(f"Failed to update resolution note for ticket ID# {id}.")
