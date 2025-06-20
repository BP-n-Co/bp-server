import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent
sys.path.append(str(root_path))


from fastapi import FastAPI

from api import api_router

app = FastAPI()

app.include_router(api_router)
