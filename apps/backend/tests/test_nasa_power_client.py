"""Mocked tests for the NASA POWER ingestion client."""

from datetime import date

import httpx
import pytest

from scripts.ingestion.nasa_power import NasaPowerClient, NasaPowerError


def make_client(handler: httpx.MockTransport) -> NasaPowerClient:
    return NasaPowerClient(client=httpx.Client(transport=handler))


def test_fetch_daily_regional_passes_documented_query_parameters() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [32.5, -24.5, 0]},
                        "properties": {"parameter": {"T2M": {"20260101": 27.1, "20260102": -999}}},
                    }
                ],
                "parameters": {"T2M": {"units": "C", "longname": "Temperature at 2 Meters"}},
                "header": {"fill_value": -999, "api": {"version": "v2.10.3"}},
            },
        )

    client = make_client(httpx.MockTransport(handler))
    payload = client.fetch_daily_regional(
        parameter="T2M",
        latitude_min=-25.0,
        latitude_max=-24.0,
        longitude_min=32.0,
        longitude_max=33.0,
        start=date(2026, 1, 1),
        end=date(2026, 1, 2),
        community="AG",
    )

    unit, values = NasaPowerClient.parse_regional_response(payload, parameter="T2M")
    assert unit == "C"
    assert len(values) == 1
    assert values[0]["value"] == 27.1
    assert values[0]["longitude"] == 32.5
    assert requests[0].url.params["parameters"] == "T2M"
    assert requests[0].url.params["format"] == "JSON"
    assert requests[0].url.params["time-standard"] == "UTC"


def test_regional_request_rejects_multiple_parameters() -> None:
    def unused_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, request=request, json={})

    client = NasaPowerClient(client=httpx.Client(transport=httpx.MockTransport(unused_handler)))
    with pytest.raises(ValueError, match="exactly one parameter"):
        client.fetch_daily_regional(
            parameter="T2M,PRECTOTCORR",
            latitude_min=-25.0,
            latitude_max=-24.0,
            longitude_min=32.0,
            longitude_max=33.0,
            start=date(2026, 1, 1),
            end=date(2026, 1, 2),
            community="AG",
        )


def test_request_normalizes_official_community_and_rejects_pre_1981_dates() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "features": [{"geometry": {"coordinates": [32.5, -24.5, 0]}}],
                "parameters": {"T2M": {"units": "C"}},
            },
        )

    client = make_client(httpx.MockTransport(handler))
    client.fetch_daily_regional(
        parameter="T2M",
        latitude_min=-25.0,
        latitude_max=-24.0,
        longitude_min=32.0,
        longitude_max=33.0,
        start=date(2026, 1, 1),
        end=date(2026, 1, 2),
        community="AG",
    )
    assert requests[0].url.params["community"] == "ag"

    with pytest.raises(ValueError, match="1981-01-01"):
        client.fetch_daily_regional(
            parameter="T2M",
            latitude_min=-25.0,
            latitude_max=-24.0,
            longitude_min=32.0,
            longitude_max=33.0,
            start=date(1980, 12, 31),
            end=date(1981, 1, 2),
            community="ag",
        )


def test_rate_limit_is_reported_as_ingestion_error() -> None:
    def rate_limit_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, request=request)

    client = make_client(httpx.MockTransport(rate_limit_handler))

    with pytest.raises(NasaPowerError, match="rate limit"):
        client.fetch_daily_regional(
            parameter="T2M",
            latitude_min=-25.0,
            latitude_max=-24.0,
            longitude_min=32.0,
            longitude_max=33.0,
            start=date(2026, 1, 1),
            end=date(2026, 1, 2),
            community="AG",
        )
