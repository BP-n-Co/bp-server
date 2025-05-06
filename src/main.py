import os
import sys

import uvicorn

from src._config import APP_PORT, UVICORN_MODE_DEBUG, base_logger

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from fastapi import FastAPI

from api.router import router as api_router

app = FastAPI()

app.include_router(api_router)

if __name__ == "__main__":
    base_logger.info("Starting application")
    uvicorn.run("main:app", host="0.0.0.0", port=APP_PORT, reload=UVICORN_MODE_DEBUG)
