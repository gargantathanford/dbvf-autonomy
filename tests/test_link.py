import asyncio

import pytest

from dbvf.link import connect, make_mavsdk


def test_connect_times_out_without_autopilot():
	async def run():
		async with make_mavsdk() as mavsdk:
			await connect(mavsdk, "udpin://0.0.0.0:14599", timeout_s=1.0)

	with pytest.raises(TimeoutError):
		asyncio.run(run())

