from elyx.console.command import Command


class TestCommand(Command):
    """A simple test command to verify the setup is working."""

    signature: str = """test {user} {--queue : Whether the job should be queued}"""

    description: str = "Test command to verify setup"

    async def handle(self):
        """Execute the test command."""

        # config = await self.elyx.app.make("config")
        # app_name = config.string("app.name")

        # config = self.get_elyx()
        config = await self.get_elyx().make("config")
        print(config.all())

        print(123)
        print(123)
        print(self.options())
        print(123)

        return 0
