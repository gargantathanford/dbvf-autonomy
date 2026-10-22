import asyncio
from types import SimpleNamespace

from dbvf.vehicle_state import (
    VehicleState,
    watch_armed,
    watch_mission_progress,
    watch_position,
)


class FakeTelemetry:
    """Acts like TelemetryAsync: each stream gives one value, then ends."""

    async def subscribe_position(self):
        yield SimpleNamespace(
            latitude_deg=36.15, longitude_deg=-95.99, relative_altitude_m=9.14
        )

    async def subscribe_armed(self):
        yield True


class FakeMissionRaw:
    """Acts like MissionRawAsync: gives one progress value, then ends."""

    async def subscribe_mission_progress(self):
        yield SimpleNamespace(current=2, total=5)


def test_new_state_has_no_data():
    state = VehicleState()
    assert state.relative_altitude_m is None
    assert state.armed is None
    assert state.flight_mode is None
    assert state.mission_current is None


def test_watch_position_copies_values():
    state = VehicleState()
    asyncio.run(watch_position(FakeTelemetry(), state))
    assert state.latitude_deg == 36.15
    assert state.longitude_deg == -95.99
    assert state.relative_altitude_m == 9.14


def test_watch_armed_copies_value():
    state = VehicleState()
    asyncio.run(watch_armed(FakeTelemetry(), state))
    assert state.armed is True
    assert state.in_air is None


def test_watch_mission_progress_copies_values():
    state = VehicleState()
    asyncio.run(watch_mission_progress(FakeMissionRaw(), state))
    assert state.mission_current == 2
    assert state.mission_total == 5