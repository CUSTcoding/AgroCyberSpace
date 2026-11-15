"""Unit tests for content seed schema validation and chapter seed loader."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from scripts.seed import SEEDS_CONTENT_DIR, seed_chapters_and_content
from scripts.validate_content import (
    ALLOWED_MISSION_TYPES,
    validate_all_content_files,
    validate_content_payload,
)


def test_all_content_files_valid() -> None:
    """Verify that all 32 generated seed JSON files pass content schema validation."""
    report = validate_all_content_files(SEEDS_CONTENT_DIR)
    assert report["total_files"] == 32
    assert report["failed_files"] == 0
    assert report["valid_files"] == 32
    assert len(report["errors"]) == 0


def test_gaza_chapter_4_the_hidden_water() -> None:
    """Verify special requirement: Gaza Chapter 4 is 'The Hidden Water' with provisional=False."""
    gaza_ch4_file = SEEDS_CONTENT_DIR / "4" / "gaza.json"
    assert gaza_ch4_file.exists()

    with gaza_ch4_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["chapter_number"] == 4
    assert data["title"] == "The Hidden Water"
    assert data["provisional"] is False
    assert data["missions"][0]["mission_type"] == "water_decision"


def test_common_chapters_structure() -> None:
    """Verify chapters 1 and 2 are marked is_common=True."""
    for ch in [1, 2]:
        file_path = SEEDS_CONTENT_DIR / str(ch) / "common.json"
        assert file_path.exists()
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["is_common"] is True
        assert data["region_code"] == "common"


def test_validate_content_payload_missing_lesson() -> None:
    """Test validation catches missing lessons."""
    payload: dict[str, Any] = {
        "chapter_number": 3,
        "title": "Capítulo 3",
        "learning_objective": "Objetivo",
        "lessons": [],
        "missions": [
            {
                "title": "M1",
                "mission_type": "interpret_signal",
                "prompt_simple": "P",
                "learning_note": "N",
            }
        ],
    }
    errors = validate_content_payload(payload)
    assert any("at least one lesson is required" in e for e in errors)


def test_validate_content_payload_missing_source() -> None:
    """Test validation catches missing agronomic/scientific source."""
    payload: dict[str, Any] = {
        "chapter_number": 3,
        "title": "Capítulo 3",
        "learning_objective": "Objetivo",
        "lessons": [
            {
                "title": "L1",
                "topic": "climate",
                "text_simple": "Texto",
                "audio_text": "Audio",
                # missing source
            }
        ],
        "missions": [
            {
                "title": "M1",
                "mission_type": "interpret_signal",
                "prompt_simple": "P",
                "learning_note": "N",
            }
        ],
    }
    errors = validate_content_payload(payload)
    assert any("missing source" in e for e in errors)


def test_validate_content_payload_invalid_mission_type() -> None:
    """Test validation rejects invalid mission types."""
    payload: dict[str, Any] = {
        "chapter_number": 3,
        "title": "Capítulo 3",
        "learning_objective": "Objetivo",
        "lessons": [
            {
                "title": "L1",
                "topic": "climate",
                "text_simple": "Texto",
                "audio_text": "Audio",
                "source": "IIAM",
            }
        ],
        "missions": [
            {
                "title": "M1",
                "mission_type": "invalid_mini_game",  # forbidden
                "prompt_simple": "P",
                "learning_note": "N",
            }
        ],
    }
    errors = validate_content_payload(payload)
    assert any("invalid mission_type" in e for e in errors)


def test_allowed_mission_types_match_contract() -> None:
    """Ensure permitted mission types strictly align with section 8 of prompt.md."""
    expected = {
        "interpret_signal",
        "choose_date",
        "choose_crop",
        "compare_areas",
        "rotation_choice",
        "replay_campaign",
        "water_decision",
        "field_observation_check",
    }
    assert ALLOWED_MISSION_TYPES == expected


def test_seed_chapters_and_content_function(tmp_path: Path) -> None:
    """Test seed loader function executes idempotently with mock database."""
    mock_db = MagicMock()

    # Mock lookups
    mock_db.scalars.return_value.first.return_value = None
    mock_db.scalars.return_value.all.return_value = []

    stats = seed_chapters_and_content(mock_db, content_dir=SEEDS_CONTENT_DIR)
    assert stats["chapters_seeded"] >= 1
    assert stats["lessons_seeded"] >= 1
    assert stats["missions_seeded"] >= 1
