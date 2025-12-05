from abc import ABC, abstractmethod


class ContainerInterface(ABC):
    @abstractmethod
    def get(self, id: str):
        """
        Finds an entry of the container by its identifier and returns it.

        Args:
            id: Identifier of the entry to look for.

        Returns:
            Entry.

        Raises:
            NotFoundExceptionInterface: No entry was found for this identifier.
            ContainerExceptionInterface: Error while retrieving the entry.
        """
        pass

    @abstractmethod
    def has(self, id: str) -> bool:
        """
        Returns true if the container can return an entry for the given identifier.
        Returns false otherwise.

        `has(id)` returning true does not mean that `get(id)` will not throw an exception.
        It does however mean that `get(id)` will not throw a `NotFoundExceptionInterface`.

        Args:
            id: Identifier of the entry to look for.

        Returns:
            bool
        """
        pass
