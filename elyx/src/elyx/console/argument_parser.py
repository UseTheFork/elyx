from argparse import ArgumentParser as BaseArgumentParser


class ArgumentParser(BaseArgumentParser):
    """Custom ArgumentParser for"""

    def __init__(self, *args, **kwargs):
        """Initialize parser with exit_on_error=False and add_help=False by default."""
        kwargs.setdefault("exit_on_error", False)
        kwargs.setdefault("add_help", False)
        super().__init__(*args, **kwargs)
