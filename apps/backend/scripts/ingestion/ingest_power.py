"""CLI entry point for scheduled NASA POWER daily ingestion."""

from __future__ import annotations

import argparse
import logging
import uuid
from collections.abc import Sequence
from datetime import date

from app.core.database import get_session_factory
from app.modules.earth_observation.service import EarthObservationService
from app.modules.regions.service import RegionService


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest one NASA POWER daily variable for a region"
    )
    parser.add_argument("--region-id", type=uuid.UUID, required=True)
    parser.add_argument("--parameter", required=True, help="One POWER parameter code")
    parser.add_argument("--start", type=date.fromisoformat, required=True, help="YYYY-MM-DD")
    parser.add_argument("--end", type=date.fromisoformat, required=True, help="YYYY-MM-DD")
    parser.add_argument("--community", choices=["ag", "hy", "sb", "re"], default="ag")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args(argv)
    session = get_session_factory()()
    try:
        region_service = RegionService(session)
        map_config = region_service.get_map_config(args.region_id)
        bbox = map_config["bbox"]
        if bbox is None:
            raise ValueError(
                "Region has no boundary geometry; cannot request a POWER bounding box."
            )
        min_lon, min_lat, max_lon, max_lat = bbox
        result = EarthObservationService(session).ingest_power_daily(
            region_id=args.region_id,
            bounds=(min_lat, max_lat, min_lon, max_lon),
            parameter=args.parameter,
            start=args.start,
            end=args.end,
            community=args.community,
        )
        logging.info("POWER ingestion completed: %s", result)
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
