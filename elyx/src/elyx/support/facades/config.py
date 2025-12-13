from elyx.support.facades.facade import Facade


class Config(Facade):
    """Facade for accessing the configuration repository."""

    @classmethod
    def get_facade_accessor(cls):
        return "config"
