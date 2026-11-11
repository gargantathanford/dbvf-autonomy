"""Build MissionRaw items in code, upload them to PX4, and start or pause the mission."""

import argparse
import asyncio
import math
from collections.abc import Callable

from mavsdk.asyncio.plugins.action import ActionError
from mavsdk.asyncio.plugins.mission_raw import MissionItem, MissionRawError
from mavsdk.asyncio.plugins.telemetry import FlightMode

from dbvf.link import SITL_URL, Plugins, connect, make_mavsdk, make_plugins
from dbvf.vehicle_state import VehicleState, start

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


async def upload_and_start(plugins: Plugins, items: list[MissionItem]) -> None:
    """Upload the mission, arm, and switch PX4 to Mission mode."""
    await plugins.mission_raw.upload_mission(items)
    await plugins.action.arm()
    await plugins.mission_raw.start_mission()


async def wait_until(condition: Callable[[], bool], timeout_s: float, period_s: float = 0.2) -> None:
    """Check condition() every period_s seconds. Raise TimeoutError if it stays False."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout_s
    while not condition():
        if loop.time() > deadline:
            raise TimeoutError(f"Condition not met within {timeout_s} s")
        await asyncio.sleep(period_s)


def outcome(state: VehicleState, was_in_air: bool) -> str | None:
    """MODE_CHANGED, DONE, or None while the mission still runs."""
    if state.armed and state.flight_mode != FlightMode.MISSION:
        return "MODE_CHANGED"
    if was_in_air and state.armed is False:
        return "DONE"
    return None


async def follow(state: VehicleState, period_s: float = 1.0) -> str:
    """Print progress until the mission ends or the mode changes. Send nothing."""
    was_in_air = False
    while True:
        print(
            f"mode={state.flight_mode.name} item={state.mission_current}/{state.mission_total} "
            f"alt={state.relative_altitude_m:.1f} m in_air={state.in_air} armed={state.armed}"
        )
        if state.in_air:
            was_in_air = True
        result = outcome(state, was_in_air)
        if result is not None:
            return result
        await asyncio.sleep(period_s)


async def run(url: str, timeout_s: float, alt_m: float) -> None:
    """Fly the GM-1 test mission at the current position, then report how it ended."""
    async with make_mavsdk() as mavsdk:
        drone = await connect(mavsdk, url, timeout_s)
        plugins = make_plugins(drone)
        state = VehicleState()
        tasks = start(plugins, state)
        try:
            print("Waiting for armable and a position...")
            await wait_until(lambda: state.is_armable and state.latitude_deg is not None, 30.0)
            items = gm1_mission(state.latitude_deg, state.longitude_deg, alt_m)
            print(f"Uploading {len(items)} items, arming, starting...")
            await upload_and_start(plugins, items)
            await wait_until(lambda: state.flight_mode == FlightMode.MISSION, 10.0)
            result = await follow(state)
            if result == "MODE_CHANGED":
                print(f"Mode changed to {state.flight_mode.name}: companion stops, sends nothing.")
            else:
                print("Mission done: landed and disarmed.")
        finally:
            for task in tasks:
                task.cancel()


def main() -> None:
    """Read the terminal options and fly the GM-1 test mission in SITL."""
    parser = argparse.ArgumentParser(description="Fly the GM-1 test mission: takeoff, then land.")
    parser.add_argument("--url", default=SITL_URL, help="MAVSDK connection URL")
    parser.add_argument("--timeout", type=float, default=10.0, help="seconds to wait for the autopilot")
    parser.add_argument("--alt", type=float, default=5.0, help="takeoff altitude above home, m")
    args = parser.parse_args()
    try:
        asyncio.run(run(args.url, args.timeout, args.alt))
    except (TimeoutError, ActionError, MissionRawError) as error:
        print(f"FAILED: {error}")
        raise SystemExit(1)
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()