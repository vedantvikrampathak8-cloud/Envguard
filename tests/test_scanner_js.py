"""
Tests for envguard.scanner_js — JavaScript / TypeScript env var detection.
"""

import tempfile
from pathlib import Path

from envguard.scanner_js import scan_js_file, scan_js_directory


def _tmp(code: str, ext: str = ".js") -> str:
    f = tempfile.NamedTemporaryFile(suffix=ext, mode="w", delete=False, encoding="utf-8")
    f.write(code)
    f.flush()
    return f.name


class TestJsScanner:
    def test_dot_access(self):
        path = _tmp("const x = process.env.MY_VAR;\n")
        usages = scan_js_file(path)
        assert any(u.name == "MY_VAR" for u in usages)

    def test_bracket_single_quote(self):
        path = _tmp("const x = process.env['SECRET_KEY'];\n")
        usages = scan_js_file(path)
        assert any(u.name == "SECRET_KEY" for u in usages)

    def test_bracket_double_quote(self):
        path = _tmp('const x = process.env["DATABASE_URL"];\n')
        usages = scan_js_file(path)
        assert any(u.name == "DATABASE_URL" for u in usages)

    def test_nullish_coalescing_default(self):
        path = _tmp("const port = process.env.PORT ?? '3000';\n")
        usages = scan_js_file(path)
        u = next(u for u in usages if u.name == "PORT")
        assert u.default == "3000"
        assert u.is_required is False

    def test_or_default(self):
        path = _tmp("const level = process.env.LOG_LEVEL || 'info';\n")
        usages = scan_js_file(path)
        u = next(u for u in usages if u.name == "LOG_LEVEL")
        assert u.default == "info"

    def test_required_no_default(self):
        path = _tmp("const secret = process.env.JWT_SECRET;\n")
        usages = scan_js_file(path)
        u = next(u for u in usages if u.name == "JWT_SECRET")
        assert u.is_required is True
        assert u.default is None

    def test_destructuring(self):
        path = _tmp("const { AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY } = process.env;\n")
        usages = scan_js_file(path)
        names = {u.name for u in usages}
        assert "AWS_ACCESS_KEY_ID" in names
        assert "AWS_SECRET_ACCESS_KEY" in names

    def test_vite_import_meta_env(self):
        path = _tmp("const url = import.meta.env.VITE_API_URL;\n", ext=".ts")
        usages = scan_js_file(path)
        assert any(u.name == "VITE_API_URL" for u in usages)

    def test_comment_line_skipped(self):
        path = _tmp("// const x = process.env.IGNORE_ME;\n")
        usages = scan_js_file(path)
        assert not any(u.name == "IGNORE_ME" for u in usages)

    def test_dedup_within_file(self):
        code = (
            "const a = process.env.REPEATED;\n"
            "const b = process.env.REPEATED;\n"
        )
        path = _tmp(code)
        usages = scan_js_file(path)
        assert sum(1 for u in usages if u.name == "REPEATED") == 1

    def test_multiple_vars(self):
        code = (
            "const a = process.env.ALPHA;\n"
            "const b = process.env['BETA'];\n"
            'const c = process.env["GAMMA"] ?? "default";\n'
        )
        path = _tmp(code)
        names = {u.name for u in scan_js_file(path)}
        assert names == {"ALPHA", "BETA", "GAMMA"}

    def test_ts_file(self):
        code = "const key: string = process.env.API_KEY!;\n"
        path = _tmp(code, ext=".ts")
        usages = scan_js_file(path)
        assert any(u.name == "API_KEY" for u in usages)

    def test_tsx_file(self):
        code = "const base = process.env.REACT_APP_BASE_URL ?? 'http://localhost';\n"
        path = _tmp(code, ext=".tsx")
        usages = scan_js_file(path)
        u = next(u for u in usages if u.name == "REACT_APP_BASE_URL")
        assert u.default == "http://localhost"

    def test_scan_directory(self, tmp_path):
        (tmp_path / "a.js").write_text("const x = process.env.ALPHA;\n")
        (tmp_path / "b.ts").write_text("const y = process.env.BETA ?? 'val';\n")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "c.tsx").write_text("const z = process.env['GAMMA'];\n")
        usages = scan_js_directory(str(tmp_path))
        names = {u.name for u in usages}
        assert {"ALPHA", "BETA", "GAMMA"}.issubset(names)

    def test_node_modules_excluded(self, tmp_path):
        nm = tmp_path / "node_modules" / "some_pkg"
        nm.mkdir(parents=True)
        (nm / "index.js").write_text("const x = process.env.SHOULD_IGNORE;\n")
        (tmp_path / "app.js").write_text("const x = process.env.APP_VAR;\n")
        usages = scan_js_directory(str(tmp_path))
        names = {u.name for u in usages}
        assert "SHOULD_IGNORE" not in names
        assert "APP_VAR" in names
