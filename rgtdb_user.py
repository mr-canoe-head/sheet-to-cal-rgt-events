# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Get RGTDB Entries for One User
# 
# https://rgtdb.com/user/72763

# %%
import pandas as pd
from datetime import datetime as dt
import datetime

dfs = pd.read_html('https://rgtdb.com/user/72763')
df = dfs[1]

# %% [markdown]
# ## Convert date to datetime, attempt to guess the year
# 
# This is going to have troubles around New Year

# %%
event_year = str(dt.today().year)
year_subtract = 0
last_month = 13

for index, row in df.iterrows():
    event_month = int(row['Date'][:2])

    if event_month > last_month:
        year_subtract += 1
        event_year = str(dt.today().year - year_subtract)
        print(event_year + '-' + str(event_month))

    df.loc[index, 'Year_Date'] = event_year + '-' + row['Date']

    last_month = event_month
    
df['Year_Date'] = pd.to_datetime(df['Year_Date'], utc=True)
df.set_index('Year_Date', inplace=True)
df

# %% [markdown]
# ## Personal Calendar for Signups
# 
# g2oh32rptulp8f17e3bdiq9iec@group.calendar.google.com

# %%
from gcsa.event import Event as gcEvent
from gcsa.google_calendar import GoogleCalendar

import socket
socket.setdefaulttimeout(300) # 5 minutes

EMAIL_FOR_CAL = 'g2oh32rptulp8f17e3bdiq9iec@group.calendar.google.com'

calendar = GoogleCalendar(EMAIL_FOR_CAL)


# %%
df.index.max() 

# %% [markdown]
# ## Read Events in Calendar which Are Within Timeframe of RGDB Data
# 
# Add one day to timeframe to compensate for unpredictable time zone handling.
# 
# Note IDs of existing events so we don't re-create them.

# %%
df['cal_id'] = None
df['event_obj'] = None
df['found'] = False

for event in calendar.get_events(time_min=df.index.min() - datetime.timedelta(days=1), time_max=df.index.max() + datetime.timedelta(days=1), timezone='UTC'):

    df.loc[(df['Name'] == event.summary) & (df.index == event.start), ['found', 'cal_id', 'event_obj']] = [True, event.event_id, event]

    #if event.start in df.loc[df['Name'] == event.summary].index:
    #    df.at[event.start, 'cal_id'] = event.event_id
    #    df.at[event.start, 'event_obj'] = event
    #    print('found ', event, event.timezone, event.event_id)


# %%
df.loc[df['found'] == False]


# %%
for index, row in df.iterrows():

    if row['found'] == False:

        print('* Adding:', index, row['Name'])

        evntColor = '1'

        event = gcEvent(
            str(row['Name']),
            start=index,
            timezone='UTC',
            color = evntColor
        )
        ret_event = calendar.add_event(event)
        print('ID after add:', event.event_id, 'Returned event ID:', ret_event.event_id)

    else: 
        print('Skipping', index, row['Name'])


# %%



