import requests
from mysql import connector
import os

ticketmaster_url = 'https://app.ticketmaster.com/discovery/v2/events'

api_key = 'CleWRaZrzLrHNHogFrXKKKz4S1LSbzwq'

API_key = os.environ.get('TICKETMASTER')

params = {
    'stateCode': 'MN',
    'keyword': 'music',
    # 'dmaId': 324,
    'apikey': api_key,
    'size': '200',
    'startDateTime': '2022-01-01T00:00:00Z', 
    'endDateTime': '2024-01-01T00:00:00Z',
    'sort': 'date,name,desc'
}

try:
    response = requests.get(ticketmaster_url, params=params)

    response.raise_for_status()

    data = response.json()

    print(data) 
    print('\n')
    # for page in data:
    #     print(page)

except requests.exceptions.RequestException as err:
    print(f"Error during API call: {err}")
except ValueError as err:
    print(f"Error decoding JSON: {err}")