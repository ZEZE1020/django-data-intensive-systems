"""
Model factories for generating test data.

This file uses `factory-boy` to define factories for each Django model.
Factories provide a convenient way to create model instances for tests
with realistic, randomized data.

Usage:
    from tests.factories import UserFactory, DeviceFactory

    user = UserFactory()
    device = DeviceFactory(device_type='pressure')

Reference: https://factoryboy.readthedocs.io/
"""

import factory
from factory.django import DjangoModelFactory
from faker import Faker

from django.utils import timezone
from django.contrib.auth.models import User
from apps.sensors.models import Device, SensorReading
from apps.orders.models import Order, OrderLineItem, Payment

# Initialize Faker for realistic data
fake = Faker()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    is_staff = False
    is_active = True


class DeviceFactory(DjangoModelFactory):
    class Meta:
        model = Device

    name = factory.LazyAttribute(lambda o: f"Device-{fake.uuid4()[:8]}")
    device_type = factory.Iterator(['temperature', 'humidity', 'pressure', 'co2'])
    location = factory.Faker('city')


class SensorReadingFactory(DjangoModelFactory):
    class Meta:
        model = SensorReading

    device = factory.SubFactory(DeviceFactory)
    value = factory.Faker('pyfloat', left_digits=2, right_digits=2, positive=True)
    timestamp = factory.Faker('date_time_this_year', tzinfo=timezone.utc)


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    customer_id = factory.Faker('uuid4')
    status = factory.Iterator([s[0] for s in Order.STATUS_CHOICES])
    total_amount = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)


class OrderLineItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderLineItem

    order = factory.SubFactory(OrderFactory)
    product_id = factory.Faker('uuid4')
    quantity = factory.Faker('random_int', min=1, max=10)
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    order = factory.SubFactory(OrderFactory)
    amount = factory.LazyAttribute(lambda o: o.order.total_amount)
    status = factory.Iterator([s[0] for s in Payment.STATUS_CHOICES])
    transaction_id = factory.Faker('uuid4')


# TODO: Add more specific factories for different states (e.g., PaidOrderFactory)
