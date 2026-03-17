# envguard 🛡️

**Intelligent environment variable scanner and validator for Python projects.**

`envguard` statically analyses your codebase to find every `os.getenv` / `os.environ` usage, infers types automatically, generates a typed `.env.schema.json` + `.env.example`, and validates your live environment at startup with clear, actionable error messages.

No more "KeyError: 'DATABASE_URL'" in production. No more hand-maintained `.env.example` files that drift from reality.

---

## Why envguard?

| Tool | Loads `.env` | Validates types | Scans codebase | Auto-generates schema |
|------|:---:|:---:|:---:|:---:|
| `python-dotenv` | ✅ | ❌ | ❌ | ❌ |
| `pydantic-settings` | ✅ | ✅ | ❌ | ❌ |
| `environs` | ✅ | ✅ | ❌ | ❌ |
| **envguard** | optional | ✅ | ✅ | ✅ |

envguard is the **discovery layer** — it tells you what env vars your codebase *actually* needs, and then validates them at runtime.

---

## Install

```bash
pip install envguard

# With python-dotenv support (optional)
pip install "envguard[dotenv]"
```

---

## Quick start

### 1. Scan your codebase

```bash
envguard scan ./src
```

```
Found 24 environment variables
╭───────────────────────┬────────┬────────────┬─────────────────────┬───────────╮
│ Variable              │ Type   │ Required   │ Default             │ Locations │
├───────────────────────┼────────┼────────────┼─────────────────────┼───────────┤
│ DATABASE_URL          │ url    │ ✓ required │ —                   │ db.py:12  │
│ SECRET_KEY            │ secret │ ✓ required │ —                   │ auth.py:5 │
│ DEBUG                 │ bool   │ optional   │ false               │ app.py:3  │
│ APP_PORT              │ int    │ optional   │ 8080                │ app.py:4  │
│ ...                   │ ...    │ ...        │ ...                 │ ...       │
╰───────────────────────┴────────┴────────────┴─────────────────────┴───────────╯

✓ Schema  → .env.schema.json
✓ Example → .env.example
```

### 2. Commit the generated files

```bash
git add .env.schema.json .env.example
git commit -m "chore: add envguard schema"
```

### 3. Validate at startup

```python
# app.py or main.py
import envguard
envguard.validate()   # raises EnvValidationError with clear messages if anything is wrong

# ... rest of your app
```

Or from the CLI:

```bash
envguard check
```

---

## CLI reference

```
envguard scan [PATH]      Scan codebase → .env.schema.json + .env.example
envguard check            Validate current env against schema
envguard audit            Full audit table with value previews (secrets masked)
envguard diff [PATH]      Show vars in code but missing from schema (schema drift)
```

### `envguard scan`

```bash
envguard scan ./src
envguard scan . --output custom-schema.json --example .env.template
```

Scans all `.py` files, infers types, and generates:
- `.env.schema.json` — machine-readable schema (commit this)
- `.env.example` — human-readable template (commit this)

### `envguard check`

```bash
envguard check
envguard check --schema custom-schema.json
envguard check --load-dotenv          # load .env file first
```

Exits with code 1 and shows a diff table if validation fails. Perfect for CI.

### `envguard audit`

```bash
envguard audit --load-dotenv
```

Shows every variable, its type, status, and a value preview (secrets are masked).

### `envguard diff`

```bash
envguard diff ./src
```

Compares code usage against schema — useful when you add new env vars and want to know what's missing.

---

## Type inference

envguard infers variable types from three signals (in priority order):

| Signal | Example |
|--------|---------|
| **Usage context** | `int(os.getenv("PORT"))` → `int` |
| **Default value** | `os.getenv("DEBUG", "true")` → `bool` |
| **Variable name** | `SECRET_KEY`, `API_TOKEN`, `PASSWORD` → `secret` |

### Supported types

| Type | Validation | Name patterns |
|------|-----------|---------------|
| `string` | passthrough | (fallback) |
| `int` | `int()` cast | `PORT`, `WORKERS`, `TIMEOUT`, `MAX_*` |
| `float` | `float()` cast | |
| `bool` | `true/false/1/0/yes/no/on/off` | `DEBUG`, `ENABLED`, `USE_*`, `IS_*` |
| `url` | must start with `http://` or `https://` | `DATABASE_URL`, `REDIS_URL`, `HOST` |
| `path` | passthrough | `PATH`, `DIR`, `FILE` |
| `secret` | must be ≥ 8 chars | `SECRET`, `TOKEN`, `KEY`, `PASSWORD` |
| `email` | basic format check | `EMAIL`, `MAIL` |

---

## Python API

### Runtime validation

```python
import envguard

# Raises EnvValidationError if anything is wrong
envguard.validate()

# Soft check — returns list of ValidationResult
results = envguard.validate(raise_on_error=False)
for r in results:
    if not r.ok:
        print(f"{r.name}: {r.error}")
```

### Programmatic scanning

```python
from envguard import scan_directory, infer_type

usages = scan_directory("./src")
for u in usages:
    print(u.name, u.file, u.line, infer_type(u.name, u.default, u.context))
```

### Working with schema directly

```python
from envguard import EnvSchema, EnvValidator

schema = EnvSchema.load(".env.schema.json")

# Validate specific variable
validator = EnvValidator(schema)
result = validator.validate_one("DATABASE_URL")
print(result.ok, result.value, result.error)
```

---

## Schema format

`.env.schema.json` is a plain JSON file — easy to parse in any language or CI system.

```json
{
  "version": "1.0",
  "vars": [
    {
      "name": "DATABASE_URL",
      "type": "url",
      "required": true,
      "default": null,
      "description": "Detected in app/db.py",
      "example": "postgres://user:password@localhost:5432/mydb",
      "locations": [
        { "file": "app/db.py", "line": 12 }
      ]
    }
  ]
}
```

You can hand-edit the schema to add descriptions, override inferred types, or mark optional vars as required.

---

## CI integration

Add to your CI pipeline to catch missing env vars before deployment:

```yaml
# .github/workflows/ci.yml
- name: Validate environment
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    SECRET_KEY: ${{ secrets.SECRET_KEY }}
    # ... other secrets
  run: envguard check
```

Or check for schema drift (new env vars added to code but not documented):

```yaml
- name: Check schema drift
  run: |
    envguard diff ./src
    git diff --exit-code .env.schema.json   # fail if schema changed
```

---

## What envguard detects

```python
import os

# All of these are detected:
os.getenv("VAR_A")                    # required (no default)
os.getenv("VAR_B", "default")         # optional, default="default"
os.environ["VAR_C"]                   # required
os.environ.get("VAR_D", "fallback")   # optional, default="fallback"

# Type inference from context:
port = int(os.getenv("PORT", "8080"))     # → type: int
debug = os.getenv("DEBUG", "false")       # → type: bool (name pattern)
db = os.environ["DATABASE_URL"]           # → type: url (name pattern)
key = os.environ["SECRET_KEY"]            # → type: secret (name pattern)
```

---

## Roadmap

- [ ] JavaScript / TypeScript support (`process.env.VAR`)
- [ ] Docker Compose `environment:` block scanning
- [ ] GitHub Actions secrets integration
- [ ] Pre-commit hook
- [ ] VS Code extension

---

## Contributing

```bash
git clone https://github.com/yourusername/envguard
cd envguard
pip install -e ".[dev]"
pytest
```

PRs welcome! Please open an issue first for large changes.

---

## License

MIT
