import math

from mavsdk.asyncio.plugins.telemetry import FlightMode

from dbvf.upload_mission import (
    MAV_CMD_NAV_LAND,
    MAV_CMD_NAV_TAKEOFF,
    MAV_CMD_NAV_WAYPOINT,
    MAV_FRAME_GLOBAL_RELATIVE_ALT,
    gm1_mission,
    outcome,
    takeoff,
    transit_leg,
    waypoint,
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


def test_waypoint_item_fields():
    w = waypoint(1, 36.1539816, -95.9927750, 10.7, hold_s=2.0)
    assert w.command == MAV_CMD_NAV_WAYPOINT
    assert w.current == 0
    assert w.param1 == 2.0
    assert w.z == 10.7


def test_transit_leg_is_takeoff_waypoint_land():
    start = (36.1539816, -95.9927750)
    end = (36.1542511, -95.9927750)
    leg = transit_leg(start, end, 10.7)
    assert [m.command for m in leg] == [MAV_CMD_NAV_TAKEOFF, MAV_CMD_NAV_WAYPOINT, MAV_CMD_NAV_LAND]
    assert [m.seq for m in leg] == [0, 1, 2]
    assert [m.current for m in leg] == [1, 0, 0]
    assert (leg[0].x, leg[0].y) == (361539816, -959927750)
    assert (leg[1].x, leg[1].y) == (leg[2].x, leg[2].y) == (361542511, -959927750)
    assert leg[0].z == leg[1].z == 10.7
    assert leg[2].z == 0.0