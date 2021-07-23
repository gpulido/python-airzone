"""Local Api tests."""
import json
import os

import pytest  # type: ignore
import requests_mock  # type: ignore

from airzone.localapi import API, Machine, OperationMode, Speed

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
response_test_path = os.path.join(THIS_DIR, "data/response.json")


@pytest.fixture
def mock_api():
    """Fixture localapi Machine init with the data/response.json file."""
    with requests_mock.Mocker() as mock_resp:
        f = open(response_test_path,)
        data = json.load(f)
        machine_ipaddr = "0.0.0.0"
        mock_addr = f"http://{machine_ipaddr}:3000/api/v1/hvac"
        mock_resp.post(mock_addr, json=data)
        return API(machine_ipaddr)


def test_create_machine(mock_api):
    """Test the creation of a machine and zones with a valid json."""
    machine = Machine(mock_api)
    assert machine.speed == Speed.AUTO
    assert machine.operation_mode == OperationMode.COOLING
