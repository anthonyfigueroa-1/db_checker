from dotenv import load_dotenv
load_dotenv()

import os

tz = os.getenv("TZ", "America/Denver")
