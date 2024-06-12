import os
import json

# Get the absolute path of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the JSON file
json_file_path = os.path.join(base_dir, '../assets/data/countries.json')

with open(json_file_path) as file:
    countries = json.load(file)

class CountryService:
    def __init__(self):
        self.country_codes = countries

    def get_by_code(self, code):
        for country in self.country_codes:
            if country['code'] == code:
                return country
        return None

    def get_by_name(self, name):
        for country in self.country_codes:
            if country['name'] == name:
                return country
        return None

countryService = CountryService()