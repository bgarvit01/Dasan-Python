import requests
import logging
import time
from pprint import pprint

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DasanClient:
    """
        Python Client to interact with Dasan WiFi Routers

    """
    def __init__(self, username='', password='', router_url="192.168.1.1", bearer_token=""):
        self.username = username
        self.password = password
        self.router_url = router_url
        self.bearer_token = bearer_token
        self.session = requests.Session()
        self.base_url = f"http://{router_url}"
        self.HEADER = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Origin': self.base_url,
            'Referer': f'{self.base_url}/wifi/settings',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
            'Authorization': f'Bearer {self.token}',
        }

    def _get_csrf_token(self, response):
        """
        Extract CSRF token from the response headers
        """
        return response.headers.get('csrf', None)

    def update_wifi_ssid_password(self, wifi_ssid = None, wifi_password = None, payload=None):
        """
        Fetch router details.

        :return: dict object containing router details or error message.
        """
        url = f"{self.base_url}/dm/tr98/?objs=WLANConfiguration&page=WifiSetupPage-WirelessSetting"
        if not wifi_ssid and not wifi_password:
            logger.error("Neither WiFi Ssid nor WiFi Password Found")
            return None

        try:
            # Initial GET request to retrieve CSRF token
            response = self.session.get(url, headers=self.AUTH_HEADER)
            response.raise_for_status()
            
            csrf_token = self._get_csrf_token(response)
            if not csrf_token:
                logger.error("CSRF token not found in headers.")
                return None
            
            # Update headers with CSRF token
            self.HEADER['x-csrf-token'] = csrf_token
            self.HEADER['Content-Type'] = 'application/json'

            # Example payload - Modify as needed
            # Change the RadiusServer and MACAddress
            if not payload:
                payload = {
                    "WLANConfiguration": {
                        "data": [{
                            "iid": 1,
                            "RadioEnabled": False,
                            "SSID": wifi_ssid,
                            "KeyPassphrase": wifi_password,
                            "SSIDAdvertisementEnabled": False,
                            "MaxStaNum": 32,
                            "Security": "WpaPskWpa2Psk",
                            "RadiusPort": 1812,
                            "RadiusServer": "1.2.3.4",
                            "RadiusKey": "airtelbroadband",
                            "WPAEncryptionModes": "TKIPandAESEncryption",
                            "UseWps": False,
                            "WpsState": "Configured",
                            "BandSteering": True,
                            "MacAclPolicy": 0,
                            "RatelimitUpstream": 0,
                            "RatelimitDownstream": 0,
                            "MACAddress": "yy:yy:yy:yy:yy:yy"
                        }]
                    }
                }

            # POST request to configure the router
            response = self.session.post(url, headers=self.HEADER, json=payload)
            response.raise_for_status()
            logger.info("Router configured successfully.")
            return response.json

        except requests.RequestException as e:
            logger.error(f"Failed to fetch router details: {e}")
            return None

    def fetch_wifi_details(self):
        """
        Fetch the updated router details.
        :return: dict object containing updated router details or error message.
        """
        url = f"{self.base_url}/dm/tr98/?objs=WLANConfiguration&page=WifiSetupPage-WirelessSetting"

        try:
            response = self.session.get(url, headers=self.AUTH_HEADER)
            response.raise_for_status()
            logger.info("Fetched updated router details successfully.")
            return response.json
        except requests.RequestException as e:
            logger.error(f"Failed to fetch updated router details: {e}")
            return None

    def fetch_updated_details(self):
        """
        Fetch the updated router details.
        :return: dict object containing updated router details or error message.
        """
        return self.fetch_wifi_details()



class DasanClientRun:
    """
    Runner Class for DasanClient
    """
    @staticmethod
    def change_basic_wifi_settings():

        client = DasanClient(router_url="192.168.1.1", bearer_token="your_auth_bearer_token_here")
        
        # Test: Fetch router details
        logger.info("<---------- Running: Fetch router details ---------->")
        router_details = client.fetch_wifi_details()
        pprint(router_details)

        wifi_ssid = "your_new_wifi_name_here"
        wifi_password = "your_new_wifi_password_here"
        # Can modify the payload from above response and send that as well
        payload = None

        # Test: Fetch router details
        logger.info("<---------- Running: Update Basic Wifi Settings ---------->")
        response = client.update_wifi_ssid_password(wifi_ssid, wifi_password, payload)
        pprint(response)

        # Test: Fetch updated router details
        logger.info("<---------- Testing: Fetch updated router details ---------->")
        updated_details = client.fetch_updated_details()
        pprint(updated_details)


if __name__ == "__main__":
    DasanClientRun.change_basic_wifi_settings()
