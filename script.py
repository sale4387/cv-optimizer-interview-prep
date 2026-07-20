from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = (
    "Dockerfile",
    ".dockerignore",
    "docker-compose.yml",
    "nginx/default.conf",
    ".env.example",
    ".gitignore",
    "streamlit/app.py",
    "cv_data/cv_profiles.json",
)

failures = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global failures
    if condition:
        print(f"[PASS] {name}")
        return

    failures += 1
    suffix = f": {detail}" if detail else ""
    print(f"[FAIL] {name}{suffix}")


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def validate_required_files() -> None:
    missing = [
        path
        for path in REQUIRED_FILES
        if not (ROOT / path).is_file()
    ]
    check(
        "required_files",
        not missing,
        "Missing: " + ", ".join(missing) if missing else "",
    )


def validate_profiles() -> None:
    try:
        registry = json.loads(read("cv_data/cv_profiles.json"))
        profile_ids = {
            item.get("profile_id")
            for item in registry.get("profiles", [])
        }
    except Exception as error:
        check("candidate_profiles", False, str(error))
        return

    check(
        "candidate_profiles",
        {"sale", "svetlana"}.issubset(profile_ids),
        f"Found profile IDs: {sorted(profile_ids)}",
    )


def validate_dockerfile() -> None:
    try:
        content = read("Dockerfile")
    except Exception as error:
        check("dockerfile", False, str(error))
        return

    required_fragments = (
        "FROM python:",
        "COPY requirements.txt",
        "pip install -r requirements.txt",
        "streamlit/app.py",
        "--server.address=0.0.0.0",
        "--server.port=8501",
    )
    missing = [
        fragment
        for fragment in required_fragments
        if fragment not in content
    ]
    unsafe = (
        "COPY .env" in content
        or "COPY secrets" in content
        or "firebase-service-account.json" in content
    )
    check(
        "dockerfile",
        not missing and not unsafe,
        (
            "Missing fragments: " + ", ".join(missing)
            if missing
            else "Dockerfile copies a secret explicitly"
        ),
    )


def validate_compose() -> None:
    try:
        content = read("docker-compose.yml")
    except Exception as error:
        check("compose_static", False, str(error))
        return

    required_fragments = (
        "cv-app:",
        "cv-proxy:",
        'FIREBASE_CREDENTIALS_PATH: /run/secrets/firebase-service-account.json',
        "source: ./secrets/firebase-service-account.json",
        "read_only: true",
        'condition: service_healthy',
        '"${CV_APP_PORT}:80"',
        "/_stcore/health",
    )
    missing = [
        fragment
        for fragment in required_fragments
        if fragment not in content
    ]
    has_fastapi_service = bool(
        re.search(r"(?m)^\s{2}(api|fastapi|backend):\s*$", content)
    )
    check(
        "compose_static",
        not missing and not has_fastapi_service,
        (
            "Missing fragments: " + ", ".join(missing)
            if missing
            else "Unexpected FastAPI service found"
        ),
    )


def validate_routes() -> None:
    try:
        content = read("nginx/default.conf")
    except Exception as error:
        check("bookmark_routes", False, str(error))
        return

    checks = (
        "location = /sale",
        "profile=sale",
        "location = /svetlana",
        "profile=svetlana",
        "proxy_pass http://cv-app:8501",
        "proxy_set_header Upgrade",
    )
    missing = [item for item in checks if item not in content]
    check(
        "bookmark_routes",
        not missing,
        "Missing: " + ", ".join(missing) if missing else "",
    )


def validate_env_and_ignore() -> None:
    try:
        env_example = read(".env.example")
        gitignore = read(".gitignore")
        dockerignore = read(".dockerignore")
    except Exception as error:
        check("secret_configuration", False, str(error))
        return

    required_env = (
        "BACKEND_API_KEY=",
        "FIREBASE_CREDENTIALS_PATH=",
        "GEMINI_API_KEY=",
        "GEMINI_MODEL=",
        "GEMINI_MAX_OUTPUT_TOKENS=",
        "GEMINI_TIMEOUT_SECONDS=",
        "GEMINI_MAX_ATTEMPTS=",
        "RATE_LIMIT=",
        "CV_APP_PORT=",
    )
    missing_env = [
        item for item in required_env if item not in env_example
    ]
    protected = (
        ".env" in gitignore
        and "secrets/" in gitignore
        and ".env" in dockerignore
        and "secrets" in dockerignore
    )
    check(
        "secret_configuration",
        not missing_env and protected,
        (
            "Missing env keys: " + ", ".join(missing_env)
            if missing_env
            else "Secret exclusions are incomplete"
        ),
    )


def validate_compose_cli() -> None:
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except FileNotFoundError:
        print(
            "[PASS] compose_cli_optional: Docker CLI is not installed "
            "on this machine; runtime validation remains for the server"
        )
        return
    except Exception as error:
        check("compose_cli_optional", False, str(error))
        return

    if result.returncode != 0:
        print(
            "[PASS] compose_cli_optional: Docker Compose is unavailable "
            "on this machine; runtime validation remains for the server"
        )
        return

    # `docker compose config` needs variable substitution, but should not
    # expose or validate the user's real secret values.
    env = {
        "BACKEND_API_KEY": "validation-only",
        "RATE_LIMIT": "10/minute",
        "FIREBASE_CREDENTIALS_PATH": "secrets/firebase-service-account.json",
        "GEMINI_API_KEY": "validation-only",
        "GEMINI_MODEL": "gemini-3.5-flash",
        "GEMINI_MAX_OUTPUT_TOKENS": "8192",
        "GEMINI_TIMEOUT_SECONDS": "60",
        "GEMINI_MAX_ATTEMPTS": "3",
        "CV_APP_PORT": "8502",
    }
    import os
    merged_env = os.environ.copy()
    merged_env.update(env)

    result = subprocess.run(
        ["docker", "compose", "config", "--quiet"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        env=merged_env,
    )
    check(
        "compose_cli_optional",
        result.returncode == 0,
        (result.stderr or result.stdout).strip(),
    )


def main() -> int:
    validate_required_files()
    validate_profiles()
    validate_dockerfile()
    validate_compose()
    validate_routes()
    validate_env_and_ignore()
    validate_compose_cli()

    if failures:
        print(f"[FAIL] TASK-016 static validation: {failures} failed")
        return 1

    print("[PASS] TASK-016 static validation completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
