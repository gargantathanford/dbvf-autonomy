import asyncio
from types import SimpleNamespace

from dbvf.vehicle_state import VehicleState, watch_position


class FakeTelemetry: 
	"""Acts like TelemetryAsync: gives one position, then the stream ends."""

	async def subscribe_position(self):
		yield SimpleNamespace(
			latitude_deg=36.15, longitude_deg=-95.99, relative_altitude_m=9.14
		)


def test_new_state_has_no_data():
	state = VehicleState()
	assert state.relative_altitude_m is None
	assert state.armed is None
	assert state.flight_mode is None


def test_watch_position_copies_values():
	state = VehicleState()
	asyncio.run(watch_position(FakeTelemetry(), state))
	assert state.latitude_deg == 36.15
	assert state.longitude_deg == -95.99
	assert state.relative_altitude_m == 9.14
