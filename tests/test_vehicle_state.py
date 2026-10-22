from dbvf.vehicle_state import VehicleState


def test_new_state_has_no_data():
    state = VehicleState()
    assert state.relative_altitude_m is None
    assert state.armed is None
    assert state.flight_mode is None
