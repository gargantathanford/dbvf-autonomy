# Stage 2: Upload and fly a mission (GM-1 test mission 0)

## Goal
Upload a mission with MissionRaw, arm, start it, and follow it.
The companion stops and sends nothing when the pilot changes the mode.

## Files
- `dbvf/link.py`: added `Plugins` and `make_plugins()` (one plugin object of each type).
- `dbvf/vehicle_state.py`: added `mission_current`, `mission_total`, `watch_mission_progress()`.
- `dbvf/upload_mission.py`: `item()`, `takeoff()`, `land()`, `gm1_mission()`,
  `upload_and_start()`, `wait_until()`, `outcome()`, `follow()`.
- `tests/test_upload_mission.py`: mission item fields and `outcome()` logic.

## Mission
| seq | command | frame | position | alt |
|---|---|---|---|---|
| 0 | 22 NAV_TAKEOFF | 3 GLOBAL_RELATIVE_ALT | current | 5 m |
| 1 | 21 NAV_LAND | 3 GLOBAL_RELATIVE_ALT | same | 0 m |

## Unit tests
```
==================================================================================================== 11 passed in 1.41s ===================================================================================================
```

## SITL tests
Setup: `docker run --rm -it px4io/px4-sitl:latest`, QGC on UDP 14550, MAVSDK on 14540.

### Test A: normal mission
```
Mission done: landed and disarmed.
```
Result: `Mission done: landed and disarmed.`

### Test B: mode change during climb
Changed mode to Hold in QGC during the climb.
```
Mode changed to HOLD: companion stops, sends nothing.
```
Result: `Mode changed to HOLD: companion stops, sends nothing.`

Note: Position mode was rejected in SITL ("No manual control input").
Position needs an RC transmitter or joystick. The real GM-1 override
(RFP p. 24) will be tested on the real drone with the pilot's RC.

## Lessons
- PX4 manual modes (Position, Altitude, Manual) need manual control input.
  Auto modes (Hold, Return, Land) do not.