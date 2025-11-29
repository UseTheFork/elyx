from elyx.foundation.application import Application


class ApplicationBuilder:
    def __init__(self, application: Application):
        """Create a new application builder instance."""
        self._application = application

    def with_commands(self, commands: list = []) -> "ApplicationBuilder":
        """foo"""

        return self


# AI: How would you recomend we implment `with_commands` the below is from laravel.
# ```
# if (empty($commands)) {
#     $commands = [$this->app->path('Console/Commands')];
# }

# $this->app->afterResolving(ConsoleKernel::class, function ($kernel) use ($commands) {
#     [$commands, $paths] = (new Collection($commands))->partition(fn ($command) => class_exists($command));
#     [$routes, $paths] = $paths->partition(fn ($path) => is_file($path));

#     $this->app->booted(static function () use ($kernel, $commands, $paths, $routes) {
#         $kernel->addCommands($commands->all());
#         $kernel->addCommandPaths($paths->all());
#         $kernel->addCommandRoutePaths($routes->all());
#     });
# });
# ```
