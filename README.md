# Redis and PostgreSQL Orchestration with Docker

This project demonstrates a common data processing pattern using Docker to containerize a Python application, a Redis database, and a PostgreSQL database.

-   **Redis** is used as a fast, in-memory message queue for incoming data.
-   **PostgreSQL** is used for long-term, persistent storage of the data.
-   **Python** acts as the orchestrator, pulling data from the Redis queue and saving it to PostgreSQL.

## Architecture

1.  The `orchestrator` service runs a Python script.
2.  The script simulates a "producer" by creating a sample JSON event and pushing it to a list in Redis (`LPUSH`).
3.  The script then acts as a "consumer" by using a blocking pop (`BRPOP`) to wait for and retrieve an event from the Redis list.
4.  Once an event is retrieved, it's parsed and inserted into a table in the PostgreSQL database.
5.  All three services (`postgres`, `redis`, `orchestrator`) are defined and networked together by `docker-compose.yml`.

## How to Run

### Prerequisites

-   Docker
-   Docker Compose

### Steps

1.  **Clone or download the project files** and make sure they are organized in the structure specified above.

2.  **Build and run the containers:**
    Open a terminal in the project's root directory (where `docker-compose.yml` is located) and run:

    ```bash
    docker-compose up --build
    ```

    -   `--build` forces Docker Compose to build the Python image from your `Dockerfile`. You only need to use it the first time or when you change the `Dockerfile` or `requirements.txt`.
    -   You will see logs from all three containers. The `orchestrator` log will show connection attempts and then the flow of data from production to storage.

3.  **View the logs:**
    To see the output from just the orchestrator, open a new terminal and run:

    ```bash
    docker-compose logs -f orchestrator
    ```
    You should see output like:
    ```
    Produced event and pushed to Redis queue: {'event_id': 'evt-8234', 'value': 42}
    
    Waiting for new data in Redis queue 'data_queue'...
    Consumed event from Redis: {'event_id': 'evt-8234', 'value': 42}
    Successfully stored event evt-8234 in PostgreSQL.
    ```

4.  **Stopping the application:**
    Press `Ctrl+C` in the terminal where `docker-compose up` is running. To remove the containers and the network, run:

    ```bash
    docker-compose down
    ```
    To also remove the PostgreSQL data volume, run:
    ```bash
    docker-compose down -v
    ```

## Verifying the Data (Optional)

You can connect to the databases directly to see the data.

### PostgreSQL

You can use any SQL client (like DBeaver, pgAdmin, or the command-line `psql`) to connect to the PostgreSQL database using these details:
-   **Host**: `localhost`
-   **Port**: `5432`
-   **Database**: `historical_data`
-   **User**: `myuser`
-   **Password**: `mypassword`

Then, run a query:
```sql
SELECT * FROM event_logs ORDER BY timestamp DESC;
```

### Redis

You can use a Redis client (like `redis-cli` or RedisInsight) to connect to:
-   **Host**: `localhost`
-   **Port**: `6379`

You can check the length of the queue with the command: `LLEN data_queue`.