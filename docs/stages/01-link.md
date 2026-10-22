# Stage 1: link.py + vehicle_state.py

## What
- link.py: one MAVSDK 4.0.6 connection as COMPANION_COMPUTER.
  connect() waits for the first autopilot and raises TimeoutError if none is found.
- vehicle_state.py: VehicleState record (None = no data yet, slots=True).
  Six telemetry watchers (position, flight mode, armed, in air, battery, health)
  run as asyncio tasks. The record prints at 1 Hz.

## How tested
- pytest (no drone): connect() timeout; empty record; watch_position and
  watch_armed with fake telemetry. 4 passed.
- SITL: docker run --rm -it px4io/px4-sitl:latest (SIH), PX4 version: <ver all result>.
  QGC connected at the same time.
- python -m dbvf.link -> "Connected: system id 1, autopilot PX4"
- python -m dbvf.vehicle_state, with QGC takeoff, mode changes and land.

## Result
- QGC stayed connected the whole time.
- Takeoff: flight_mode HOLD -> TAKEOFF -> HOLD; armed True; in_air True;
  relative_altitude_m about 3.04 m.
- Sample line:
  VehicleState(latitude_deg=47.3977433, longitude_deg=8.5455945,
  relative_altitude_m=3.037, flight_mode=<FlightMode.HOLD: 3>, armed=True,
  in_air=True, battery_percent=50.0, is_armable=True)
- "Error from async_receive_from: Bad file descriptor" at exit is MAVSDK
  shutdown logging on macOS (socket close), not a fault (udp_connection.cpp).

## Bug found and fixed
- In SITL, armed stayed None while in the air. Cause: a misspelled name in
  watch_armed (missing "_"). No error was shown.
- Fixes: @dataclass(slots=True) rejects unknown field names;
  test_watch_armed_copies_value calls the watcher directly.

## Open
- Pin the SITL image tag to v1.18.0-rc1 (later v1.18.0). Now: latest.
- Unit tests for the other four watchers (optional).
