.
## Project Services
The project consists of the following services:

- API Service: Responsible for handling HTTP requests and serving the FastAPI application.
- Data Transformation Service: Handles data transformation tasks and provides APIs for data manipulation.
- AI Service: Implements machine learning algorithms and provides AI-related functionalities.

Each service has its own directory within the project structure and contains the necessary files and modules to fulfill its specific role.

Feel free to contribute to any of these services or suggest improvements by opening an issue or submitting a pull request.


## Table of Contents
- [Installation](#installation)
- [Setup](#setup)
- [Running the Application](#running-the-application)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites
To install and run the project, you need the following prerequisites:
- Python 3.12+
- Poetry
- Redis

### Setup
To set up the project, follow these steps:

1. **Clone the Repository**

    ```bash
    git clone https://github.com/your-username/your-repo.git
    cd your-repo
    ```

2. **Set up Virtual Environment**

    ```bash
    poetry shell
    ```

3. **Install Dependencies**

    ```bash
    poetry install --no-root 
    ```

### Environment Variables

To configure the environment variables for the project, follow these steps:

1. **Create `.env` File**

    Create a new file named `.env` in the root directory of the project.

2. **Configure Rate Limiting Parameters**

    Update the values in your `.env` file to configure the rate limiting parameters for your routes.

    ```dotenv
    RATE_LIMIT_TIME=60
    RATE_LIMIT_REQUESTS=100
    OTLP_ENDPOINT=http://localhost:4317
    DB_URI=postgresql://admin:admin429@localhost:5432/db-amp-core
    REDIS_URL=redis://localhost
    RATE_LIMITER_TIMES=50
    RATE_LIMITER_DURATION=60
    ```

    Make sure to adjust the values as needed.

### Running the Application

To run the FastAPI application, use the following command:

```bash
poetry uvicorn __main__.py:app --reload
```

This will start the application and make it accessible at `http://localhost:8000`.

## Project Structure

The project structure is as follows:

```
.
├── api
│   ├── __main__.py
│   ├── db.py
│   ├── services
|   |   ├── db.py
│   │   └── ratelimiter.py
│   └── v1
│       ├── __init__.py
│       ├── ping.py
│       └── user.py
├── common
│   ├── datasources
│   │   ├── __init__.py
│   |   ├── main.py
│   │   └── redis.py
│   ├── models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services
│   │   └── logger.py
│   └── utils
│       ├── config.py
│       └──  opentelemetry.py
├── .env
├── poetry.lock
├── pyproject.toml
└── README.md
```

## Contributing

Contributions are welcome! If you find any issues or have suggestions, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

