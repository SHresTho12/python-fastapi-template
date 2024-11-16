import random

from faker import Faker

fake = Faker()


def get_new_service():
    service = {
        "name": fake.name(),
        "description": fake.name(),
        "status": 1
    }
    return service
