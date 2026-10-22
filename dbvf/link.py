"""Make the one MAVLink connection to PX4 and find the autopilot"""

import argparse
import asyncio

from mavsdk.asyncio import ComponentType, Configuration, Mavsdk, System

SITL_URL = "udpin://0.0.0.0:14540"


def make_mavsdk() -> Mavsdk:
	"""Make the MAVSDK object, identified as a companion computer."""
	config = Configuration.create_with_component_type(ComponentType.COMPANION_COMPUTER)
	return Mavsdk(config)
