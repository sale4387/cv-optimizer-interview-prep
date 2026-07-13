from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Callable

from services.candidate_profile_service import (
    get_default_candidate_profile,
    list_candidate_options,
    load_candidate_cv,
)


APP_PATH = Path("streamlit/app.py")


def read_app() -> str:
    if not APP_PATH.exists():
        raise FileNotFoundError(
            "streamlit/app.py was not found."
        )

    return APP_PATH.read_text(
        encoding="utf-8"
    )


def count_sidebar_optimize_buttons(
    app_text: str,
) -> int:
    return len(
        re.findall(
            r"st\.sidebar\.button\(\s*[\"']Optimize CV[\"']",
            app_text,
        )
    )


def test_cv_landing_file_exists() -> None:
    assert Path("ui/cv_landing.py").exists()


def test_cv_landing_imports() -> None:
    from ui.cv_landing import render_cv_landing_page

    assert callable(render_cv_landing_page)


def test_default_profile_is_sale() -> None:
    default_profile = get_default_candidate_profile()

    assert default_profile.profile_id == "sale"


def test_profiles_sale_and_svetlana_available() -> None:
    profiles = list_candidate_options()
    profile_ids = {
        profile.profile_id
        for profile in profiles
    }

    assert "sale" in profile_ids
    assert "svetlana" in profile_ids


def test_sale_cv_loads() -> None:
    cv = load_candidate_cv("sale")

    assert cv.profile_id == "sale"


def test_svetlana_cv_loads() -> None:
    cv = load_candidate_cv("svetlana")

    assert cv.profile_id == "svetlana"


def test_app_imports_cv_landing() -> None:
    app_text = read_app()

    assert "render_cv_landing_page" in app_text


def test_app_has_cv_first_route() -> None:
    app_text = read_app()

    assert 'page == "cv"' in app_text
    assert "render_cv_landing_page()" in app_text


def test_app_has_optimize_route() -> None:
    app_text = read_app()

    assert 'page == "optimize"' in app_text
    assert "_render_optimize_page()" in app_text


def test_app_default_page_is_cv() -> None:
    app_text = read_app()

    assert (
        'get("page", "cv")' in app_text
        or "get('page', 'cv')" in app_text
        or 'get("page") or "cv"' in app_text
        or "get('page') or 'cv'" in app_text
    )


def test_app_not_defaulting_to_optimize() -> None:
    app_text = read_app()

    forbidden_fragments = [
        'get("page", "optimize")',
        "get('page', 'optimize')",
        'get("page") or "optimize"',
        "get('page') or 'optimize'",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in app_text


def test_sidebar_has_current_cv_button() -> None:
    app_text = read_app()

    assert '"Current CV"' in app_text


def test_sidebar_has_only_one_optimize_cv_button() -> None:
    app_text = read_app()

    count = count_sidebar_optimize_buttons(
        app_text
    )

    assert count == 1, (
        f"Expected exactly one sidebar Optimize CV button, found {count}."
    )


def test_sidebar_buttons_have_keys() -> None:
    app_text = read_app()

    sidebar_button_blocks = re.findall(
        r"st\.sidebar\.button\([\s\S]*?\):",
        app_text,
    )

    assert sidebar_button_blocks, (
        "No sidebar buttons were found."
    )

    for block in sidebar_button_blocks:
        assert "key=" in block, (
            "A sidebar button is missing a unique key."
        )


def test_optimize_form_reads_profile_query_param() -> None:
    app_text = read_app()

    assert "requested_profile_id" in app_text
    assert "default_profile_index" in app_text
    assert "index=default_profile_index" in app_text


TESTS: list[
    tuple[str, Callable[[], None]]
] = [
    (
        "CV landing file exists",
        test_cv_landing_file_exists,
    ),
    (
        "CV landing imports",
        test_cv_landing_imports,
    ),
    (
        "Default profile is sale",
        test_default_profile_is_sale,
    ),
    (
        "Profiles sale and svetlana available",
        test_profiles_sale_and_svetlana_available,
    ),
    (
        "Sale CV loads",
        test_sale_cv_loads,
    ),
    (
        "Svetlana CV loads",
        test_svetlana_cv_loads,
    ),
    (
        "App imports CV landing",
        test_app_imports_cv_landing,
    ),
    (
        "App has CV-first route",
        test_app_has_cv_first_route,
    ),
    (
        "App has optimize route",
        test_app_has_optimize_route,
    ),
    (
        "App default page is CV",
        test_app_default_page_is_cv,
    ),
    (
        "App does not default to optimize",
        test_app_not_defaulting_to_optimize,
    ),
    (
        "Sidebar has Current CV button",
        test_sidebar_has_current_cv_button,
    ),
    (
        "Sidebar has only one Optimize CV button",
        test_sidebar_has_only_one_optimize_cv_button,
    ),
    (
        "Sidebar buttons have keys",
        test_sidebar_buttons_have_keys,
    ),
    (
        "Optimize form reads profile query param",
        test_optimize_form_reads_profile_query_param,
    ),
]


def main() -> int:
    passed = 0
    failed = 0

    for test_name, test_function in TESTS:
        try:
            test_function()

        except Exception as error:
            failed += 1
            print(
                f"[FAIL] {test_name} — "
                f"{type(error).__name__}: {error}"
            )

        else:
            passed += 1
            print(f"[PASS] {test_name}")

    print()
    print(
        f"Result: {passed} passed, {failed} failed"
    )

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
