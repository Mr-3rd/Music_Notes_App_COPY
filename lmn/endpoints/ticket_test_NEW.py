import requests
import os
import json

ticketmaster_url = 'https://app.ticketmaster.com/discovery/v2/events'

api_key = 'CleWRaZrzLrHNHogFrXKKKz4S1LSbzwq'

API_key = os.environ.get('TICKETMASTER')

params = {
    'stateCode': 'MN',
    'classificationName': 'music',
    'apikey': api_key,
    'size': '200',
    'pageSize':'200',
    'pageNumber': '200',
    'startDateTime': '2022-01-01T00:00:00Z', 
    'endDateTime': '2024-01-01T00:00:00Z',
    'sort': 'random',
}

try:
    response = requests.get(ticketmaster_url, params=params)
    response.raise_for_status()

    data = response.json()

    file_path = 'lmn\endpoints\\ticketmaster_data.txt'

    #locate and store just events
    data = data["_embedded"]["events"]



    with open(file_path, 'w') as file:

        show_number = 0
        artist_number = 0
        venue_number = 0

        for event in data:

            show_number = show_number + 1
            show_title = event['name']
            show_date = event['dates']['start']['localDate']

            if 'localTime' in event['dates']['start'].keys():

                event_time = event['dates']['start']['localTime']
            else:
                event_time = '00:00:00'
            

            file.write(f'--Show{show_number}-- \n') 

            file.write(f'Show: {show_title} \n')
            
            file.write(f'Date: {show_date} \n')

            file.write(f'Event Time: {event_time} \n')

            file.write(f'\n')
            
            venues = event["_embedded"]["venues"]
            
            for venue in venues:
                venue_name = venue['name']
                venue_city = venue['city']['name']
                venue_state = venue['state']['name']
                stateCode = venue['state']['stateCode']
                venue_number = venue_number + 1

                file.write(f'venue {venue_number}: \n' +
                    f'Name: {venue_name} \n' +
                    f'City: {venue_city} \n' +
                    f'State: {venue_state} \n' +
                    f'Code: {stateCode} \n' +
                    f'\n' )
            
            if 'attractions' in event["_embedded"].keys():

                if 'name' in event['_embedded']['attractions'][0]:

                    artist_name = event['_embedded']['attractions'][0]['name']

                    file.write(f'Artist: {artist_name} \n')
                    file.write('\n')
                else:
                    artist_number = artist_number + 1
                    file.write(f'Artist: Local Artist {artist_number} \n')

            else:
                artist_number += 1
                file.write(f'Artist: Local Artist {artist_number} \n')

    print(f"Data successfully saved to {file_path}")

except requests.exceptions.RequestException as err:
    print(f"Error during API call: {err}")
except ValueError as err:
    print(f"Error decoding JSON: {err}")

