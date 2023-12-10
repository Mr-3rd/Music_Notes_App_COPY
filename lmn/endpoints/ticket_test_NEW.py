import requests
import os

ticketmaster_url = 'https://app.ticketmaster.com/discovery/v2/events'

api_key = os.environ.get('TICKETMASTER')

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

        # Tracking which artist, my query returns 60
        show_number = 0
        artist_number = 0
        venue_number = 0

        #the list of events is pulled above
        for event in data:

            
            show_number = show_number + 1

            #TODO: Create the data we save to the DB
            show_title = event['name']
            show_date = event['dates']['start']['localDate']

            #Some shows didn't have a local time, so I just made them all zeros
            if 'localTime' in event['dates']['start'].keys():
                event_time = event['dates']['start']['localTime']
            else:
                event_time = '00:00:00'
            
            # Save the Show Data
            file.write(f'--Show{show_number}-- \n') 
            file.write(f'Show: {show_title} \n')
            file.write(f'Date: {show_date} \n')
            file.write(f'Event Time: {event_time} \n')


            #find the venues
            venues = event["_embedded"]["venues"]

            # The list stores 1 venue for each time we collected above
            for venue in venues:
                venue_name = venue['name']
                venue_city = venue['city']['name']
                venue_state = venue['state']['name']
                stateCode = venue['state']['stateCode']
                venue_number = venue_number + 1

                #TODO: Save to DB
                file.write(f'venue {venue_number}: \n' +
                    f'Name: {venue_name} \n' +
                    f'City: {venue_city} \n' +
                    f'State: {venue_state} \n' +
                    f'Code: {stateCode} \n' +
                    f'\n' )
            
            # Some attractions did not have an artist name ( two local artist doing covers
            if 'attractions' in event["_embedded"].keys():
                if 'name' in event['_embedded']['attractions'][0]:

                    #TODO: Create the data for the artist
                    artist_name = event['_embedded']['attractions'][0]['name']
                    
                    #TODO: Save to DB
                    file.write(f'Artist: {artist_name} \n')
                    file.write('\n')


    #Create a "Local Artist # for the unknown local artists doing cover shows"
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

