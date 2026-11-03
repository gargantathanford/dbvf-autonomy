"""Build MissionRaw items in code, upload them to PX4, and start or pause the mission."""

import math

from mavsdk.asyncio.plugins.mission_raw import MissionItem

# MAVLink values, from message_definitions/v1.0/common.xml
MAV_FRAME_MISSION = 2  # item has no position
MAV_FRAME_GLOBAL_RELATIVE_ALT = 3  # lat/lon, altitude above home
MAV_MISSION_TYPE_MISSION = 0
MAV_CMD_NAV_WAYPOINT = 16
MAV_CMD_NAV_LAND = 21
MAV_CMD_NAV_TAKEOFF = 22


def item(
    seq: int,
    command: int,
    lat_deg: float,
    lon_deg: float,
    alt_m: float,
    param1: float = 0.0,
    param2: float = 0.0,
    param4: float = math.nan,
) -> MissionItem:
    """One mission item with a position, in MISSION_ITEM_INT form."""
    return MissionItem(
        seq=seq,
        frame=MAV_FRAME_GLOBAL_RELATIVE_ALT,
        command=command,
        current=1 if seq == 0 else 0,
        autocontinue=1,
        param1=param1,
        param2=param2,
        param3=0.0,
        param4=param4,
        x=round(lat_deg * 1e7),
        y=round(lon_deg * 1e7),
        z=alt_m,
        mission_type=MAV_MISSION_TYPE_MISSION,
    )


def takeoff(seq: int, lat_deg: float, lon_deg: float, alt_m: float) -> MissionItem:
    """Vertical takeoff to alt_m above home, at this position."""
    return item(seq, MAV_CMD_NAV_TAKEOFF, lat_deg, lon_deg, alt_m)


def land(seq: int, lat_deg: float, lon_deg: float) -> MissionItem:
    """Land at this position."""
    return item(seq, MAV_CMD_NAV_LAND, lat_deg, lon_deg, 0.0)


def gm1_mission(lat_deg: float, lon_deg: float, alt_m: float) -> list[MissionItem]:
    """GM-1 override test: autonomous takeoff and landing at one location (RFP p. 24)."""
    return [
        takeoff(0, lat_deg, lon_deg, alt_m),
        land(1, lat_deg, lon_deg),
    ]