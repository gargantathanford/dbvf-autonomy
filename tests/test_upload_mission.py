import math

from mavsdk.asyncio.plugins.telemetry import FlightMode

from dbvf.upload_mission import (
    MAV_CMD_NAV_LAND,
    MAV_CMD_NAV_TAKEOFF,
    MAV_FRAME_GLOBAL_RELATIVE_ALT,
    gm1_mission,
    outcome,
    takeoff,
)
from dbvf.vehicle_state import VehicleState


def test_takeoff_item_fields():
    t = takeoff(0, 36.1539816, -95.9927750, 5.0)
    assert t.seq == 0
    assert t.command == MAV_CMD_NAV_TAKEOFF
    assert t.frame == MAV_FRAME_GLOBAL_RELATIVE_ALT
    assert t.current == 1
    assert t.autocontinue == 1
    assert t.x == 361539816
    assert t.y == -959927750
    assert t.z == 5.0
    assert math.isnan(t.param4)


def test_gm1_mission_is_takeoff_then_land_at_same_place():
    mission = gm1_mission(36.1539816, -95.9927750, 5.0)
    assert [m.command for m in mission] == [MAV_CMD_NAV_TAKEOFF, MAV_CMD_NAV_LAND]
    assert [m.seq for m in mission] == [0, 1]
    assert mission[1].current == 0
    assert (mission[0].x, mission[0].y) == (mission[1].x, mission[1].y)


def test_outcome_running_in_mission():
    state = VehicleState(flight_mode=FlightMode.MISSION, armed=True, in_air=True)
    assert outcome(state, was_in_air=True) is None


def test_outcome_mode_changed_by_pilot():
    state = VehicleState(flight_mode=FlightMode.POSCTL, armed=True, in_air=True)
    assert outcome(state, was_in_air=True) == "MODE_CHANGED"


def test_outcome_done_after_landing():
    state = VehicleState(flight_mode=FlightMode.MISSION, armed=False, in_air=False)
    assert outcome(state, was_in_air=True) == "DONE"


def test_outcome_not_done_before_takeoff():
    state = VehicleState(flight_mode=FlightMode.MISSION, armed=False, in_air=False)
    assert outcome(state, was_in_air=False) is None