# Changelog

All notable changes to envguard will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Planned
- JavaScript / TypeScript support (`process.env.VAR`)
- Docker Compose `environment:` block scanning
- Pre-commit hook integration
- VS Code extension

---

## [0.1.0] - 2024-01-01

### Added
- **AST-based scanner** — detects `os.getenv`, `os.environ[...]`, and `os.environ.get(...)` across entire codebases
- **Type inference engine** — infers `int`, `float`, `bool`, `url`, `path`, `secret`, `email`, `string` from usage context, default values, and variable name patterns
- **Schema generation** — produces `.env.schema.json` (machine-readable) and `.env.example` (human-readable template)
- **Runtime validator** — validates live environment at app startup with coercion and clear error messages
- **CLI commands**: `scan`, `check`, `audit`, `diff`
- **Python API**: `envguard.validate()`, `EnvSchema`, `EnvValidator`, `scan_directory()`
- **Rich terminal output** — coloured tables, status badges, secret masking in audit view
- **31 tests** covering scanner, infer, schema, and validator modules
- **GitHub Actions CI** workflow template
