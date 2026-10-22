"""Keep the latest vehicle data from PX4 telemetry in one record."""

import argparse
import asyncio
from dataclasses import dataclass

from mavsdk.asyncio import System
from mavsdk.asyncio.plugins.telemetry import FlightMode, TelemetryAsync

from dbvf.link import SITL_URL, connect, make_mavsdk


@dataclass(slots=True)
class VehicleState:
	"""Latest telemetry values. None means: no message received yet."""
	
	latitude_deg: float | None = None
	longitude_deg: float | None = None
	relative_altitude_m: float | None = None
	flight_mode: FlightMode | None = None
	armed: bool | None = None
	in_air: bool | None = None
	battery_percent: float | None = None
	is_armable: bool | None = None


async def watch_position(telemetry: TelemetryAsync, state: VehicleState) -> None:
	"""Copy each new position into the record"""
	async for position in telemetry.subscribe_position():
		state.latitude_deg = position.latitude_deg
		state.longitude_deg = position.longitude_deg
		state.relative_altitude_m = position.relative_altitude_m


async def watch_flight_mode(telemetry: TelemetryAsync, state: VehicleState) -> None: 
	"""Copy each new flight mode into the record."""
	async for flight_mode in telemetry.subscribe_flight_mode():
		state.flight_mode = flight_mode


async def watch_armed(telemetry: TelemetryAsync, state: VehicleState) -> None:
	"""Copy each new armed value into the record."""
	async for armed in telemetry.subscribe_armed():
		state.armed = armed


async def watch_in_air(telemetry: TelemetryAsync, state: VehicleState) -> None:
	"""Copy each new in-air value to the record."""
	async for in_air in telemetry.subscribe_in_air():
		state.in_air = in_air


async def watch_battery(telemetry: TelemetryAsync, state: VehicleState) -> None:
	"""Copy each new battery percent (0 to 100) into the record."""
	async for battery in telemetry.subscribe_battery():
		state.battery_percent = battery.remaining_percent


async def watch_health(telemetry: TelemetryAsync, state: VehicleState) -> None:
	"""Copy each new armable value into the record."""
	async for health in telemetry.subscribe_health():
		state.is_armable = health.is_armable


def start(drone: System, state: VehicleState) -> None: 
	"""Start one watcher task per telemetry stream. Keep the returned list."""
	telemetry = TelemetryAsync(drone)
	watchers = (
		watch_position,
		watch_flight_mode,
		watch_armed,
		watch_in_air,
		watch_battery,
		watch_health,
	)
	return [asyncio.create_task(watcher(telemetry, state)) for watcher in watchers]


async def run(url: str, timeout_s: float, period_s: float) -> None:
	"""Connect, start the watchers, and print the record every period_s seconds."""
	async with make_mavsdk() as mavsdk:
		drone = await connect(mavsdk, url, timeout_s)
		state = VehicleState()
		tasks = start(drone,state)
		try:
			while True:
				print(state)
				await asyncio.sleep(period_s)
		finally:
			for task in tasks:
				task.cancel()


def main() -> None: 
	"""Read the terminal options and print the live vehicle state."""
	parser = argparse.ArgumentParser(description="Print the live vehicle state from PX4.")
	parser.add_argument("--url", default=SITL_URL, help="MAVSDK connection URL")
	parser.add_argument("--timeout", type=float, default=10.0, help="seconds to wait for the autopilot")
	parser.add_argument("--period", type=float, default=1.0, help="seconds between prints")
	args = parser.parse_args()
	try:
		asyncio.run(run(args.url, args.timeout, args.period))
	except TimeoutError as error:
		print(f"FAILED: {error}")
		raise SystemExit(1)
	except KeyboardInterrupt:
		print("Stopped.")


if __name__ == "__main__":
	main()
