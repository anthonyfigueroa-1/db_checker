from app.redis import red
from app.logs import logs

def send_rows_to_queue(rows):
    for row in rows:
        id = row[0]
        pipe = red.pipeline()
        pipe.lpush("db_check", f"{id}")
        pipe.hset(f"db_check:{id}", mapping={"type":"normal"})
        pipe.expire(f"db_check:{id}", 86400)
        pipe.execute()
    logs(f"Sent rows to queue")
