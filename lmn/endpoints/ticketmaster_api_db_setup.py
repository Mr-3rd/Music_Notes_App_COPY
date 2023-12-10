import requests
import os
from ..models import Artist, Venue, Show

ticketmaster_url = 'https://app.ticketmaster.com/discovery/v2/events'
api_key = 'CleWRaZrzLrHNHogFrXKKKz4S1LSbzwq'
API_key = os.environ.get('TICKETMASTER')

params = {
    'stateCode': 'MN',
    'classificationName': 'music',
    'apikey': api_key,
    'size': '200',
    'pageSize': '200',
    'pageNumber': '200',
    'startDateTime': '2022-01-01T00:00:00Z',
    'endDateTime': '2024-01-01T00:00:00Z',
    'sort': 'random',
}

try:
    response = requests.get(ticketmaster_url, params=params)
    response.raise_for_status()
    data = response.json()

    # Insert data into Django models
    for event in data["_embedded"]["events"]:
        # We do not need show title
        # show_title = event['name']

        # Get the show data now, but hold off on saving it

        #Every show has a date
        show_date = event['dates']['start']['localDate']
        # Use a get method to search for localTime or enter in all 000 for unknown/ TBD events
        event_time = event['dates']['start'].get('localTime', '00:00:00')

        # Insert Venue data
        venues = event["_embedded"]["venues"]
        for venue in venues:
            venue_name = venue['name']
            venue_city = venue['city']['name']
            venue_state = venue['state']['name']

            # State code saved for future iteration
            # stateCode = venue['state']['stateCode']

            venue_instance = Venue(name=venue_name, city=venue_city, state=venue_state)
            venue_instance.save()

        # Insert Artist data
        if 'attractions' in event["_embedded"] and event['_embedded']['attractions'][0].get('name'):
            artist_name = event['_embedded']['attractions'][0]['name']

            artist_instance = Artist(name=artist_name)
            artist_instance.save()

        # Insert Show data
        show_date_time = show_date +' ' + event_time

        show_instance = Show(show_date=show_date_time, artist_id=artist_instance.pk, venue_id=venue_instance.pk)
        show_instance.save()
    print("Data successfully saved to Django models")

except requests.exceptions.RequestException as err:
    print(f"Error during API call: {err}")
except ValueError as err:
    print(f"Error decoding JSON: {err}")