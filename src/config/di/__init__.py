from .dev import Container
from .test import TestContainer

container = Container()
test_container = TestContainer()


def get_di_container() -> Container:
    return container


def get_di_test_container() -> Container:
    return test_container
