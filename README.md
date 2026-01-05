# django-data-intensive-systems

A comprehensive reference repository demonstrating best practices for building large-scale, data-intensive Django applications. This project is inspired by the principles outlined in "Designing Data-Intensive Applications" by Martin Kleppmann, focusing on architectural patterns suitable for high-throughput systems such as e-commerce, Point-of-Sale (POS) systems, sensor data ingestion, and event-driven microservices.

## Features

*   **Multi-tenant Architecture:** Implemented through a robust `core` application, providing isolated data management for different tenants.
*   **Modular Django Applications:**
    *   `orders`: Handles order processing and management for an e-commerce or POS system.
    *   `sensors`: Manages ingestion and processing of data from various sensors.
    *   `monitoring`: Provides health checks, logging, and metrics for application performance and stability.
*   **Asynchronous Processing:** Leverages Celery for background tasks and event-driven workflows.
*   **Containerized Development & Deployment:** Utilizes Docker and Docker Compose for consistent environments across development and production.
*   **Comprehensive Configuration:** Separate settings for development and production environments.
*   **Code Quality & Testing:** Includes `pytest` for testing and `pyproject.toml` for dependency management.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Docker Desktop (or Docker Engine and Docker Compose) installed on your system.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/django-data-intensive-systems.git
    cd django-data-intensive-systems
    ```

2.  **Set up environment variables:**
    Copy the example environment file and modify it as needed.
    ```bash
    cp .env.example .env
    ```
    *Note: For production, ensure sensitive information in `.env` is properly managed.*

3.  **Build and run the Docker containers:**
    ```bash
    docker-compose up --build
    ```
    This command will build the Docker images (if not already built) and start the services defined in `docker-compose.yml`.

### Running the Application

Once the Docker containers are up:

*   The Django application will be accessible at `http://localhost:8000`.
*   You can access the Django admin panel at `http://localhost:8000/admin`.
    *   To create a superuser for the admin panel:
        ```bash
        docker-compose exec web python manage.py createsuperuser
        ```
        Follow the prompts to create your superuser.

### Running Tests

To run the test suite:
```bash
docker-compose exec web pytest
```

### Project Structure Overview

```
.
├── apps/                # Django applications (core, monitoring, orders, sensors)
├── config/              # Django project settings and URL configurations
├── docs/                # Project documentation (architecture, database, patterns)
├── requirements/        # Python dependency management (base, dev, prod, test)
├── scripts/             # Utility scripts (data generation, load testing, migration audit)
├── tests/               # Unit and integration tests
├── Dockerfile           # Docker image definition for the application
├── docker-compose.yml   # Defines multi-container Docker application
├── manage.py            # Django's command-line utility
├── pyproject.toml       # Project metadata and build system (e.g., poetry, flit)
└── README.md            # This file
```

## Documentation

Further documentation on architecture, database design, and design patterns can be found in the `docs/` directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
