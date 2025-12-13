from elyx.console.command import Command
from elyx.support.facades.config import Config


class AboutCommand(Command):
    """foo"""

    signature: str = """about {--only= : The section to display} {--json : Output the information as JSON}"""

    description: str = "Display basic information about your application"

    async def handle(self):
        """Execute the test command."""
        config = self.get_elyx().make("config")
        print(config.all())

        config = await self._gather_application_information()

        return 0

    async def _gather_application_information(self):
        app_name = Config.get("app.name")

        print(123)
        print(app_name)
        print(app_name)
        print(app_name)

        return 0
