
# dbvf-autonomy

Companion computer software for the VFS DBVF 2026-2027 competition aircraft. Setup: PX4 v1.16 on a Cube Orange+, MAVSDK 4.x (Python), AprilTag guided magnetic payload pickup. 

## Build and Run

## Build and run

### Prerequisites
- Python 3.10 or newer (`python3 --version`)
- Git
- For simulation: Docker Desktop and QGroundControl
- macOS: the mavsdk 4.0.6 wheel needs macOS 15 or newer
- Raspberry Pi: 64-bit Raspberry Pi OS (mavsdk has no 32-bit ARM wheel)

### 1. Clone
```
git clone https://github.com/<user>/dbvf-autonomy.git
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
Terminal 1: start the PX4 simulator (SIH, no graphics):
```
docker run --rm -it px4io/px4-sitl:latest
```

Linux host: docker run --rm -it --network host px4io/px4-sitl:latest


Wait for the `pxh>` prompt. Do not add `-p` port options: on Docker Desktop the container sends MAVLink to the host by itself.

Open QGroundControl. It connects by itself on UDP 14550.

Terminal 2 (repo folder, venv active):
```
python -m dbvf.link
```
Expected: `Connected: system id 1, autopilot PX4`.
Our code listens on UDP 14540 (PX4's offboard API port), so it does not interfere with QGC.

### Updating dependencies
1. Edit `pyproject.toml`.
2. `pip install -e ".[dev]"`
3. `pip freeze --exclude-editable > requirements.txt`
4. Commit both files together.
