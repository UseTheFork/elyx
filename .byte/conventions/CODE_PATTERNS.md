# Elyx Code Patterns Convention

## Key Principles

- **Async for lifecycle, sync for resolution**: Async used post-bootstrap (boot, handle), container resolution is synchronous
- **Container-driven resolution**: Always `app.make()`, never manual instantiation
- **Callback-based lifecycle**: Lists for extensibility (booting, resolving, terminating)
- **Fluent builders**: Method chaining with `return self`
- **Use helper utilities**: Leverage `Str`, `Arr`, `Collection` for common operations instead of raw Python

## Dependency Injection

**Constructor injection for core dependencies:**

```python
class ConsoleKernel:
    def __init__(self, app: Application, **kwargs):
        self.app = app
```

**Setter injection for commands (avoid constructor DI):**

```python
class Command:
    def __init__(self):
        self._parse_signature()  # No dependencies

    def set_elyx(self, elyx: Container) -> None:
        self.elyx = elyx
```

**Auto-resolution via type hints:**

```python
for param in signature.parameters.values():
    if param.annotation is not inspect.Parameter.empty:
        dependencies[param.name] = self.make(type_to_resolve)
```

## Async/Await Patterns

**Async for application lifecycle (post-bootstrap):**

```python

async def handle(self, input: InputInterface) -> int:
    return await self.elyx.call(command, parameters)
```

**Sync for container resolution:**

```python
instance = self.make(MyClass)  # make() and resolve() are synchronous
```

**Check before invoking callbacks:**

```python
if inspect.iscoroutinefunction(callback):
    await callback(instance, self)
else:
    callback(instance, self)
```

## Error Handling

**Custom exceptions with context:**

```python
raise EntryNotFoundException(f"{msg} while building [{abstract}]") from e
```

**Graceful fallback:** Use `param.default` when resolution fails

## Callback Pattern

**Dual signature for global vs type-specific:**

```python
def resolving(self, abstract, callback: Callable | None = None):
    if callable(abstract) and callback is None:
        self._global_resolving_callbacks.append(abstract)
    else:
        self._resolving_callbacks[abstract_str].append(callback)
```

## Builder & Bootstrapper

**Fluent chaining:** `Application.configure(path).with_kernels().create()`

**Sequential bootstrap:** `for b in bootstrappers: self.make(b).bootstrap(self)`

## Type Normalization

**Always normalize abstracts using Str helper:**

```python
def _normalize_abstract(self, abstract) -> str:
    return Str.class_to_string(abstract)
```

**Unwrap Optional/Union using typing utilities:**

```python
from typing import get_args, get_origin
import types

origin = get_origin(type_to_resolve)
if origin is Union or origin is types.UnionType:
    args = get_args(type_to_resolve)
    non_none_args = [arg for arg in args if arg is not types.NoneType]
```

**Use ReflectsClosures mixin for closure inspection:**

```python
class Container(ReflectsClosures):
    def _get_closure_return_types(self, closure: Callable) -> list[type]:
        # Inherited from ReflectsClosures
        return self._closure_return_types(closure)
```

## Things to Avoid

- ❌ `MyClass()` → Use `app.make(MyClass)`
- ❌ Constructor DI in commands → Use setters
- ❌ Await without `iscoroutinefunction()` check
