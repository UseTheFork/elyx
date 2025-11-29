from abc import ABC, abstractmethod

from elyx.console.argument_parser import ArgumentParser


class CommandContract(ABC):
    @abstractmethod
    @property
    def name(self) -> str:
        pass

    @abstractmethod
    @property
    def description(self) -> str:
        pass

    @abstractmethod
    @property
    def parser(self) -> ArgumentParser:
        pass
