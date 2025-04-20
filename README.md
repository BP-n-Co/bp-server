# Backend API

This repository contains a FastAPI backend application for BP&Co services.

## Prerequisites

Before running the application, you need to have Docker Desktop installed:

1. Download Docker Desktop from [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
2. Install Docker Desktop following the installation instructions for your operating system
3. Start Docker Desktop and ensure it's running

---

Copy paste `.env-example` to `.env` and fill it with your own environment requirements.

## Reset the database

To reset the database, use the following command:
```bash
/bin/bash bash/reset-db.sh
```

## Running the Application

To run the application, use the following command:

```bash
docker-compose up -d
```

To stop the application, use the following command:

```bash
docker-compose down
```

The API will be available at:
- API: http://localhost:${APP_PORT}
- API Documentation: http://localhost:${APP_PORT}/docs
- Alternative API Documentation: http://localhost:${APP_PORT}/redoc
