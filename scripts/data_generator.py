"""
Synthetic data generation script.

This script uses Faker and Factory Boy to generate realistic-looking
test data for the database. It's useful for populating a development
database for testing, demonstrations, or performance benchmarking.

Usage:
    python manage.py shell < scripts/data_generator.py

Note: This script should be run within the Django shell to have access to the models.
"""

import random
from faker import Faker
from django.utils import timezone
from apps.sensors.models import Device, SensorReading
from apps.orders.models import Order, OrderLineItem, Payment
import uuid

# Initialize Faker
fake = Faker()

# Generate a consistent tenant_id for all generated data for simplicity in testing
TEST_TENANT_ID = uuid.uuid4()

def generate_devices(count=10):
    """
    Generates a number of sensor devices.
    """
    devices = []
    for _ in range(count):
        device = Device.objects.create(
            name=f"Device-{fake.uuid4()[:8]}",
            device_type=random.choice(['temperature', 'humidity', 'pressure']),
            location=fake.city(),
            tenant_id=TEST_TENANT_ID, # Add tenant_id
        )
        devices.append(device)
    print(f"Generated {len(devices)} devices.")
    return devices

def generate_sensor_readings(devices, readings_per_device=100):
    """
    Generates sensor readings for a list of devices.
    """
    readings = []
    for device in devices:
        for _ in range(readings_per_device):
            reading = SensorReading(
                device=device,
                value=random.uniform(20.0, 30.0),
                created_at=timezone.now() - timezone.timedelta(days=random.randint(0, 365)), # Use created_at
                tenant_id=TEST_TENANT_ID, # Add tenant_id
            )
            readings.append(reading)
    
    SensorReading.objects.bulk_create(readings)
    print(f"Generated {len(readings)} sensor readings.")
    return readings

# TODO: Add functions to generate orders, payments, etc.

if __name__ == "__main__":
    print("Starting data generation...")
    # This check prevents running the script outside of the Django shell context
    # where models aren't loaded.
    try:
        # Check if a model is available. This will fail if not in Django shell.
        Device.objects.exists()
        
        # Run generation functions
        devices = generate_devices(10)
        generate_sensor_readings(devices, 50)
        
        # Also generate some orders for the same tenant
        # from apps.orders.models import Order, OrderLineItem # Already imported
        # from apps.orders.models import Payment # Already imported
        
        customer_email = fake.email()
        customer_name = fake.name()
        shipping_address = fake.address()

        order = Order.objects.create(
            order_number=f"ORD-{fake.uuid4()[:8]}",
            customer_email=customer_email,
            customer_name=customer_name,
            shipping_address=shipping_address,
            subtotal=Decimal(0), # Will be calculated by line items
            total_amount=Decimal(0),
            tenant_id=TEST_TENANT_ID,
        )
        print(f"Generated Order: {order.order_number}")

        # Generate some line items for the order
        for _ in range(random.randint(1, 5)):
            product_name = fake.word().capitalize() + " Sensor"
            unit_price = Decimal(random.uniform(10.0, 100.0)).quantize(Decimal('0.01'))
            quantity = random.randint(1, 5)
            OrderLineItem.objects.create(
                order=order,
                product_name=product_name,
                product_sku=fake.ean8(),
                quantity=quantity,
                unit_price=unit_price,
                tenant_id=TEST_TENANT_ID,
            )
        order.calculate_total()
        order.save()
        print(f"Generated {order.line_items.count()} Line Items for Order {order.order_number}")


        print("Data generation complete.")
        
    except NameError:
        print("\nThis script must be run within the Django shell.")
        print("Usage: python manage.py shell < scripts/data_generator.py")
    except Exception as e:
        print(f"An error occurred: {e}")
