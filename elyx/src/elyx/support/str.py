class Str:
    """String helper utilities."""

    @staticmethod
    def parse_callback(callback: str, default: str | None = None) -> tuple[str, str | None]:
        """
        Parse a Class:method style callback into class and method.

        Args:
            callback: Callback string in format 'Class:method'.
            default: Default method name if not specified.

        Returns:
            Tuple of (class_name, method_name).
        """
        if Str.contains(callback, ":anonymous\0"):
            if Str.substr_count(callback, ":") > 1:
                return (
                    Str.before_last(callback, ":"),
                    Str.after_last(callback, ":"),
                )

            return (callback, default)

        if Str.contains(callback, ":"):
            parts = callback.split(":", 1)
            return (parts[0], parts[1])
        return (callback, default)

    @staticmethod
    def contains(haystack: str | None, needles: str | list[str], ignore_case: bool = False) -> bool:
        """
        Determine if a given string contains a given substring.

        Args:
            haystack: The string to search in.
            needles: The substring(s) to search for.
            ignore_case: Whether to ignore case.

        Returns:
            True if any needle is found, False otherwise.
        """
        if haystack is None:
            return False

        if ignore_case:
            haystack = haystack.lower()

        if not isinstance(needles, list):
            needles = [needles]

        for needle in needles:
            if ignore_case:
                needle = needle.lower()

            if needle != "" and needle in haystack:
                return True

        return False

    @staticmethod
    def substr_count(haystack: str, needle: str, offset: int = 0, length: int | None = None) -> int:
        """
        Returns the number of substring occurrences.

        Args:
            haystack: The string to search in.
            needle: The substring to search for.
            offset: The offset where to start counting.
            length: The maximum length after the offset to search for.

        Returns:
            Number of occurrences.
        """
        if length is not None:
            return haystack[offset : offset + length].count(needle)

        return haystack[offset:].count(needle)

    @staticmethod
    def before_last(subject: str, search: str) -> str:
        """
        Get the portion of a string before the last occurrence of a given value.

        Args:
            subject: The string to search in.
            search: The value to search for.

        Returns:
            The portion before the last occurrence, or the original string if not found.
        """
        if search == "":
            return subject

        pos = subject.rfind(search)

        if pos == -1:
            return subject

        return subject[:pos]

    @staticmethod
    def after_last(subject: str, search: str) -> str:
        """
        Return the remainder of a string after the last occurrence of a given value.

        Args:
            subject: The string to search in.
            search: The value to search for.

        Returns:
            The portion after the last occurrence, or the original string if not found.
        """
        if search == "":
            return subject

        position = subject.rfind(search)

        if position == -1:
            return subject

        return subject[position + len(search) :]

    @staticmethod
    def substr(string: str, start: int, length: int | None = None) -> str:
        """
        Returns the portion of the string specified by the start and length parameters.

        Args:
            string: The input string.
            start: The start position.
            length: The length of the substring.

        Returns:
            The extracted substring.
        """
        if length is None:
            return string[start:]
        elif length >= 0:
            return string[start : start + length]
        else:
            return string[start:length]

    @staticmethod
    def class_to_string(abstract: str | type) -> str:
        """
        Normalize abstract type to string representation.

        Args:
            abstract: Abstract type identifier or class.

        Returns:
            String representation of the abstract type.
        """
        if isinstance(abstract, type):
            return f"{abstract.__module__}.{abstract.__qualname__}"
        return abstract
