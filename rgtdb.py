# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Reading events from RGTDB
# 
# Query to get JSON:
# 
# https://rgtdb.com/events/json?search=&offset=0&limit=100
# 
# This reads upcoming events from rgtdb.com and converts them into iCAL format and writes to a file for manual import. Then this saves or updates the events in a Google calendar.
# %% [markdown]
# ## Get data and cache response

# %%
import pandas as pd 

import datetime
from datetime import datetime as dt

import io
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.debug("Debug level logging turned on")

import requests
from cachecontrol import CacheControl
from cachecontrol.caches import FileCache
from cachecontrol.heuristics import ExpiresAfter

sess = requests.session()
cached_sess = CacheControl(sess, cache = FileCache('.web_cache'), heuristic=ExpiresAfter(hours=1))

try:
    response = cached_sess.get('https://rgtdb.com/events/json?search=&offset=0&limit=200') # Get 200 events. Should be about a week's worth of events
    response.raise_for_status()

except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')

logger.setLevel(logging.ERROR)

print(dt.now())


# %%
response.json().keys()

# %% [markdown]
# ## Convert JSON to Pandas Dataframe
# 
# Not necessary, but hey, pretending to be a data scientist feels cool.

# %%
df = pd.json_normalize(response.json(), 'rows')
df

# %% [markdown]
# ## Convert start time into datetime format - and guess at the year
# 
# This will be an issue every year around new year.

# %%

this_year = str(dt.today().year)
df['date'] = pd.to_datetime(df['startAt'] + ' ' + this_year, format='%m-%d %H:%M %Y', utc=True)
df.set_index('date', inplace=True)


# %%
df.head()

# %% [markdown]
# 
# 
# 
# %% [markdown]
# ## Use icalendar package to create ICAL format events
# 
# * GitHub: https://github.com/collective/icalendar
# 

# %%
from datetime import timedelta
from icalendar import vCalAddress, vText
from icalendar import Calendar, Event
import pytz

cal = Calendar()
cal.add('prodid', '-//My calendar product//mxm.com//')
cal.add('version', '2.0')

for index, row in df.iterrows():
    print(index, row['name'], row['tags'])
    event = Event()
    event['uid'] = row['detailsUrl']
    event.add('summary', str(row['name']) + ' ' + str(row['tags']) + ' ' + str(row['signUps']))
    event.add('dtstart', index)
    event.add('dtend', index  + timedelta(hours=1))
    event.add('url', 'https://rgtdb.com' + row['detailsUrl'])
    event.add('description', row['distance'] + ' ' + 'https://rgtdb.com' + row['detailsUrl'])
    event.add('color', 'Tomato')
    event['location'] = vText(row['roadName'])

    cal.add_component(event)

# %% [markdown]
# ## Write to File
# 
# Can use to manually import into Google, other calendars

# %%
import tempfile, os
f = open('./rgt_events.ics', 'wb')
f.write(cal.to_ical())
f.close()

# %% [markdown]
# ## Use gcsa for Simplified Access to Google Calendar API
# 
# * GitHub: https://github.com/kuzmoyev/google-calendar-simple-api
# * Docs: https://google-calendar-simple-api.readthedocs.io/en/latest/index.html
# 
# Need to add socket timeout of 5 minutes due to slow response on my machine
# 
# ### Shared Calendar
# 
# * Calendar ID: 3e8gau8bommfjk33j92rv5k7q0@group.calendar.google.com
# * Google sharing link: https://calendar.google.com/calendar/u/0?cid=M2U4Z2F1OGJvbW1mamszM2o5MnJ2NWs3cTBAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ
# * ICS format for e.g., Apple Calendar: https://calendar.google.com/calendar/ical/3e8gau8bommfjk33j92rv5k7q0%40group.calendar.google.com/public/basic.ics
# 

# %%
from gcsa.event import Event as gcEvent
from gcsa.google_calendar import GoogleCalendar
from gcsa.recurrence import Recurrence, DAILY, SU, SA

import socket
socket.setdefaulttimeout(300) # 5 minutes

EMAIL_FOR_CAL = '3e8gau8bommfjk33j92rv5k7q0@group.calendar.google.com'

calendar = GoogleCalendar(EMAIL_FOR_CAL)

# %% [markdown]
# ## Cleanup: Delete All Events from Google Calendar
# 
# Uncomment to clean up calendar.

# %%
#calendar.clear() # This gives an error in the Google API

#for event in calendar.get_events(time_min=df.index.min() - datetime.timedelta(days=1), time_max=df.index.max() + datetime.timedelta(days=1), timezone='UTC'):
#    print('Deleting:', event, event.event_id)
#    calendar.delete_event(event)

# %% [markdown]
# ## Find existing events, mark for update instead of creation

# %%
import re

reExtractName = re.compile(" \[\'.*")

df['cal_id'] = None
df['event_obj'] = None
df['found'] = False

for event in calendar.get_events(time_min=df.index.min() - datetime.timedelta(days=1), time_max=df.index.max() + datetime.timedelta(days=1), timezone='UTC'):

    print(event)

    rideName = reExtractName.sub("", event.summary) # Get substring from event summary with just the name

    df.loc[(df['name'] == rideName) & (df.index == event.start), ['found', 'cal_id', 'event_obj']] = [True, event.event_id, event]


# %%
df.loc[df['found'] == True]


# %%
df.loc[df['found'] == False]

# %% [markdown]
# ## Add All Events to Google Calendar

# %%
from gcsa.event import Event as gcEvent

for index, row in df.iterrows():

    evntSummary = str(str(row['name']) + ' ' + str(row['tags']) + ' ' + str(row['signUps']) + '/' + row['distance'] + '/' + row['elevationGain'])

    evntDescription = 'Signups: ' +  str(row['signUps']) + '\n' + 'Distance: ' + row['distance'] + '\n' +  'Elevation gain: ' + row['elevationGain'] + '\n' + 'Descent: ' + row['elevationLost'] + '\n' + 'https://rgtdb.com' + str(row['detailsUrl'])

    evntString = row['detailsUrl'].replace('/events/', '')

    if row['found'] == False:

        print('+New event: ', index, row['name'], row['tags'], evntString)

        evntColor = '1'

        if "groupride" in row['tags']:
            evntColor = '2'
        elif 'pro' in row['tags']:
            evntColor = '3'
        elif 'elimination' in row['tags']:
            evntColor = '4'
        elif "itt" in row['tags']:
            evntColor = '5'
        elif "race" in row['tags']:
            evntColor = '6'

        event = gcEvent(
            evntSummary,
            start=index,
            timezone='UTC',
            location=str(row['roadName']),
            description=evntDescription,
            event_id=evntString,
            color = evntColor
        )

        print('ID before add:', event.event_id)
        ret_event = calendar.add_event(event)
        print('ID after add:', event.event_id, 'Returned event ID:', ret_event.event_id)

    else:

        print('-Updating event: ', index, row['name'], row['tags'], evntString)

        event = row['event_obj']

        event.summary = evntSummary
        event.description = evntDescription

        calendar.update_event(event)


# %%
df.loc[df['signUps'] > 9]


# %%
df.loc[df['name'].str.startswith('Wacky Races')]


# %%



