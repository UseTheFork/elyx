Based on the codebase analysis, here's the comment standards convention:

# Elyx Comment & Documentation Standards

## Key Principles

- **Google-style docstrings** for all public methods with parameters/returns
- **One-line docstrings** for simple methods (getters, setters, property-like)
- **No docstrings** for obvious implementations (e.g., empty `pass` classes)
- **Inline comments** only for non-obvious logic (regex patterns, workarounds)

## Docstring Format

**Simple methods (one-line):**

```python
def flush(self) -> None:
    """Flush the container of all bindings and resolved instances."""
```

**Complex methods (Google-style with Args/Returns):**

```python
async def call(
    self,
    command: str,
    parameters: dict[str, Any] = {},
    output_buffer: Any | None = None,
) -> int:
    """
    Run a console command by name.

    Args:
        command: The command name to run.
        parameters: Parameters to pass to the command.
        output_buffer: Optional output buffer for capturing command output.

    Returns:
        Exit status code (0 for success, non-zero for error).
    """
```

**Class-level docstrings:**

```python
class Application(ApplicationContract):
    """Console application for handling command execution."""
```

## When to Document

**Always document:**

- Public methods with parameters or return values
- Abstract methods in contracts (even if just restating the signature)
- Class purpose (one-line at top)

**Skip docstrings for:**

- Empty pass-through classes: `class Console(BaseConsole): pass`
- `__init__` with only attribute assignment (type hints suffice)
- Private methods with obvious names (`_normalize_abstract`)

## Inline Comments

**Use for non-obvious logic:**

```python
# Extract command name (everything before first space or {)
match = re.match(r"^([^\s{]+)", self.signature)

# Handle shortcuts: {--Q|queue=}
if "|" in arg_def:
```

## Things to Avoid

- ❌ Redundant docstrings: `def get_name() -> str: """Get name."""` (type hint is enough)
- ❌ Commenting obvious code: `# Set the name` before `self.name = name`
- ❌ Outdated comments (update or remove when code changes)
- ❌ Docstrings on abstract methods that just repeat the contract
- ❌ Mentioning PHP or Laravel in comments/docs (unless explicitly requested by user)
