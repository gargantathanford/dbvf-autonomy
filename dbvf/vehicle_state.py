"""Keep the latest vehicle data from PX4 telemetry in one record."""

import argparse
import asyncio
from dataclasses import dataclass

from mavsdk.asyncio import System
from mavsdk.asyncio.plugins.telemetry import FlightMode, TelemetryAsync

from dbvf.link import SITL_URL, connect, make_mavsdk


@dataclass
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
