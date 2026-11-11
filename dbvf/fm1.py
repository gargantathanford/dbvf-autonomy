"""FM-1: take off at H, land in D, wait for GO, take off at D, land in H (RFP pp. 26-27)."""

import argparse
import asyncio
import math
import threading

from mavsdk.asyncio.plugins.action import ActionError
from mavsdk.asyncio.plugins.mission_raw import MissionRawError

from dbvf.link import SITL_URL, connect, make_mavsdk, make_plugins
from dbvf.upload_mission import fly_leg, transit_leg, wait_until
from dbvf.vehicle_state import VehicleState, start

EARTH_RADIUS_M = 6378137.0  # WGS84 equatorial radius
FM1_ALT_M = 10.7  # 35 ft: the 30 ft AGL minimum (RFP p. 23) plus margin


def offset(lat_deg: float, lon_deg: float, north_m: float, east_m: float) -> tuple[float, float]:
    """The point north_m and east_m from (lat, lon). Flat-earth: short SITL distances only."""
    dlat = math.degrees(north_m / EARTH_RADIUS_M)
    dlon = math.degrees(east_m / (EARTH_RADIUS_M * math.cos(math.radians(lat_deg))))
    return lat_deg + dlat, lon_deg + dlon


async def wait_for_go(prompt: str) -> None:
    """Wait until the operator presses Enter. Telemetry keeps running meanwhile."""
    loop = asyncio.get_running_loop()
    pressed = loop.create_future()

    def read() -> None:
        try:
            input(prompt)
        except EOFError as error:
            loop.call_soon_threadsafe(pressed.set_exception, error)
            return
        loop.call_soon_threadsafe(pressed.set_result, None)

    threading.Thread(target=read, daemon=True).start()
    await pressed


async def run(url: str, timeout_s: float, alt_m: float, d: tuple[float, float] | None, d_north_m: float) -> None:
    """Fly FM-1. H is the position at start. D is given, or (SITL only) d_north_m north of H."""
    async with make_mavsdk() as mavsdk:
        drone = await connect(mavsdk, url, timeout_s)
        plugins = make_plugins(drone)
        state = VehicleState()
        tasks = start(plugins, state)
        try:
            print("Waiting for a position...")
            await wait_until(lambda: state.latitude_deg is not None, 30.0)
            h = (state.latitude_deg, state.longitude_deg)
            if d is None:
                d = offset(h[0], h[1], d_north_m, 0.0)
                print(f"SITL: D is {d_north_m} m north of H.")
            print(f"H = {h[0]:.7f}, {h[1]:.7f}")
            print(f"D = {d[0]:.7f}, {d[1]:.7f}")

            result = await fly_leg(plugins, state, transit_leg(h, d, alt_m), "Leg 1 H -> D")
            if result == "MODE_CHANGED":
                print(f"Mode changed to {state.flight_mode.name}: companion stops, sends nothing.")
                return
            print("Landed in D and disarmed.")

            await wait_for_go("Judge flag at D? Press Enter for GO (arm and take off), Ctrl+C to stop: ")
            here = (state.latitude_deg, state.longitude_deg)
            result = await fly_leg(plugins, state, transit_leg(here, h, alt_m), "Leg 2 D -> H")
            if result == "MODE_CHANGED":
                print(f"Mode changed to {state.flight_mode.name}: companion stops, sends nothing.")
                return
            print("FM-1 done: landed in H and disarmed.")
        finally:
            for task in tasks:
                task.cancel()


def main() -> None:
    """Read the terminal options and fly FM-1."""
    parser = argparse.ArgumentParser(description="Fly FM-1: H -> D, wait for GO, D -> H.")
    parser.add_argument("--url", default=SITL_URL, help="MAVSDK connection URL")
    parser.add_argument("--timeout", type=float, default=10.0, help="seconds to wait for the autopilot")
    parser.add_argument("--alt", type=float, default=FM1_ALT_M, help="transit altitude above home, m")
    where = parser.add_mutually_exclusive_group(required=True)
    where.add_argument("--d", nargs=2, type=float, metavar=("LAT", "LON"), help="zone D center, degrees")
    where.add_argument("--sitl-d-north", type=float, metavar="M", help="SITL only: put D this many m north of H")
    args = parser.parse_args()
    d = tuple(args.d) if args.d else None
    try:
        asyncio.run(run(args.url, args.timeout, args.alt, d, args.sitl_d_north))
    except (TimeoutError, ActionError, MissionRawError, EOFError) as error:
        print(f"FAILED: {error!r}")
        raise SystemExit(1)
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()