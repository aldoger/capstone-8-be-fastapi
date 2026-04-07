import random
import uuid

def generate_random_int_id() -> int:
    random_id = random.randint(1, 1000000)
    return random_id

def generate_random_uuid() -> str:
    random_id = str(uuid.uuid4())
    return random_id