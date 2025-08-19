import os
import logging
import argparse
from csv import excel

import yaml
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WeatherDataFetcher:
    BASE_URL = "api_path"

    def __init__(self):
        # Setup logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.__logger = logging.getLogger(self.__name__)

        # Load config file
        try:
            with open("config.yaml", "r") as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            self.__logger.error("Missing configuration file!")

    def __login(self):
        username = os.getenv("API_USER")
        user_password = os.getenv("API_PWD")

    def __logout(self):
        pass

    def get_weather_forecast(self, city:str, units: str):
        pass


def main():
    parser = argparse.ArgumentParser(description="Weather Data Fetcher")
    parser.add_argument("--city", help="City name")
    parser.add_argument("--units", choices=["metric", "imperial"], help="Units")
    args = parser.parse_args()

    data_fetcher = WeatherDataFetcher()
    data_fetcher.get_weather_forecast(args.city, args.units)


if __name__ == "__main__":
    main()
