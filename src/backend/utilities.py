import random

product_ids = []

def generate_product_id() -> int:
    """
    Description / Purpose:
        Generates a unique random 4-digit integer identifier for products.

    Args / Parameters:
        None.

    Returns:
        int: Unique random integer between 1000 and 10000.

    Constraints / Notes:
        Maintains an in-memory registry of issued IDs to prevent collisions.
    """
    while True:
        rand_num = random.randint(1000, 10000)
        if rand_num not in product_ids:
            product_ids.append(rand_num)
            return rand_num


