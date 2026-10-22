# Stage 1: link.py + vehicle_state.py

## What
link.py: one MAVSDK 4.0.6 connection as COMPANION_COMPUTER; connect() waits for the first autopilot, raises TimeoutError if none. 

## How tested
- pytest:
test_connect_times_out_without_autopilot (no autopilot on port 14599). 
- SITL: docker run --rm -it px4ip/px4-sitl:latest (SIH, Docker Desktop on macOS), QGC connected at the same time. 
- python -m dbvf.link --timeout 15

## Result 
Connected: system id 1, autopilot PX4
QGC stayed connected
Note: "Error from async_receive_from: Bad file descriptor" as exit is MAVSDK shutdown logging on macOS (socket close), not a fault. See udp_connection.cpp

## Open
- Pin the image tag to the Cube firmware version (now: latest).
- vehicle_state.py
