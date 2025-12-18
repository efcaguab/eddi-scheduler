"""Tests for the EddiClient."""

import pytest
from unittest.mock import Mock, patch
from eddi_scheduler.client import EddiClient


@pytest.fixture
def client():
    """Create a test client."""
    return EddiClient("12345678", "test_api_key", "https://test.myenergi.net")


def test_client_initialization():
    """Test client initialization."""
    client = EddiClient("12345678", "test_key")
    assert client.serial_number == "12345678"
    assert client.api_key == "test_key"
    assert client.base_url == "https://s18.myenergi.net"


def test_client_custom_base_url():
    """Test client with custom base URL."""
    client = EddiClient("12345678", "test_key", "https://custom.url")
    assert client.base_url == "https://custom.url"


@patch("eddi_scheduler.client.requests.Session")
def test_get_status(mock_session_class, client):
    """Test getting device status."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = [{"eddi": [{"sno": 10088888}]}]
    mock_session.get.return_value = mock_response
    client.session = mock_session
    
    result = client.get_status()
    
    assert result == [{"eddi": [{"sno": 10088888}]}]
    mock_session.get.assert_called_once_with("https://test.myenergi.net/cgi-jstatus-*")


@patch("eddi_scheduler.client.requests.Session")
def test_get_eddi_devices(mock_session_class, client):
    """Test getting eddi devices."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = [
        {"eddi": [{"sno": 10088888, "sta": 1}]},
        {"harvi": []}
    ]
    mock_session.get.return_value = mock_response
    client.session = mock_session
    
    result = client.get_eddi_devices()
    
    assert result == [{"sno": 10088888, "sta": 1}]


@patch("eddi_scheduler.client.requests.Session")
def test_get_eddi_devices_empty(mock_session_class, client):
    """Test getting eddi devices when none exist."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = [{"harvi": []}]
    mock_session.get.return_value = mock_response
    client.session = mock_session
    
    result = client.get_eddi_devices()
    
    assert result == []


@patch("eddi_scheduler.client.requests.Session")
def test_set_mode_stop(mock_session_class, client):
    """Test setting device to stop mode."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {"status": 0, "statustext": ""}
    mock_session.get.return_value = mock_response
    client.session = mock_session
    
    result = client.set_mode("10088888", "stop")
    
    assert result == {"status": 0, "statustext": ""}
    mock_session.get.assert_called_once_with(
        "https://test.myenergi.net/cgi-eddi-mode-E10088888-0"
    )


@patch("eddi_scheduler.client.requests.Session")
def test_set_mode_normal(mock_session_class, client):
    """Test setting device to normal mode."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {"status": 0, "statustext": ""}
    mock_session.get.return_value = mock_response
    client.session = mock_session
    
    result = client.set_mode("10088888", "normal")
    
    assert result == {"status": 0, "statustext": ""}
    mock_session.get.assert_called_once_with(
        "https://test.myenergi.net/cgi-eddi-mode-E10088888-1"
    )


def test_set_mode_invalid(client):
    """Test setting invalid mode raises error."""
    with pytest.raises(ValueError, match="Invalid mode"):
        client.set_mode("10088888", "invalid")


@patch("eddi_scheduler.client.requests.Session")
def test_stop(mock_session_class, client):
    """Test stop convenience method."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {"status": 0}
    mock_session.get.return_value = mock_response
    client.session = mock_session
    
    result = client.stop("10088888")
    
    assert result == {"status": 0}


@patch("eddi_scheduler.client.requests.Session")
def test_start(mock_session_class, client):
    """Test start convenience method."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {"status": 0}
    mock_session.get.return_value = mock_response
    client.session = mock_session
    
    result = client.start("10088888")
    
    assert result == {"status": 0}
