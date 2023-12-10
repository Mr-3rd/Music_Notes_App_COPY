from django.core.management.base import BaseCommand
import requests
import os
from lmn.models import Artist, Venue, Show

class Command(BaseCommand):
    help = 'my custom'

    def handle(self, *args, **options):
        ticketmaster_url = 'https://app.ticketmaster.com/discovery/v2/events'
        api_key = os.environ.get('TICKETMASTER')

        params = {
            'stateCode': 'MN',
            'classificationName': 'music',
            'apikey': api_key,
            'size': '200',
            'pageSize': '200',
            'pageNumber': '200',
            'startDateTime': '2022-01-01T00:00:00Z',
            'endDateTime': '2024-01-01T00:00:00Z',
            # 'sort': 'random',
        }

        try:
            response = requests.get(ticketmaster_url, params=params)
            response.raise_for_status()
            data = response.json()

            # Insert data into Django models
            for event in data["_embedded"]["events"]:
                show_date = event['dates']['start']['localDate']
                event_time = event['dates']['start'].get('localTime', '00:00:00')

                # Insert Venue data
                venues = event["_embedded"]["venues"]
                for venue in venues:
                    venue_name = venue['name']
                    venue_city = venue['city']['name']
                    venue_state = venue['state']['name']

                    # Check if Venue already exists
                    venue_instance, created = Venue.objects.get_or_create(name=venue_name, city=venue_city, state=venue_state)

                # Insert Artist data
                if 'attractions' in event["_embedded"] and event['_embedded']['attractions'][0].get('name'):
                    artist_name = event['_embedded']['attractions'][0]['name']

                    # Check if Artist already exists
                    artist_instance, created = Artist.objects.get_or_create(name=artist_name)

                # Insert Show data
                show_date_time = show_date + ' ' + event_time

                # Check if Show already exists < I assume this is where the constraint is stalling the build
                show_instance, created = Show.objects.get_or_create(show_date=show_date_time, artist_id=artist_instance.pk, venue_id=venue_instance.pk)

            print("Data successfully saved to Django models")

        except requests.exceptions.RequestException as err:
            print(f"Error during API call: {err}")
        except ValueError as err:
            print(f"Error decoding JSON: {err}")