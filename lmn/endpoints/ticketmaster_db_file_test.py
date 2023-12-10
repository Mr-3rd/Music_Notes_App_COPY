import requests
import os
import json

ticketmaster_url = 'https://app.ticketmaster.com/discovery/v2/events'

api_key = 'CleWRaZrzLrHNHogFrXKKKz4S1LSbzwq'

API_key = os.environ.get('TICKETMASTER')

params = {
    'stateCode': 'MN',
    'keyword': 'concert',
    'apikey': api_key,
    'size': '200',
    'startDateTime': '2022-01-01T00:00:00Z', 
    'endDateTime': '2024-01-01T00:00:00Z',
    # 'sort': 'date,name,desc'
}

try:
    response = requests.get(ticketmaster_url, params=params)
    response.raise_for_status()

    data = response.json()

    # Specify the file path where you want to save the data
    file_path = 'text/ticketmaster_data.txt'

    with open(file_path, 'w') as file:
        # Write the JSON data to the file
        json.dump(data, file, indent=2)

    print(f"Data successfully saved to {file_path}")

except requests.exceptions.RequestException as err:
    print(f"Error during API call: {err}")
except ValueError as err:
    print(f"Error decoding JSON: {err}")