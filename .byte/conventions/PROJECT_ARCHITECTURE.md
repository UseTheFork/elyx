# Elyx Architecture Convention

## Key Principles
- **Laravel-inspired layered architecture**: Foundation → Console → Commands
- **Contract-first design**: Abstract contracts define interfaces, concrete implementations follow
- **Dependency injection everywhere**: Container-based resolution, no manual instantiation
- **Async by default**: All resolution and execution paths support async/await

## Directory Structure

**Core framework (`elyx/src/elyx/`):**
```
contracts/          # Abstract contracts (interfaces)
  ├── console/      # Console-related contracts
  ├── container/    # DI container contracts
foundation/         # Core application layer
  ├── bootstrap/    # Bootstrap classes
  ├── configuration/# Builder patterns
console/            # Console implementation
support/            # Shared utilities (ServiceProvider)
```

**User application (`example/`):**
```
app/console/commands/   # User commands (auto-discovered)
bootstrap/providers.py  # Provider registration list
```

## Dependency Patterns

**Container inheritance:** `Application(Container)` extends `Container(DynamicContainer, ContainerContract)`

**Kernel receives Application:**
```python
class ConsoleKernel(KernelContract):
    def __init__(self, app: Application):
        self.app = app
```

**Commands use setter injection (not constructor):**
```python
class Command(CommandContract):
    def __init__(self):
        # No dependencies - parse signature only
        pass
    
    def set_elyx(self, elyx: ContainerContract) -> None:
        self.elyx = elyx
```

## Separation of Concerns

**Contracts (`contracts/`):** Pure ABCs with `@abstractmethod`, no implementation

**Foundation (`foundation/`):** Application lifecycle (bootstrap, boot, providers), builder pattern

**Console (`console/`):** Command parsing/execution, signature DSL `{user} {--queue}`, no business logic

**Support (`support/`):** Base classes for user extension (`ServiceProvider`)

## Key Patterns

**Bootstrap pattern:** Bootstrappers mutate Application via `bootstrap(app)` method
```python
class RegisterProviders:
    async def bootstrap(self, app: Application) -> None:
        for provider_class in self._get_providers(app):
            provider = await app.make(provider_class, app=app)
            await provider.register()
```

**Builder pattern:**
```python
Application.configure(base_path).with_kernels().with_commands([]).create()
```

**Auto-discovery:** Scan `app/console/commands/*.py` for classes with `handle()` method

## Things to Avoid
- ❌ Dependencies in Command `__init__` (use setter)
- ❌ Circular imports (use `TYPE_CHECKING`)
- ❌ Bypass container (always `app.make()`)
