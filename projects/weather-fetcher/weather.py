import os
import logging
import argparse
import base64
import yaml
import requests
from datetime import datetime, UTC
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WeatherDataFetcher:
    BASE_URL = "api_path"

    def __init__(self):
        # Setup logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.__logger = logging.getLogger(self.__class__.__name__)

        # Load config file
        try:
            with open("config.yaml", "r") as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            self.__logger.error("Missing configuration file!")

        self.__access_token:str = ""

    def login(self):
        username = os.getenv("API_USER")
        user_password = os.getenv("API_PWD")

        credentials = base64.b64encode(f"{username}:{user_password}".encode("utf-8")).decode("utf-8")
        auth_header = {'Authorization': f"Basic {credentials}"}

        login_url = self.config['meteomatics']['login_url']
        response = requests.get(url= login_url, headers=auth_header)
        if response.status_code == 200:
            response_payload = response.json()
            self.__logger.info("Login successful!")
            self.__access_token = response_payload['access_token']
        else:
            self.__logger.error("Failed to login!")

    def logout(self):
        self.__logger.info("Logout from API!")
        self.__access_token = ""

    @staticmethod
    def __validate_location(latitude: float, longitude: float) -> str:
        if (latitude > 90) or (latitude < -90):
            raise ValueError("Invalid latitude, must be between -90 and 90")

        if (longitude > 180) or (longitude < -180):
            raise ValueError("Invalid longitude, must be between -180 and 180")

        return f"{round(latitude, 6)},{round(longitude, 6)}"

    def __build_url_request(self, interval:str, location:str, units:str) -> str:
        base_url = self.config['meteomatics']['base_url']

        if units == "metric":
            parameters = "t_2m:C"
        elif units == "imperial":
            parameters = "t_2m:F"
        else:
            self.__logger.error(f"Request for invalid unit: {units}")
            raise ValueError("Invalid unit")

        complete_url = f"{base_url}/{interval}/{parameters}/{location}/json"
        return complete_url

    @staticmethod
    def __process_response(payload) -> dict:
        temperature_response = {
            "latitude": None,
            "longitude": None,
            "date": None,
            "temperature": None
        }

        for response_data in payload['data']:
            for place in response_data['coordinates']:
                temperature_response['latitude'] = place['lat']
                temperature_response['longitude'] = place['lon']
                temperature_response['date'] = place['dates'][0]['date']
                temperature_response['temperature'] = place['dates'][0]['value']

        return temperature_response

    def get_current_temperature(self, latitude: float, longitude:float, units: str) -> dict | None:
        self.__logger.info("Current temperature requested!")
        if not self.__access_token:
            self.login()
        auth_header = {'Authorization': f"Bearer {self.__access_token}"}

        location = self.__validate_location(latitude, longitude)
        interval = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        request_url = self.__build_url_request(interval, location, units)

        response = requests.get(url= request_url, headers=auth_header)
        if response.status_code == 200:
            response_payload = response.json()

            self.__logger.info("Successfully fetch temperature data!")
            return self.__process_response(response_payload)

        return None

def main():
    parser = argparse.ArgumentParser(description="Weather Data Fetcher")
    parser.add_argument("--latitude", default= 52.52081958147629, help="Latitude")
    parser.add_argument("--longitude", default= 13.4094293014525, help="Longitude")
    parser.add_argument("--units", default="metric", choices=["metric", "imperial"], help="Units")
    args = parser.parse_args()

    data_fetcher = WeatherDataFetcher()
    result = data_fetcher.get_current_temperature(args.latitude, args.longitude, args.units)
    print(result)


if __name__ == "__main__":
    main()
