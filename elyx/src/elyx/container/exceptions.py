class EntryNotFoundException(Exception):
    """Exception raised when a container entry is not found."""

    def __init__(self, entry_id: str):
        self.entry_id = entry_id
        super().__init__(f"Entry not found in container: {entry_id}")
