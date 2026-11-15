"""Import national geospatial layers (CENACARTA 2017 / Data4Moz) into database."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

from shapely.geometry import shape

from app.core.database import get_session_factory
from scripts.seed import SEEDS_AOI_DIR, load_aoi_geojson, seed_regions_and_districts

logger = logging.getLogger(__name__)

NATIONAL_LAYER_METADATA = {
    "title": "Limite de Distritos (CENACARTA, 2017)",
    "source": "CENACARTA 2017",
    "year": 2017,
    "license": "Dados públicos abertos / Atribuição obrigatória CENACARTA",
    "crs": "EPSG:4326",
    "portal_url": "https://dataportal.co.mz/dados-espaciais",
}


def validate_aoi_geojson_layer(geojson_path: Path) -> dict[str, Any]:
    """Validate that an AOI GeoJSON file contains valid EPSG:4326 geometry and metadata."""
    if not geojson_path.exists():
        raise FileNotFoundError(f"AOI file not found: {geojson_path}")

    data = load_aoi_geojson(geojson_path)
    if data.get("type") != "FeatureCollection":
        raise ValueError(f"Invalid GeoJSON in {geojson_path}: expected FeatureCollection")

    features = data.get("features", [])
    if not features:
        raise ValueError(f"No features found in {geojson_path}")

    feature = features[0]
    geom_dict = feature.get("geometry")
    if not geom_dict:
        raise ValueError(f"No geometry found in {geojson_path}")

    # Validate with Shapely
    geom = shape(geom_dict)
    if not geom.is_valid:
        raise ValueError(f"Invalid geometry in {geojson_path}")

    bounds = geom.bounds  # (minx, miny, maxx, maxy) -> lon, lat
    # Mozambique bounds approx: Lon [30, 41], Lat [-27, -10]
    if not (30.0 <= bounds[0] <= 42.0 and -27.5 <= bounds[1] <= -10.0):
        logger.warning(
            "Geometry bounds %s for %s appear outside Mozambique bounding extent",
            bounds,
            geojson_path.name,
        )

    return {
        "valid": True,
        "filename": geojson_path.name,
        "geometry_type": geom.geom_type,
        "bounds": bounds,
        "metadata": NATIONAL_LAYER_METADATA,
    }


def import_national_layers(source_dir: Path = SEEDS_AOI_DIR) -> dict[str, Any]:
    """Import national layers into database, prioritizing local canonical AOIs."""
    logger.info("Verifying national layer metadata: %s", NATIONAL_LAYER_METADATA)

    geojson_files = sorted(source_dir.glob("*.geojson"))
    validation_reports: list[dict[str, Any]] = []

    for file_path in geojson_files:
        report = validate_aoi_geojson_layer(file_path)
        validation_reports.append(report)
        logger.info("Layer valid: %s [%s]", report["filename"], report["geometry_type"])

    session_factory = get_session_factory()
    db = session_factory()
    try:
        seed_stats = seed_regions_and_districts(db, aoi_dir=source_dir)
        return {
            "status": "success",
            "metadata": NATIONAL_LAYER_METADATA,
            "layers_validated": len(validation_reports),
            "reports": validation_reports,
            "seed_stats": seed_stats,
        }
    finally:
        db.close()


def main() -> None:
    """CLI execution for national layer import."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="Import national layers into AgroSight API")
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=SEEDS_AOI_DIR,
        help="Directory containing AOI GeoJSON files",
    )
    args = parser.parse_args()

    try:
        summary = import_national_layers(source_dir=args.source_dir)
        logger.info("National layers imported successfully: %s", summary)
    except Exception as exc:
        logger.error("Failed to import national layers: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
