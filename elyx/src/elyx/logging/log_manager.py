from elyx.contracts.container import Container as ContainerContract


class LogManager:
    def __init__(self, app: ContainerContract):
        self.app = app
        self.channels = {}  # Cache of created channels

    async def _resolve_channel(self, name: str):
        """
        Create a channel based on config.

        Args:
            name: The channel name.

        Returns:
            Logger instance.
        """
        from elyx.logging.console_logger import ConsoleLogger

        config = await self.app.make("config")
        channel_config = config.get(f"logging.channels.{name}")

        if not channel_config:
            raise ValueError(f"Logging channel '{name}' is not configured.")

        driver = channel_config.get("driver")

        # Map drivers to classes
        drivers = {
            "console": ConsoleLogger,
        }

        logger_class = drivers.get(driver)
        if not logger_class:
            raise ValueError(f"Unsupported logging driver: {driver}")

        return logger_class(channel_config)

    async def channel(self, name: str | None = None):
        """Get a log channel instance"""
        if name is None:
            name = await self.get_default_driver()

        if name not in self.channels:
            self.channels[name] = await self._resolve_channel(name)

        return self.channels[name]

    async def get_default_driver(self) -> str:
        """Get default channel name from config"""
        config = await self.app.make("config")
        return config.get("logging.default", "stack")
