"""Make the one MAVLink connection to PX4 and find the autopilot"""

import argparse
import asyncio

from mavsdk.asyncio import ComponentType, Configuration, Mavsdk, System

SITL_URL = "udpin://0.0.0.0:14540"


def make_mavsdk() -> Mavsdk:
	"""Make the MAVSDK object, identified as a companion computer."""
	config = Configuration.create_with_component_type(ComponentType.COMPANION_COMPUTER)
	return Mavsdk(config)


async def connect(mavsdk: Mavsdk, url: str, timeout_s: float = 10.0) -> System:
	"""Add the connection and wait for the first autopilot. Raise if none is found."""
	await mavsdk.add_any_connection(url)
	drone = await mavsdk.first_autopilot(timeout_s)
	if drone is None:
		raise TimeoutError(f"No autopilot foundon {url} within {timeout_s} s")
	return drone


async def run(url: str, timeout_s: float) -> None:
	"""Connect once, print what was found, then close the connection."""
	async with make_mavsdk() as mavsdk:
		print(f"Waiting for an autopilot on {url} (max {timeout_s} s)...")
		drone = await connect (mavsdk, url, timeout_s)
		system_id = await drone.get_system_id()
		autopilot = await drone.autopilot_type()
		print(f"Connected: system id {system_id}, autopilot {autopilot_name}")


def main() -> None:
	"""Read the terminal options and run the connection check."""
	parser = argparse.ArgumentParser(description="Connect to PX4 and report the autopilot.")
	parser.add_argument("--url", default=SITL_URL, help="MAVSDK connection url")
	parser.add_argument("--timeout", type=float, default=10.0, help="seconds to wait")
	args = parser.parse_args()
	try:
		asyncio.run(run(args.url, args.timeout))
	except TimeoutError as error:
		print(f"FAILED: {error}")
		raise SystemExit(1)


if __name__ == "__main__":
	main()
