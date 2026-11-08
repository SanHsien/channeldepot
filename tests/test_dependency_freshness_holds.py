"""依賴新鮮度檢查器：紅燈的兩條正當出口。

宣告是相容性承諾，不是消音鍵。某個下限**不該**跟著現行版走時，只有兩種留下理由的做法：
宣告行上的 `# freshness-hold:`（長期政策），或 `.github/dependency-deferrals.json` 記下
「這次不升 + 當時看到的版本」——PyPI 一超過那個版本，延後自動失效，報告重新問。
"""

from __future__ import annotations

import json
from pathlib import Path

import yt_fetch
from tools import check_dependency_freshness as freshness


def test_hold_marker_is_read_from_the_declaring_line(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        "[project]\n"
        "dependencies = [\n"
        '    "yt-dlp>=2026.3.17",  # freshness-hold: 跟著 EXE 打包版本走\n'
        '    "imageio-ffmpeg>=0.6.0",\n'
        "]\n",
        encoding="utf-8",
    )

    assert freshness.declared_hold("yt-dlp", pyproject) == "跟著 EXE 打包版本走"
    assert freshness.declared_hold("imageio-ffmpeg", pyproject) == ""


def test_a_comment_without_the_marker_is_not_a_hold(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\ndependencies = [\n    "yt-dlp>=2026.3.17",  # 一般註解\n]\n',
        encoding="utf-8",
    )

    assert freshness.declared_hold("yt-dlp", pyproject) == ""


def test_deferral_without_a_reviewed_release_is_ignored(tmp_path):
    # 沒有 deferredLatest 的條目等於永久靜音，直接忽略。
    path = tmp_path / "deferrals.json"
    path.write_text(json.dumps({"deferrals": {"yt-dlp": {"reason": "later"}}}), encoding="utf-8")

    assert freshness.load_deferrals(path) == {}


def test_deferral_with_a_reviewed_release_is_read(tmp_path):
    path = tmp_path / "deferrals.json"
    path.write_text(
        json.dumps(
            {
                "deferrals": {
                    "yt-dlp": {"deferredLatest": "2026.8.19", "reason": "要重打 EXE 才驗得到"}
                }
            }
        ),
        encoding="utf-8",
    )

    assert freshness.load_deferrals(path) == {"yt-dlp": ("2026.8.19", "要重打 EXE 才驗得到")}


def test_missing_deferrals_file_defers_nothing(tmp_path):
    assert freshness.load_deferrals(tmp_path / "absent.json") == {}


def test_aged_floor_needs_review_unless_held_or_deferred():
    assert freshness.needs_review({"outdated": True, "hold": "", "deferred_reason": ""})
    assert not freshness.needs_review({"outdated": True, "hold": "政策", "deferred_reason": ""})
    assert not freshness.needs_review(
        {"outdated": True, "hold": "", "deferred_reason": "已評估，等重打 EXE"}
    )


def check_yt_dlp_baseline_compatibility(pyproject: Path) -> None:
    requires_python = freshness.declared_requires_python(pyproject)
    if not freshness.supports_python_version(requires_python, "3.10"):
        return

    declared_yt_dlp = freshness.declared_minimum_version("yt-dlp", pyproject)
    assert declared_yt_dlp is not None

    # yt-dlp 2026.10.21 是支援 Python 3.10 的最後一個版本
    assert not yt_fetch.is_newer_version(
        declared_yt_dlp, "2026.10.21"
    ), f"yt-dlp 宣告基線為 {declared_yt_dlp}，高於支援 Python 3.10 的最後版本 2026.10.21"

    hold = freshness.declared_hold("yt-dlp", pyproject)
    assert (
        hold
    ), "yt-dlp 維持在支援 Python 3.10 的版本，必須在 pyproject.toml 宣告行加 # freshness-hold:"


def test_yt_dlp_baseline_compatible_with_python_310_support():
    """yt-dlp 2026.10.26 開始要求 Python >= 3.11。

    專案若支援 Python 3.10，宣告的 yt-dlp 下限不得超過 2026.10.21，
    且必須透過 freshness-hold 說明維持宣告的理由。
    """
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    assert freshness.supports_python_version(
        freshness.declared_requires_python(pyproject), "3.10"
    ), "專案目前預期涵蓋 Python 3.10"
    check_yt_dlp_baseline_compatibility(pyproject)


def test_yt_dlp_baseline_when_python_310_not_supported(tmp_path):
    """若專案不涵蓋 Python 3.10，不應阻擋高於 2026.10.21 的 yt-dlp 基線。"""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        "[project]\n"
        'requires-python = ">=3.11"\n'
        "dependencies = [\n"
        '    "yt-dlp>=2026.10.26",\n'
        "]\n",
        encoding="utf-8",
    )
    check_yt_dlp_baseline_compatibility(pyproject)
