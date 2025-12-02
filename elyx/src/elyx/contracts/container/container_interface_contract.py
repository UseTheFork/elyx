from abc import ABC, abstractmethod


class ContainerInterfaceContract(ABC):
    @abstractmethod
    def get(self, id: str):
        """
        Finds an entry of the container by its identifier and returns it.

        Args:
            id: Identifier of the entry to look for.

        Returns:
            Entry.
        """
        pass

    @abstractmethod
    def has(self, id: str) -> bool:
        """
        Returns true if the container can return an entry for the given identifier.

        Args:
            id: Identifier of the entry to look for.

        Returns:
            bool
        """
        pass
