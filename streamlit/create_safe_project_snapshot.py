from __future__ import annotations

import fnmatch
import re
from pathlib import Path


PROJECT_ROOT = Path.cwd()
OUTPUT_FILE = PROJECT_ROOT / "project_snapshot_safe.md"

MAX_FILE_SIZE_BYTES = 250_000

EXCLUDED_DIRECTORIES = {
    ".git",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
    "backups",
    "coverage",
    "htmlcov",
}

EXCLUDED_FILE_PATTERNS = {
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*.crt",
    "*.cer",
    "token.json",
    "credentials.json",
    "*service-account*.json",
    "*service_account*.json",
    "*firebase-adminsdk*.json",
    "id_rsa",
    "id_ed25519",
    "*.sqlite",
    "*.sqlite3",
    "*.db",
    OUTPUT_FILE.name,
}

ALLOWED_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".sql",
    ".json",
    ".html",
    ".css",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".sh",
    ".ps1",
}

ALLOWED_EXTENSIONLESS_FILES = {
    "Dockerfile",
    "Makefile",
    "Procfile",
}

SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"""(?ix)
    \b(
        api[_-]?key
        |secret
        |token
        |password
        |passwd
        |client[_-]?secret
        |private[_-]?key
        |access[_-]?key
    )\b
    (\s*[:=]\s*)
    (["']?)[^,\s"' }\]]+\3
    """
)

KNOWN_SECRET_PATTERN = re.compile(
    r"""(?x)
    (
        sk-[A-Za-z0-9_-]{16,}
        |AIza[A-Za-z0-9_-]{20,}
        |gh[pousr]_[A-Za-z0-9_]{20,}
        |xox[baprs]-[A-Za-z0-9-]{20,}
        |Bearer\s+[A-Za-z0-9._~+/=-]{15,}
    )
    """
)

PRIVATE_KEY_MARKERS = (
    "-----BEGIN PRIVATE KEY-----",
    "-----BEGIN RSA PRIVATE KEY-----",
    "-----BEGIN OPENSSH PRIVATE KEY-----",
)


def is_excluded_path(path: Path) -> bool:
    relative_parts = path.relative_to(PROJECT_ROOT).parts

    if any(part in EXCLUDED_DIRECTORIES for part in relative_parts):
        return True

    return any(
        fnmatch.fnmatch(path.name, pattern)
        for pattern in EXCLUDED_FILE_PATTERNS
    )


def is_allowed_file(path: Path) -> bool:
    if path.name in ALLOWED_EXTENSIONLESS_FILES:
        return True

    return path.suffix.lower() in ALLOWED_EXTENSIONS


def sanitize_content(content: str) -> str:
    if any(marker in content for marker in PRIVATE_KEY_MARKERS):
        return "[FILE CONTENT REMOVED: PRIVATE KEY DETECTED]"

    sanitized_lines: list[str] = []

    for line in content.splitlines():
        sanitized = SECRET_ASSIGNMENT_PATTERN.sub(
            lambda match: (
                f"{match.group(1)}"
                f"{match.group(2)}"
                "[REDACTED]"
            ),
            line,
        )

        sanitized = KNOWN_SECRET_PATTERN.sub(
            "[REDACTED]",
            sanitized,
        )

        sanitized_lines.append(sanitized)

    return "\n".join(sanitized_lines)


def language_for(path: Path) -> str:
    mapping = {
        ".py": "python",
        ".md": "markdown",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".sql": "sql",
        ".html": "html",
        ".css": "css",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".jsx": "jsx",
        ".sh": "bash",
        ".ps1": "powershell",
    }

    return mapping.get(path.suffix.lower(), "text")


def collect_files() -> list[Path]:
    files: list[Path] = []

    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue

        if is_excluded_path(path):
            continue

        if not is_allowed_file(path):
            continue

        try:
            if path.stat().st_size > MAX_FILE_SIZE_BYTES:
                continue
        except OSError:
            continue

        files.append(path)

    return sorted(
        files,
        key=lambda item: str(item.relative_to(PROJECT_ROOT)).lower(),
    )


def build_tree(files: list[Path]) -> str:
    return "\n".join(
        str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        for path in files
    )


def main() -> int:
    files = collect_files()

    sections = [
        "# Safe Project Snapshot",
        "",
        f"Project root: `{PROJECT_ROOT.name}`",
        f"Included files: {len(files)}",
        "",
        "## Project structure",
        "",
        "```text",
        build_tree(files),
        "```",
    ]

    included_count = 0
    failed_count = 0

    for path in files:
        relative_path = path.relative_to(PROJECT_ROOT)

        try:
            content = path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except OSError as exc:
            failed_count += 1
            sections.extend(
                [
                    "",
                    f"## `{relative_path}`",
                    "",
                    f"[READ FAILED: {type(exc).__name__}]",
                ]
            )
            continue

        sanitized = sanitize_content(content)

        sections.extend(
            [
                "",
                f"## `{str(relative_path).replace(chr(92), '/')}`",
                "",
                f"```{language_for(path)}",
                sanitized,
                "```",
            ]
        )

        included_count += 1

    OUTPUT_FILE.write_text(
        "\n".join(sections) + "\n",
        encoding="utf-8",
    )

    print(f"[PASS] Snapshot created: {OUTPUT_FILE}")
    print(f"[INFO] Files included: {included_count}")
    print(f"[INFO] Files unreadable: {failed_count}")
    print("")
    print("IMPORTANT: Manually inspect the output before uploading it.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())