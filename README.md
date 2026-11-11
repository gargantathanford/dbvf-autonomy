# dbvf-autonomy

Companion computer software for the VFS DBVF 2026-2027 competition aircraft.
Setup: PX4 v1.18 on a CubePilot Cube Orange+, MAVSDK 4.x (Python) on a Raspberry Pi,
AprilTag-guided magnetic payload pickup.

## Stages

Each stage is one branch, one pull request, and one tag on `main`.
The record for each stage (tests, results, lessons) is in `docs/stages/`.

| Stage | Tag | New files | Test | Status |
|---|---|---|---|---|
| 0 | `stage-0` | skeleton | install + `pytest` | done ([record](docs/stages/00-skeleton.md)) |
| 1 | `stage-1` | `link.py`, `vehicle_state.py` | SITL + QGC at the same time | done ([record](docs/stages/01-link.md)) |
| 2 | `stage-2` | `upload_mission.py` (GM-1 test mission 0) | SITL: takeoff, land; stop on mode change | done ([record](docs/stages/02-mission.md)) |
| 3 | `stage-3` | `fm1.py` (FM-1 legs, GO input) | SITL: H, D, GO, H | done ([record](docs/stages/03-fm1.md)) |
| 4 | | `set_magnet.py` | bench, props off: PWM 1000/1800 us at the magnet, also after disarm | |
| 5 | | `vision.py`, `apriltag_offset_error.py`, `pinpoint.py` | `pytest` + sample images | |
| 6 | | `set_velocity_setpoint.py`, `states.py` (pickup track) | SITL with fake detections | |
| 7 | | dropoff track, attempt timer, `main.py` | SITL, then low flight with a safety pilot | |

## Build and run

### Prerequisites
- Python 3.10 or newer (`python3 --version`)
- Git
- For simulation: Docker Desktop and QGroundControl
- macOS: the mavsdk 4.0.6 wheel needs macOS 15 or newer
- Raspberry Pi: 64-bit Raspberry Pi OS (mavsdk has no 32-bit ARM wheel)

### 1. Clone
```
git clone https://github.com/gargantathanford/dbvf-autonomy.git
cd dbvf-autonomy
```

### 2. Make and activate a virtual environment
macOS / Linux:
```
python3 -m venv .venv
source .venv/bin/activate
```
Windows (PowerShell):
```
py -m venv .venv
.venv\Scripts\Activate.ps1
```
The prompt must start with `(.venv)`. Activate again in each new terminal.

### 3. Install
Development (pytest included):
```
pip install -e ".[dev]"
```
Exact tested versions (use on the aircraft computer):
```
pip install -r requirements.txt
pip install -e . --no-deps
```

### 4. Check the install
```
python -c "from mavsdk.asyncio import Mavsdk; print('mavsdk OK')"
pytest -v
```
All tests must pass. No simulator is needed for pytest.

### 5. Connect to PX4 SITL
Terminal 1: start the PX4 simulator (SIH, no graphics).

macOS / Windows (Docker Desktop):
```
docker run --rm -it px4io/px4-sitl:latest
```
Linux host:
```
docker run --rm -it --network host px4io/px4-sitl:latest
```
Wait for the `pxh>` prompt. Do not add `-p` port options: the container sends
MAVLink to the host by itself. Run only one PX4 container (`docker ps` to check).

Open QGroundControl. It connects by itself on UDP 14550.

Terminal 2 (repo folder, venv active):
```
python -m dbvf.link
```
Expected: `Connected: system id 1, autopilot PX4`.
Our code listens on UDP 14540 (PX4's offboard API port), so it does not interfere with QGC.

#### Without Docker
PX4 then sends to the same ports on this computer, so all commands below work with no change.
Use the same PX4 version as the flight controller firmware.
- Ubuntu 22.04/24.04, pre-built: download `px4_*.deb` for your PX4 version
  from https://github.com/PX4/PX4-Autopilot/releases, then
  ```
  sudo apt install ./px4_*.deb
  px4
  ```
- From source (see the PX4 dev-environment docs for setup), Ubuntu or macOS:
  ```
  make px4_sitl sihsim_quadx
  ```
- Windows: use WSL2 + Ubuntu, and run both PX4 and this repo inside WSL2.

### 6. Run the missions in SITL
PX4 in Terminal 1, QGC open, then in Terminal 2:

| Command | What it flies | Expected last line |
|---|---|---|
| `python -m dbvf.vehicle_state` | nothing: prints telemetry each second | (Ctrl+C to stop) |
| `python -m dbvf.upload_mission` | GM-1 test mission 0: takeoff to 5 m, land | `Mission done: landed and disarmed.` |
| `python -m dbvf.fm1 --sitl-d-north 30` | FM-1: H, D (30 m north), GO (Enter), H | `FM-1 done: landed in H and disarmed.` |

- At the event, give the real zone D: `python -m dbvf.fm1 --d LAT LON`.
  `--sitl-d-north` is for SITL only.
- To test the pilot takeover, change the mode in QGC during the flight. The
  companion prints `Mode changed to ...` and sends nothing more.
  In SITL, use **Hold**: Position mode needs RC or a joystick, and SITL has neither.
- Restart PX4 between FM-1 runs so that each run starts at H.
- Add `--help` to any command for its options.

### Updating dependencies
1. Edit `pyproject.toml`.
2. `pip install -e ".[dev]"`
3. `pip freeze --exclude-editable > requirements.txt`
4. Commit both files together.