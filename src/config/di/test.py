# type: ignore

from dependency_injector import containers

from config.di.dev import Container


@containers.copy(Container)
class TestContainer(containers.DeclarativeContainer):
    pass
