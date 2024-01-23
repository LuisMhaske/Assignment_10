import requests
import geocoder
from datetime import datetime, timedelta


class Forecast:

    def __init__(self):
        self.api_base_url = "https://api.open-meteo.com/v1/forecast"
        self.results_file = "weather_results.txt"

    def get_weather(self, latitude, longitude, searched_date):
        api_url = (f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily"
                   f"=precipitation_sum&timezone=Europe%2FLondon&start_date={searched_date}&end_date={searched_date}")
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()

            precipitation_sum = data.get('daily', {}).get('precipitation_sum', {}).get(searched_date, 0.0)
            return precipitation_sum
        else:
            print(f"Error fetching weather data. Status code: {response.status_code}")
            return None

    def get_location_coordinates(self):
        while True:
            location = input("Enter the location (city, country): ")
            try:
                g = geocoder.osm(location)
                return g.latlng
            except Exception as e:
                print(f"Error: {e}, Please enter valid location.")

    def save_result_to_file(self, date, location, result):
        with open(self.results_file, "a") as file:
            file.write(f"{date} - {location}: {result}\n")

    def check_cached_result(self, searched_date, location):
        with open(self.results_file, "r") as file:
            lines = file.readline()
            for line in lines:
                if searched_date in line and location in line:
                    print(f"Result for {searched_date} in {location} found in file. Retrieving from cache.")
                    print(line.strip())
                    return True
        return False

    def main(self):
        user_date_input = input("Enter the date in 'YYYY-mm-dd' format (or press enter for next day): ").strip()
        if not user_date_input:
            next_day = datetime.now() + timedelta(days=1)
            searched_date = next_day.strftime("%Y-%m-%d")
        else:
            try:
                datetime.strptime(user_date_input, "%Y-%m-%d")
                searched_date = user_date_input
            except ValueError:
                print("Invalid date format. Please use 'YYYY-mm-dd'.")
                return

            location_coordinates = self.get_location_coordinates()
            latitude, longitude = location_coordinates
            location = geocoder.osm([latitude, longitude], method='reverse').address

            if self.check_cached_result(searched_date, location):
                return

            precipitation_sum = self.get_weather(latitude, longitude, searched_date)

            if precipitation_sum is not None:
                if precipitation_sum > 0.0:
                    result = f"It will rain. Precipitation value: {precipitation_sum}"
                elif precipitation_sum == 0.0:
                    result = "It will not rain."
                else:
                    result = "I don't know."

                print(result)
                self.save_result_to_file(searched_date, location, result)

        if __name__ == "__main__":
            weather_checker = Forecast
            weather_checker.main()

