"""NASA POWER Daily API client for scheduled ingestion jobs."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from math import isfinite
from typing import Any

import httpx

NASA_POWER_DAILY_REGIONAL_URL = "https://power.larc.nasa.gov/api/temporal/daily/regional"


class NasaPowerError(RuntimeError):
    """Raised when NASA POWER returns an unusable response."""


class NasaPowerClient:
    """Fetch one daily POWER parameter for a requested bounding box."""

    def __init__(
        self,
        client: httpx.Client | None = None,
        base_url: str = NASA_POWER_DAILY_REGIONAL_URL,
    ) -> None:
        self.client = client or httpx.Client(timeout=30.0)
        self.base_url = base_url

    def fetch_daily_regional(
        self,
        *,
        parameter: str,
        latitude_min: float,
        latitude_max: float,
        longitude_min: float,
        longitude_max: float,
        start: date,
        end: date,
        community: str,
    ) -> dict[str, Any]:
        """Fetch a regional JSON time series without interpreting the values."""
        self._validate_request(
            parameter,
            latitude_min,
            latitude_max,
            longitude_min,
            longitude_max,
            start,
            end,
            community,
        )
        response = self.client.get(
            self.base_url,
            params={
                "parameters": parameter,
                "community": community.lower(),
                "latitude-min": latitude_min,
                "latitude-max": latitude_max,
                "longitude-min": longitude_min,
                "longitude-max": longitude_max,
                "start": start.strftime("%Y%m%d"),
                "end": end.strftime("%Y%m%d"),
                "format": "JSON",
                "time-standard": "UTC",
            },
        )
        if response.status_code == 429:
            raise NasaPowerError("NASA POWER rate limit reached; retry in a later ingestion run.")
        try:
            response.raise_for_status()
            payload: dict[str, Any] = response.json()
        except (httpx.HTTPError, ValueError) as err:
            raise NasaPowerError("NASA POWER request failed or returned invalid JSON.") from err

        features = payload.get("features")
        parameters = payload.get("parameters")
        if not isinstance(features, list) or not features:
            raise NasaPowerError("NASA POWER regional response contains no grid-cell features.")
        if not isinstance(parameters, dict) or parameter not in parameters:
            raise NasaPowerError("NASA POWER response does not describe the requested parameter.")
        return payload

    @staticmethod
    def parse_regional_response(
        payload: dict[str, Any],
        *,
        parameter: str,
        fill_value: float = -999.0,
    ) -> tuple[str, list[dict[str, Any]]]:
        """Normalize documented regional POWER features to dated grid-point values."""
        features = payload.get("features")
        parameter_info = payload.get("parameters", {}).get(parameter)
        if not isinstance(features, list) or not isinstance(parameter_info, dict):
            raise NasaPowerError(
                "NASA POWER regional payload has an invalid feature or parameter schema."
            )
        unit = parameter_info.get("units")
        if not isinstance(unit, str) or not unit.strip():
            raise NasaPowerError("NASA POWER did not provide a unit for the requested parameter.")

        values: list[dict[str, Any]] = []
        for feature in features:
            try:
                coordinates = feature["geometry"]["coordinates"]
                longitude, latitude = float(coordinates[0]), float(coordinates[1])
                series = feature["properties"]["parameter"][parameter]
            except (KeyError, IndexError, TypeError, ValueError) as err:
                raise NasaPowerError(
                    "NASA POWER feature has an invalid regional data shape."
                ) from err
            if not isinstance(series, dict):
                raise NasaPowerError(
                    "NASA POWER point parameter values must be a date-keyed object."
                )
            for raw_date, raw_value in series.items():
                try:
                    observed_at = datetime.strptime(raw_date, "%Y%m%d").date()
                    value = float(raw_value)
                except (TypeError, ValueError) as err:
                    raise NasaPowerError(
                        "NASA POWER returned an invalid date or numeric value."
                    ) from err
                if not isfinite(value):
                    raise NasaPowerError("NASA POWER returned a non-finite numeric value.")
                if value == fill_value:
                    continue
                values.append(
                    {
                        "id": uuid.uuid4(),
                        "observed_at": observed_at,
                        "latitude": latitude,
                        "longitude": longitude,
                        "value": value,
                    }
                )
        return unit, values

    @staticmethod
    def _validate_request(
        parameter: str,
        latitude_min: float,
        latitude_max: float,
        longitude_min: float,
        longitude_max: float,
        start: date,
        end: date,
        community: str,
    ) -> None:
        if not parameter.strip() or "," in parameter:
            raise ValueError("Regional POWER requests require exactly one parameter.")
        if community.lower() not in {"ag", "hy", "sb", "re"}:
            raise ValueError("POWER community must be one of: ag, hy, sb, re.")
        if not (-90 <= latitude_min < latitude_max <= 90):
            raise ValueError("Latitude bounds must be ordered within [-90, 90].")
        if not (-180 <= longitude_min < longitude_max <= 180):
            raise ValueError("Longitude bounds must be ordered within [-180, 180].")
        if end < start:
            raise ValueError("The end date must not precede the start date.")
        if start < date(1981, 1, 1):
            raise ValueError("NASA POWER Daily data start on 1981-01-01.")
