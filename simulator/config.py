import os

SIMULATOR_INTERVAL_SECONDS = float(os.getenv("SIMULATOR_INTERVAL_SECONDS", "5.0"))
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
