from app.redis import red

def rpop():
    ticket_id = red.rpop("db_check", 1)

    if ticket_id is None:
        return
    else:
        return ticket_id[0]

def hget(ticket_id):
    hash = red.hgetall(f"db_check:{ticket_id}")

    if hash:
        job_type = hash.get("type")

        return job_type
