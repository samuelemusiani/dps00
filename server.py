from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
import httpx

app = FastAPI(title="Lagovia Train Tracker")

BELGIUM_TZ = ZoneInfo("Europe/Brussels")

IRAIL_BASE = "https://api.irail.be/v1"
HEADERS = {"User-Agent": "lagovia-train-tracker/1.0.0 (github.com/samuelemusiani; samuele.musiani@tum.de)"}

# For testing
DEBUG_TIME: str | None = "0110"  
DEBUG_DATE: str | None = "15062026"


class Departure(BaseModel):
    train_number: str
    destination: str
    scheduled_time: str   # ISO-8601, e.g. "2024-06-15T14:32:00"
    delay_minutes: int


class StationDepartures(BaseModel):
    station: str
    departures: List[Departure]


class DeparturesResponse(BaseModel):
    stations: List[StationDepartures]


class ErrorResponse(BaseModel):
    error: str
    detail: str


# Helper models and functions for iRail API interaction
class Station(BaseModel):
    id: str
    name: str


async def search_stations(query: str, client: httpx.AsyncClient) -> List[Station]:
    """Return stations whose name contains `query` as a case-insensitive substring."""
    response = await client.get(
        f"{IRAIL_BASE}/stations/",
        params={"format": "json", "lang": "en"},
        headers=HEADERS,
    )
    response.raise_for_status()
    stations = response.json()["station"]
    return [
        Station(id=s["id"], name=s["name"])
        for s in stations
        if query.lower() in s["name"].lower()
    ]


async def fetch_departures_for_station(station: Station, client: httpx.AsyncClient) -> List[Departure]:
    """Return departures within the next 15 minutes for the given station."""
    params = {"id": station.id, "format": "json", "lang": "en", "arrdep": "departure"}
    if DEBUG_TIME:
        params["time"] = DEBUG_TIME
    if DEBUG_DATE:
        params["date"] = DEBUG_DATE

    response = await client.get(f"{IRAIL_BASE}/liveboard/", params=params, headers=HEADERS)
    response.raise_for_status()

    raw = response.json().get("departures", {}).get("departure", [])

    if DEBUG_DATE and DEBUG_TIME:
        day, month, year = DEBUG_DATE[:2], DEBUG_DATE[2:4], DEBUG_DATE[4:]
        hour, minute = DEBUG_TIME[:2], DEBUG_TIME[2:]
        now = datetime(int(year), int(month), int(day), int(hour), int(minute), tzinfo=BELGIUM_TZ)
    else:
        now = datetime.now(BELGIUM_TZ)

    departures = []
    for d in raw:
        scheduled = datetime.fromtimestamp(int(d["time"]), tz=BELGIUM_TZ)
        minutes_until = (scheduled - now).total_seconds() / 60
        if 0 <= minutes_until <= 15:
            departures.append(Departure(
                train_number=d["vehicleinfo"]["number"],
                destination=d["station"],
                scheduled_time=scheduled.isoformat(),
                delay_minutes=int(d["delay"]) // 60,
            ))
    return departures


@app.get(
    "/departures",
    response_model=DeparturesResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Query too short"},
        502: {"model": ErrorResponse, "description": "Upstream iRail error"},
    },
)
async def get_departures(q: str = Query(..., description="Station name substring (≥ 3 chars)")):
    if len(q) < 3:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "query_too_short",
                "detail": f"Query must be at least 3 characters, got {len(q)}.",
            },
        )

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            stations = await search_stations(q, client)
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502,
                detail={"error": "upstream_error", "detail": f"iRail stations request failed: {exc}"},
            )

        results: List[StationDepartures] = []
        for station in stations:
            try:
                departures = await fetch_departures_for_station(station, client)
            except httpx.HTTPError as exc:
                raise HTTPException(
                    status_code=502,
                    detail={"error": "upstream_error", "detail": f"iRail liveboard failed for '{station.name}': {exc}"},
                )
            results.append(StationDepartures(station=station.name, departures=departures))

    return DeparturesResponse(stations=results)
