# holiwell-backend

Backend service for gym app.
Used stack: *FastAPI*, *PostgreSQL*, *asyncio*.

## Install

Install `holiwell` from source:

    git clone https://github.com/omka0708/holiwell
    cd holiwell

You should have `.env` file at the */holiwell* folder.

Environment file `.env` should contain:
    
    DB_USER=<db_username>
    DB_PASS=<db_password>
    DB_HOST=holiwell-db
    DB_PORT=5432
    DB_NAME=<db_name>
    PGADMIN_EMAIL=<pgadmin_mail>
    PGADMIN_PASSWORD=<pgadmin_pass>
    SECRET_AUTH=<some_string>

## Run app

Run this command at the working directory */holiwell*:

    docker compose up -d --build

## Documentation

You can see documentation at:

    GET localhost:8000

It will redirect you to API documentation. 

