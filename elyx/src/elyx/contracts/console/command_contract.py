from abc import ABC, abstractmethod

from elyx.console.argument_parser import ArgumentParser


class CommandContract(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def parser(self) -> ArgumentParser:
        pass
