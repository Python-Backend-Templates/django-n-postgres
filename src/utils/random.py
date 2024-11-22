import random
import string


def random_string(length: int = 20) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def random_int(length: int = 20) -> str:
    return "".join(random.choices(string.digits, k=length))
