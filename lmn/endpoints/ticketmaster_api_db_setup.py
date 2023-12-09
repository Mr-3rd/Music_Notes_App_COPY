import ticketpy
import os

api_key = os.environ.get('TICKETMASTER')

tm_client = ticketpy.ApiClient(api_key)

pages = tm_client.events.find(
    state_code='MN',
    sort = 'random',
    start_date_time='2022-01-01T00:00:00Z',
    end_date_time='2024-01-01T00:00:00Z'
).limit(200)

for page in pages:
    for event in page:
        print(event)