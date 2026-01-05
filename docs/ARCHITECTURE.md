# Architecture Overview

This document provides a high-level overview of the system architecture for the **django-data-intensive-systems** project.

## Guiding Principles

- **Scalability**: Components are designed to be horizontally scalable.
- **Reliability**: The system is designed to be resilient to failures.
- **Maintainability**: Code is organized into logical, decoupled modules.
- **Observability**: The system provides metrics, logs, and traces for monitoring.

## System Components

The architecture is composed of several key components working together:

![System Architecture Diagram](placeholder_for_diagram.png)
*TODO: Add a Mermaid or PNG diagram here.*

1.  **Web Application (Django)**
    -   The core of the system, providing the API and business logic.
    -   Built with Django and Django REST Framework.
    -   Serves API endpoints for sensor data ingestion and order processing.

2.  **Database (PostgreSQL)**
    -   The primary data store for relational data (orders, devices, etc.).
    -   Chosen for its reliability, extensibility, and performance.
    -   See [DATABASE.md](./DATABASE.md) for details on schema and indexing.

3.  **Cache & Message Broker (Redis)**
    -   Used for caching frequently accessed data to reduce database load.
    -   Acts as the message broker for Celery to manage asynchronous tasks.

4.  **Task Queue (Celery)**
    -   Manages background and asynchronous tasks, such as:
        -   Batch processing of sensor data.
        -   Executing steps in a Saga pattern for orders.
        -   Sending notifications.
    -   Uses Celery workers that can be scaled independently.

5.  **Monitoring Stack**
    -   **Prometheus**: For scraping and storing time-series metrics.
    -   **Grafana**: For visualizing metrics and creating dashboards (not included in repo).
    -   **Structured Logging**: JSON logs sent to a log aggregation service (e.g., ELK, Datadog).

## Application Modules (`/apps`)

The project is divided into several Django apps, each with a distinct responsibility:

-   `apps/core`: Shared utilities, abstract models (`TimeStampedModel`), and core patterns.
-   `apps/sensors`: Handles high-throughput ingestion and aggregation of time-series data.
-   `apps/orders`: Manages e-commerce transactions, payments, and implements the Saga pattern for consistency.
-   `apps/monitoring`: Provides health checks, metrics, and logging infrastructure.
-   `apps/events`: (Future) Implements event sourcing and CQRS patterns.

## Data Flow Examples

### 1. Sensor Data Ingestion

1.  A device sends a batch of readings to `/api/sensors/readings/bulk/`.
2.  The Django app validates the data and creates a Celery task for ingestion.
3.  A Celery worker picks up the task and performs a `bulk_create` to insert raw data into the `SensorReading` table.
4.  A separate, scheduled Celery task runs periodically to aggregate the raw data into the `SensorAggregate` table for efficient querying.

### 2. Order Creation (Saga Pattern)

1.  A user creates an order via `/api/orders/`.
2.  An `OrderSaga` is initiated.
3.  The saga executes a series of steps as Celery tasks: `process_payment`, `update_inventory`, `notify_customer`.
4.  If any step fails, compensation tasks are triggered to roll back the transaction.

See [PATTERNS.md](./PATTERNS.md) for more details on the specific design patterns used.
