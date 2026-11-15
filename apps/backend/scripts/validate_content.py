"""Content validation script for AgroSight game chapters, lessons, and missions."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SEEDS_CONTENT_DIR = Path(__file__).resolve().parent.parent / "seeds" / "content"

ALLOWED_MISSION_TYPES = {
    "interpret_signal",
    "choose_date",
    "choose_crop",
    "compare_areas",
    "rotation_choice",
    "replay_campaign",
    "water_decision",
    "field_observation_check",
}

ALLOWED_LANGUAGES = {"pt", "en"}


class ContentValidationError(Exception):
    """Raised when content fails validation rules."""

    pass


def validate_content_payload(data: dict[str, Any], file_path: Path | None = None) -> list[str]:
    """Validate a single chapter content payload against rules in prompt.md."""
    errors: list[str] = []
    location = f"[{file_path.name}] " if file_path else ""

    # 1. Top-level Chapter attributes
    chapter_num = data.get("chapter_number")
    if not isinstance(chapter_num, int) or not (1 <= chapter_num <= 12):
        errors.append(f"{location}chapter_number must be an integer between 1 and 12")

    title = data.get("title")
    if not title or not isinstance(title, str) or len(title.strip()) < 3:
        errors.append(f"{location}title is required and must have at least 3 characters")

    objective = data.get("learning_objective")
    if not objective or not isinstance(objective, str):
        errors.append(f"{location}learning_objective is required")

    # 2. Lessons validation
    lessons = data.get("lessons")
    if not isinstance(lessons, list) or len(lessons) == 0:
        errors.append(f"{location}at least one lesson is required")
    else:
        for idx, lesson in enumerate(lessons):
            l_prefix = f"{location}lesson #{idx + 1}: "
            if not lesson.get("title"):
                errors.append(f"{l_prefix}missing title")
            if not lesson.get("topic"):
                errors.append(f"{l_prefix}missing topic")
            if not lesson.get("text_simple"):
                errors.append(f"{l_prefix}missing text_simple")
            if not lesson.get("audio_text"):
                errors.append(f"{l_prefix}missing audio_text")
            if not lesson.get("source"):
                errors.append(
                    f"{l_prefix}missing source (agronomic/scientific source is mandatory)"
                )
            lang = lesson.get("language", "pt")
            if lang not in ALLOWED_LANGUAGES:
                errors.append(f"{l_prefix}unsupported language '{lang}'")

    # 3. Missions validation (desafios)
    missions = data.get("missions")
    if not isinstance(missions, list) or len(missions) == 0:
        errors.append(f"{location}at least one mission (desafio) is required")
    else:
        for idx, mission in enumerate(missions):
            m_prefix = f"{location}mission #{idx + 1}: "
            if not mission.get("title"):
                errors.append(f"{m_prefix}missing title")
            m_type = mission.get("mission_type")
            if m_type not in ALLOWED_MISSION_TYPES:
                allowed_str = ", ".join(sorted(ALLOWED_MISSION_TYPES))
                errors.append(
                    f"{m_prefix}invalid mission_type '{m_type}'. Allowed: [{allowed_str}]"
                )
            if not mission.get("prompt_simple"):
                errors.append(f"{m_prefix}missing prompt_simple")
            if not mission.get("learning_note"):
                errors.append(f"{m_prefix}missing learning_note")
            max_score = mission.get("max_score", 100)
            if not isinstance(max_score, int) or max_score <= 0:
                errors.append(f"{m_prefix}max_score must be a positive integer")
            lang = mission.get("language", "pt")
            if lang not in ALLOWED_LANGUAGES:
                errors.append(f"{m_prefix}unsupported language '{lang}'")

    return errors


def validate_all_content_files(content_dir: Path = SEEDS_CONTENT_DIR) -> dict[str, Any]:
    """Scan and validate all JSON content files in seeds/content directory."""
    if not content_dir.exists():
        raise FileNotFoundError(f"Content directory does not exist: {content_dir}")

    json_files = sorted(content_dir.glob("*/*.json"))
    if not json_files:
        raise FileNotFoundError(f"No content JSON files found in {content_dir}")

    all_errors: dict[str, list[str]] = {}
    valid_count = 0

    for file_path in json_files:
        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            file_errors = validate_content_payload(data, file_path=file_path)
            if file_errors:
                all_errors[str(file_path)] = file_errors
            else:
                valid_count += 1
        except Exception as exc:
            all_errors[str(file_path)] = [f"Failed to read/parse JSON: {exc}"]

    return {
        "total_files": len(json_files),
        "valid_files": valid_count,
        "failed_files": len(all_errors),
        "errors": all_errors,
    }


def main() -> None:
    """CLI execution for content validator."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="Validate AgroSight game content seeds")
    parser.add_argument(
        "--content-dir",
        type=Path,
        default=SEEDS_CONTENT_DIR,
        help="Path to seeds/content directory",
    )
    args = parser.parse_args()

    try:
        report = validate_all_content_files(content_dir=args.content_dir)
        if report["failed_files"] > 0:
            logger.error("Content validation failed for %d files:", report["failed_files"])
            for path, errs in report["errors"].items():
                logger.error("  File: %s", path)
                for err in errs:
                    logger.error("    - %s", err)
            sys.exit(1)
        else:
            logger.info("All %d content files passed validation!", report["total_files"])
    except Exception as exc:
        logger.error("Fatal error during validation: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
