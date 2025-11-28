from elyxate.foundation.application import Application


class ApplicationBuilder:
    def __init__(self, app: Application):
        """
        Create a new application builder instance.

        Args:
            app: The application instance.
        """
        self.app = app
