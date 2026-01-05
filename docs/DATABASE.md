# Database Design & Strategy

This document outlines the database design, schema choices, and optimization strategies for the project, with a focus on handling data-intensive workloads in PostgreSQL.

## Data Models

For a detailed view of the Django models, see the source code in the `apps/*/models.py` files.

### Key Models:

-   **`sensors.Device`**: Metadata for sensor devices.
-   **`sensors.SensorReading`**: Raw, time-series data from sensors. This is expected to be the largest table in the database.
-   **`sensors.SensorAggregate`**: Pre-aggregated time-series data (e.g., hourly averages) to speed up analytics.
-   **`orders.Order`**: Represents a customer order, including status and total amount.
-   **`orders.OrderLineItem`**: Individual items within an order.
-   **`orders.Payment`**: Payment information related to an order.

## Indexing Strategy

Indexes are critical for read performance. Our strategy is to index based on common query patterns.

### `sensors.SensorReading`

This table is write-heavy but also needs to be queried efficiently for aggregation.

-   **BRIN Index on `timestamp`**:
    ```python
    models.Index(fields=['timestamp'], name='reading_timestamp_brin_idx', opclasses=['brin_minmax_ops'])
    ```
    A BRIN (Block Range Index) is ideal for `timestamp` because the data is naturally ordered. BRIN indexes are much smaller and have lower maintenance overhead than B-Tree indexes, which is perfect for a table with a very high volume of inserts.

-   **Composite B-Tree Index on `(device_id, timestamp)`**:
    ```python
    models.Index(fields=['device', 'timestamp'], name='reading_device_timestamp_idx')
    ```
    This is a standard B-Tree index used for efficiently looking up readings for a specific device within a time range, which is the primary query pattern for the aggregation task.

### `orders.Order`

-   **Index on `customer_id`**: For looking up orders by customer.
-   **Index on `status`**: For finding all orders with a specific status (e.g., 'pending', 'shipped').

## Partitioning Strategy (for `sensors.SensorReading`)

To manage the massive size of the `SensorReading` table, we will use **Time-Based Partitioning**, a native feature in PostgreSQL 10+.

### Concept

Instead of a single giant `sensors_sensorreading` table, we create a "parent" partitioned table. Data is then routed into child tables (partitions) based on a key. In our case, the key is the `timestamp` field.

We can create new partitions for each week or month.

### Example Implementation (Manual DDL)

While Django doesn't natively support creating partitions, we can use `RunSQL` migrations to manage them.

```sql
-- Create the parent table (managed by Django's makemigrations)
CREATE TABLE "sensors_sensorreading" (
    -- columns...
) PARTITION BY RANGE (timestamp);

-- Create a partition for January 2026
CREATE TABLE sensors_sensorreading_2026_01
PARTITION OF sensors_sensorreading
FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- Create a partition for February 2026
CREATE TABLE sensors_sensorreading_2026_02
PARTITION OF sensors_sensorreading
FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
```

### Benefits of Partitioning

1.  **Improved Query Performance**: When querying for a specific time range, PostgreSQL can perform "partition pruning," meaning it only scans the relevant child tables instead of the entire dataset.
2.  **Easier Data Management**: Old data can be archived or deleted efficiently by simply detaching or dropping a partition, which is much faster than running a large `DELETE` query.
3.  **Faster Maintenance**: Operations like `VACUUM` and `REINDEX` can be run on individual partitions, reducing the performance impact on the live system.

### Automation

A custom management command will be created (`scripts/manage_partitions.py`) to automatically create new partitions for the upcoming month and archive old ones. This will be run on a schedule (e.g., via cron).

*TODO: Implement the partition management script.*
