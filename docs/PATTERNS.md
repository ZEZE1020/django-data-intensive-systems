# Design Patterns

This document describes the key software design patterns used throughout the **django-data-intensive-systems** project. Each pattern is chosen to address specific challenges related to building reliable, scalable, and maintainable data-intensive applications.

## Core Application Patterns (`apps/core`)

### 1. Abstract Base Models
-   **Description**: We use abstract Django models in `apps/core/models.py` and `apps/core/mixins.py` to provide common fields and functionality to other models in the system.
-   **Examples**:
    -   `TimeStampedModel`: Automatically adds `created_at` and `updated_at` fields.
    -   `SoftDeleteModel`: Implements logical deletion by setting a `deleted_at` timestamp instead of physically removing records.
-   **Benefit**: Enforces consistency and reduces code duplication.

### 2. Custom QuerySet & Manager
-   **Description**: Custom `QuerySet` and `Manager` classes (e.g., for `SoftDeleteModel`) provide reusable methods for filtering and querying data, such as `all_with_deleted()` or `only_deleted()`.
-   **Benefit**: Encapsulates data access logic at the model layer, making views and services cleaner.

## Reliability & Concurrency Patterns

### 1. Optimistic Locking
-   **Pattern**: Implemented in `apps/core/mixins.py` via the `VersionedModel`.
-   **Description**: An integer `version` field is added to models. Before saving an object, the application checks if the `version` in the database matches the `version` of the object in memory. If they don't match, it means another process has modified the object, and a `StaleObjectError` is raised.
-   **Use Case**: Preventing lost updates in the `Order` model, where multiple processes might try to update an order concurrently.
-   **Benefit**: Ensures data consistency without the heavy overhead of pessimistic database-level locking.

### 2. Idempotency for API Endpoints
-   **Pattern**: Implemented via the `IdempotentModel` and related middleware/decorators.
-   **Description**: API endpoints that create or modify resources can be made idempotent by tracking a unique `Idempotency-Key` provided by the client. If a request with the same key is received twice, the original result is returned without re-processing the request.
-   **Use Case**: Safely retrying failed API requests to create a payment without charging the customer twice.
-   **Benefit**: Increases fault tolerance and reliability in distributed systems.

### 3. Saga Pattern
-   **Pattern**: Used for managing distributed transactions in the `apps/orders` module.
-   **Description**: A saga is a sequence of local transactions. Each transaction updates data in a single service and publishes an event or triggers the next transaction. If a local transaction fails, the saga executes a series of compensating transactions to undo the preceding transactions.
-   **Use Case**: The order creation process involves multiple steps (process payment, update inventory, notify user). A saga ensures that this multi-step operation completes fully or is properly rolled back.
-   **Benefit**: Maintains data consistency across multiple services without requiring distributed locks.

## Data Handling & Performance Patterns

### 1. Bulk Ingestion & Batch Processing
-   **Pattern**: Used in the `apps/sensors` module for high-throughput data ingestion.
-   **Description**: Instead of inserting sensor readings one by one, data is collected in batches and inserted using Django's `bulk_create` method. This is handled asynchronously by a Celery task.
-   **Benefit**: Drastically reduces the number of database round-trips and improves write throughput.

### 2. Pre-aggregation of Time-Series Data
-   **Pattern**: Implemented in `apps/sensors/models.py` with `SensorReading` (raw data) and `SensorAggregate` (aggregated data).
-   **Description**: A scheduled Celery task periodically reads the raw, high-frequency sensor data and computes aggregates (e.g., hourly average, min, max). These aggregates are stored in a separate table.
-   **Use Case**: Dashboards and analytical queries can read from the small `SensorAggregate` table instead of scanning millions of rows in the `SensorReading` table.
-   **Benefit**: Massively improves read performance for analytics and reporting.

### 3. Command Query Responsibility Segregation (CQRS)
-   **Pattern**: To be implemented in the `apps/events` module.
-   **Description**: CQRS separates the model used for writes (the "Command" model, or write model) from the model used for reads (the "Query" model, or read model).
-   **Use Case**: In event sourcing, the write model is an append-only log of events. The read models are projections of these events, optimized for different query needs.
-   **Benefit**: Allows for highly optimized and distinct models for writing and reading data, improving performance and scalability.
