import requests
import os
import json

ticketmaster_url = 'https://app.ticketmaster.com/discovery/v2/events'

api_key = os.environ.get('TICKETMASTER')

params = {
    'stateCode': 'MN',
    # 'keyword': 'concert',
    'classificationName': 'music',
    'apikey': api_key,
    'size': '200',
    'pageSize':'200',
    'pageNumber': '200',
    # 'source': 'ticketmaster',
    'startDateTime': '2022-01-01T00:00:00Z', 
    'endDateTime': '2024-01-01T00:00:00Z',
    'sort': 'random',
    # 'sort': 'date,name,desc',
    # 'type': 'event',
    # 'type': 'venue'
}

try:
    response = requests.get(ticketmaster_url, params=params)
    response.raise_for_status()

    data = response.json()

    # Specify the file path where you want to save the data
    # file_path = 'text/ticketmaster_data.txt'
    file_path = 'lmn\endpoints\\ticketmaster_data.txt'

    with open(file_path, 'w') as file:
        # Write the JSON data to the file
        json.dump(data, file, indent=2)
        json.dump(data, file, indent=2)

    print(f"Data successfully saved to {file_path}")

    #locate and store just events
    data2 = data["_embedded"]["events"]

    show_number = 0
    artist_number = 0
    venue_number = 0

    for event in data2:

        # for item in event:
        #     print('------------------')
        #     print(item)

        show_number = show_number + 1

        print(f'--Show{show_number}--') 

        show_title = event['name']

        print(f'Show: ', show_title)
        
        show_date = event['dates']['start']['localDate']

        print(f'Date: ', show_date)

        if 'localTime' in event['dates']['start'].keys():

            event_time = event['dates']['start']['localTime']
        else:
            event_time = '00:00:00'

        print(f'Event Time: ', event_time)

        # print(event['dates']["start"].keys())
        # print('---------------------------------------------------------------------------')

        # print(event["_embedded"]["venues"])
        
        venues = event["_embedded"]["venues"]
        
        for venue in venues:
            venue_name = venue['name']
            venue_city = venue['city']['name']
            venue_state = venue['state']['name']
            stateCode = venue['state']['stateCode']
            venue_number = venue_number + 1

            print(f'venue {venue_number}: \n' +
                  f'Name: ', venue_name + '\n' +
                  f'City: ', venue_city + '\n' +
                  f'State: ', venue_state + '\n' +
                  f'Code: ', stateCode + '\n' +
                  f'------------------------------' )
        
        if 'attractions' in event["_embedded"].keys():

            if 'name' in event['_embedded']['attractions'][0]:

                artist_name = event['_embedded']['attractions'][0]['name']

                print('Artist: ', artist_name)
            else:
                artist_number = artist_number + 1
                print('Artist: Local Artist ', artist_number)

        else:
            artist_number += 1
            print('Artist: artists', artist_number)

        print('---------------------------------------------------------------------------')

    file_path2 = 'lmn\endpoints\\ticketmaster_events.txt'

    with open(file_path2, 'w') as file2:
        for event in data2:
            file2.write(json.dumps(event, indent=2))  # Write event
            file2.write("\n" + "-" * 25 + "\n")  # Add separator
        # json.dump(data2, file2, indent=2)

    print(f"Data successfully saved to {file_path2}")

except requests.exceptions.RequestException as err:
    print(f"Error during API call: {err}")
except ValueError as err:
    print(f"Error decoding JSON: {err}")
