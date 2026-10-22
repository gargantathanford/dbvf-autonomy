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
