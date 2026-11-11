import math

from dbvf.fm1 import EARTH_RADIUS_M, offset


def test_offset_north_changes_latitude_only():
    lat, lon = offset(36.1539816, -95.9927750, 30.0, 0.0)
    assert math.isclose(lat - 36.1539816, math.degrees(30.0 / EARTH_RADIUS_M))
    assert lon == -95.9927750


def test_offset_30_m_north_is_about_0_00027_deg():
    lat, _ = offset(36.0, -96.0, 30.0, 0.0)
    assert math.isclose(lat - 36.0, 0.000269, abs_tol=1e-6)


def test_offset_east_is_larger_in_degrees_away_from_equator():
    _, lon_equator = offset(0.0, 0.0, 0.0, 30.0)
    _, lon_tulsa = offset(36.0, 0.0, 0.0, 30.0)
    assert lon_tulsa > lon_equator