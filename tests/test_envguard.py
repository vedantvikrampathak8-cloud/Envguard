"""
Tests for envguard — scanner, infer, schema, validator.
"""

import os
import json
import tempfile
from pathlib import Path

import pytest

from envguard.scanner import scan_file, scan_directory
from envguard.infer import infer_type
from envguard.schema import EnvSchema, EnvVarSchema
from envguard.validator import EnvValidator, EnvValidationError


# ---------------------------------------------------------------------------
# Scanner tests
# ---------------------------------------------------------------------------

def _write_tmp(code: str) -> str:
    f = tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8")
    f.write(code)
    f.flush()
    return f.name


class TestScanner:
    def test_os_getenv_simple(self):
        path = _write_tmp('import os\nx = os.getenv("MY_VAR")\n')
        usages = scan_file(path)
        assert len(usages) == 1
        assert usages[0].name == "MY_VAR"
        assert usages[0].is_required is True  # no default provided → not required (None default)

    def test_os_getenv_with_default(self):
        path = _write_tmp('import os\nx = os.getenv("PORT", "8080")\n')
        usages = scan_file(path)
        assert usages[0].default == "8080"
        assert usages[0].is_required is False

    def test_os_environ_subscript(self):
        path = _write_tmp('import os\nx = os.environ["SECRET_KEY"]\n')
        usages = scan_file(path)
        assert usages[0].name == "SECRET_KEY"
        assert usages[0].is_required is True

    def test_os_environ_get(self):
        path = _write_tmp('import os\nx = os.environ.get("REDIS_URL", "redis://localhost")\n')
        usages = scan_file(path)
        assert usages[0].name == "REDIS_URL"
        assert usages[0].default == "redis://localhost"

    def test_multiple_vars(self):
        code = (
            'import os\n'
            'A = os.getenv("VAR_A")\n'
            'B = os.environ["VAR_B"]\n'
            'C = os.environ.get("VAR_C", "default")\n'
        )
        path = _write_tmp(code)
        names = {u.name for u in scan_file(path)}
        assert names == {"VAR_A", "VAR_B", "VAR_C"}

    def test_syntax_error_file_skipped(self):
        path = _write_tmp("def broken(:\n")
        assert scan_file(path) == []

    def test_scan_directory(self, tmp_path):
        (tmp_path / "a.py").write_text('import os\nx = os.getenv("ALPHA")\n')
        (tmp_path / "b.py").write_text('import os\ny = os.environ["BETA"]\n')
        usages = scan_directory(str(tmp_path))
        names = {u.name for u in usages}
        assert "ALPHA" in names
        assert "BETA" in names


# ---------------------------------------------------------------------------
# Infer tests
# ---------------------------------------------------------------------------

class TestInfer:
    def test_name_port(self):
        assert infer_type("APP_PORT", "8080", "") == "int"

    def test_name_secret(self):
        assert infer_type("SECRET_KEY", None, "") == "secret"

    def test_name_url(self):
        assert infer_type("DATABASE_URL", None, "") == "url"

    def test_name_bool(self):
        assert infer_type("DEBUG", "false", "") == "bool"

    def test_context_int(self):
        assert infer_type("WORKERS", None, "n = int(os.getenv('WORKERS'))") == "int"

    def test_context_bool(self):
        assert infer_type("MYFLAG", None, "if val.lower() in ['true', 'false']:") == "bool"

    def test_default_int(self):
        assert infer_type("SOMETHING", "42", "") == "int"

    def test_default_bool(self):
        assert infer_type("SOMETHING", "true", "") == "bool"

    def test_fallback_string(self):
        assert infer_type("RANDOM_VAR", None, "") == "string"


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

class TestSchema:
    def test_roundtrip(self, tmp_path):
        schema = EnvSchema()
        schema.vars.append(EnvVarSchema(
            name="FOO", type="string", required=True, default=None,
            description="Test var", example="bar", locations=[{"file": "app.py", "line": 1}]
        ))
        out = str(tmp_path / "schema.json")
        schema.save(out)
        loaded = EnvSchema.load(out)
        assert len(loaded.vars) == 1
        assert loaded.vars[0].name == "FOO"
        assert loaded.vars[0].required is True

    def test_generate_env_example(self):
        schema = EnvSchema()
        schema.vars.append(EnvVarSchema(
            name="API_KEY", type="secret", required=True, default=None,
            description="API key", example=None, locations=[]
        ))
        example = schema.generate_env_example()
        assert "API_KEY=" in example
        assert "REQUIRED" in example

    def test_merge_var_dedup(self):
        schema = EnvSchema()
        schema.merge_var(name="X", type_="string", required=False, default="a",
                         description="d", example=None, location={"file": "a.py", "line": 1})
        schema.merge_var(name="X", type_="string", required=True,  default="a",
                         description="d", example=None, location={"file": "b.py", "line": 5})
        assert len(schema.vars) == 1
        assert schema.vars[0].required is True          # required wins
        assert len(schema.vars[0].locations) == 2       # both locations kept


# ---------------------------------------------------------------------------
# Validator tests
# ---------------------------------------------------------------------------

def _make_schema(*var_dicts) -> EnvSchema:
    schema = EnvSchema()
    for d in var_dicts:
        schema.vars.append(EnvVarSchema(**d))
    return schema


class TestValidator:
    def _schema(self, **kwargs):
        defaults = dict(name="X", type="string", required=True, default=None,
                        description="", example=None, locations=[])
        defaults.update(kwargs)
        return _make_schema(defaults)

    def test_missing_required(self):
        schema = self._schema(name="MUST_EXIST")
        v = EnvValidator(schema)
        results = v.validate_all(raise_on_error=False)
        assert results[0].ok is False

    def test_raises_on_error(self):
        schema = self._schema(name="MUST_EXIST")
        with pytest.raises(EnvValidationError):
            EnvValidator(schema).validate_all(raise_on_error=True)

    def test_valid_string(self, monkeypatch):
        monkeypatch.setenv("MY_STR", "hello")
        schema = self._schema(name="MY_STR", type="string")
        results = EnvValidator(schema).validate_all(raise_on_error=False)
        assert results[0].ok
        assert results[0].value == "hello"

    def test_int_coercion(self, monkeypatch):
        monkeypatch.setenv("MY_INT", "42")
        schema = self._schema(name="MY_INT", type="int")
        results = EnvValidator(schema).validate_all(raise_on_error=False)
        assert results[0].ok
        assert results[0].value == 42

    def test_int_invalid(self, monkeypatch):
        monkeypatch.setenv("MY_INT", "not_a_number")
        schema = self._schema(name="MY_INT", type="int")
        results = EnvValidator(schema).validate_all(raise_on_error=False)
        assert results[0].ok is False

    def test_bool_true_values(self, monkeypatch):
        for val in ("true", "True", "1", "yes", "on"):
            monkeypatch.setenv("MY_BOOL", val)
            schema = self._schema(name="MY_BOOL", type="bool")
            results = EnvValidator(schema).validate_all(raise_on_error=False)
            assert results[0].value is True

    def test_bool_false_values(self, monkeypatch):
        for val in ("false", "False", "0", "no", "off"):
            monkeypatch.setenv("MY_BOOL", val)
            schema = self._schema(name="MY_BOOL", type="bool")
            results = EnvValidator(schema).validate_all(raise_on_error=False)
            assert results[0].value is False

    def test_url_valid(self, monkeypatch):
        monkeypatch.setenv("API_URL", "https://api.example.com")
        schema = self._schema(name="API_URL", type="url")
        results = EnvValidator(schema).validate_all(raise_on_error=False)
        assert results[0].ok

    def test_url_invalid(self, monkeypatch):
        monkeypatch.setenv("API_URL", "not-a-url")
        schema = self._schema(name="API_URL", type="url")
        results = EnvValidator(schema).validate_all(raise_on_error=False)
        assert results[0].ok is False

    def test_email_valid(self, monkeypatch):
        monkeypatch.setenv("ADMIN_EMAIL", "admin@example.com")
        schema = self._schema(name="ADMIN_EMAIL", type="email")
        results = EnvValidator(schema).validate_all(raise_on_error=False)
        assert results[0].ok

    def test_secret_too_short(self, monkeypatch):
        monkeypatch.setenv("SECRET_KEY", "abc")
        schema = self._schema(name="SECRET_KEY", type="secret")
        results = EnvValidator(schema).validate_all(raise_on_error=False)
        assert results[0].ok is False

    def test_optional_absent(self):
        schema = self._schema(name="OPT_VAR", required=False, default="default_val")
        results = EnvValidator(schema).validate_all(raise_on_error=False)
        assert results[0].ok
        assert results[0].value == "default_val"
