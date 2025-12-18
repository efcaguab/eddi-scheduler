"""Client for interacting with myenergi eddi devices."""

from typing import Optional, Dict, Any, List
import requests
from requests.auth import HTTPDigestAuth


class EddiClient:
    """Client to interact with myenergi eddi device API."""

    def __init__(
        self,
        serial_number: str,
        api_key: str,
        base_url: Optional[str] = None
    ):
        """Initialize the eddi client.

        Args:
            serial_number: The hub serial number (used as username)
            api_key: The API key/password from myenergi app
            base_url: Optional base URL. If not provided, will use s18.myenergi.net
        """
        self.serial_number = serial_number
        self.api_key = api_key
        self.base_url = base_url or "https://s18.myenergi.net"
        
        # Set up session with digest auth
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(serial_number, api_key)
        self.session.headers.update({
            "accept": "application/json",
            "content-type": "application/json"
        })

    def get_status(self) -> List[Dict[str, Any]]:
        """Get the status of all devices.

        Returns:
            List of device status information

        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/cgi-jstatus-*"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_eddi_devices(self) -> List[Dict[str, Any]]:
        """Get list of eddi devices.

        Returns:
            List of eddi device information

        Raises:
            requests.RequestException: If the API request fails
        """
        status = self.get_status()
        for item in status:
            if "eddi" in item:
                return item["eddi"]
        return []

    def set_mode(self, eddi_serial: str, mode: str) -> Dict[str, Any]:
        """Set the mode for an eddi device.

        Args:
            eddi_serial: Serial number of the eddi device
            mode: Mode to set ('stop' or 'normal')

        Returns:
            API response as dictionary

        Raises:
            ValueError: If mode is invalid
            requests.RequestException: If the API request fails
        """
        if mode not in ["stop", "normal"]:
            raise ValueError(f"Invalid mode: {mode}. Must be 'stop' or 'normal'")
        
        mode_value = "0" if mode == "stop" else "1"
        url = f"{self.base_url}/cgi-eddi-mode-E{eddi_serial}-{mode_value}"
        
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def stop(self, eddi_serial: str) -> Dict[str, Any]:
        """Put eddi device into stop mode.

        Args:
            eddi_serial: Serial number of the eddi device

        Returns:
            API response as dictionary
        """
        return self.set_mode(eddi_serial, "stop")

    def start(self, eddi_serial: str) -> Dict[str, Any]:
        """Put eddi device into normal mode (exit stop mode).

        Args:
            eddi_serial: Serial number of the eddi device

        Returns:
            API response as dictionary
        """
        return self.set_mode(eddi_serial, "normal")
