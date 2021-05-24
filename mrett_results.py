import pandas as pd

# Read spreadsheet several times to initialize:

df_MRETT_GC = pd.read_csv('https://docs.google.com/spreadsheets/d/' + 
                   '11uk0WpQzjVBOWs99cev9buajG1PalFdC5mtdynhqejU' +
                   '/export?gid=' + '1384530880' + '&format=csv',
                   index_col=1,
                  )

import time

for i in range(5):
    time.sleep(5) 
    pd.read_csv('https://docs.google.com/spreadsheets/d/' + 
                    '11uk0WpQzjVBOWs99cev9buajG1PalFdC5mtdynhqejU' +
                    '/export?' + '' + '&format=csv',
                    index_col=1,
                    )

# Read all spreadsheet tabs:

mrett_gids = {
    'GC' : '1384530880',
    '21' : '0',
    '22' : '601708178',
    '23' : '171816323',
    '24' : '1769801856',
    '25' : '1953569581',
    '26' : '1178762166'
}

df_mretts = {}

for mrett in mrett_gids.keys():
    #print(mrett, mrett_gids[mrett])
    gid = mrett_gids[mrett]
    df_mretts[mrett] = pd.read_csv('https://docs.google.com/spreadsheets/d/' + '11uk0WpQzjVBOWs99cev9buajG1PalFdC5mtdynhqejU' + '/export?gid=' + gid + '&format=csv', index_col=1, na_values=['', ' '])

# Repair missing data
if pd.isna(df_mretts['GC']['MRETT21'].iloc[0]):
    df_mretts['GC'].at['eCKD 1', 'MRETT21'] = 200
    df_mretts['GC'].at['Rasio Racing', 'MRETT21'] = 190
    df_mretts['GC'].at['The Pedalers', 'MRETT21'] = 170
    df_mretts['GC'].at['Pocomotion', 'MRETT21'] = 175
    df_mretts['GC'].at['OTR Black', 'MRETT21'] = 165
    df_mretts['GC'].at['KISS Racing Team 1', 'MRETT21'] = 150
    df_mretts['GC'].at['Moon Riders', 'MRETT21'] = 160
    df_mretts['GC'].at['OTR Blue', 'MRETT21'] = 155
    df_mretts['GC'].at['OTR Green', 'MRETT21'] = 141
    df_mretts['GC'].at['Team Lou Racing Squad', 'MRETT21'] = 137
    df_mretts['GC'].at['eCKD 2', 'MRETT21'] = 145
    df_mretts['GC'].at['Westerley CC Purple', 'MRETT21'] = 129
    df_mretts['GC'].at['WKG Renegades', 'MRETT21'] = 125
    df_mretts['GC'].at['Westerlies', 'MRETT21'] = 0
    df_mretts['GC'].at['RGT France 1', 'MRETT21'] = 189
    df_mretts['GC'].at['Team Lou Too', 'MRETT21'] = 0
    df_mretts['GC'].at['Les Watts', 'MRETT21'] = 0
    df_mretts['GC'].at['Tricky Allsorts', 'MRETT21'] = 133
    df_mretts['GC']['Total']  = df_mretts['GC']['Total'] + df_mretts['GC']['MRETT21'] 

# GC Results

import pandas_bokeh
import bokeh
from bokeh.themes import built_in_themes
from bokeh.io import curdoc

GC_html_graph = df_mretts['GC'][::-1].loc[:,'MRETT21':'MRETT26'].fillna(0).plot_bokeh.barh(
    ylabel="Team",
    xlabel="Points", 
    title="MRETT Series 2 GC", 
    stacked=True,
    alpha=0.6,
    figsize=(1600, 600),
    legend = "bottom_right",
    sizing_mode="scale_width",
    return_html=True, show_figure=False
    )

GC_html_table = df_mretts['GC'].to_html(classes=['uk-table', 'uk-table-small', 'uk-table-hover', 'uk-table-divider'], border=0)

# Stage Results 

for mrett in mrett_gids.keys():
    if mrett != 'GC':
        df_mretts[mrett]['timedelta'] = pd.to_timedelta(df_mretts[mrett].Time) 
        df_mretts[mrett]['Time in Seconds'] = df_mretts[mrett]['timedelta'].dt.total_seconds() 
        df_mretts[mrett]['Time in Minutes'] = df_mretts[mrett]['Time in Seconds']/60
        df_mretts[mrett]['Time in Minutes Truncated'] = divmod(df_mretts[mrett]['Time in Seconds'], 60)[0] 
        df_mretts[mrett]['Time Remainder in Seconds'] = divmod(df_mretts[mrett]['Time in Seconds'], 60)[1] 
        df_mretts[mrett]['Team Name'] = df_mretts[mrett].index

stage_html_graphs = ''

for mrett in mrett_gids.keys():
    if mrett != 'GC':
        out_html = df_mretts[mrett][::-1].plot_bokeh.barh(    
            title = 'MRETT' + mrett,
            xlabel = 'Time (Minutes)',
            y='Time in Minutes',
            alpha=0.6,
            figsize=(1600, 600),
            legend = "top_right",
            hovertool_string="""<h2> #@{#} 
                                @{Team Name} </h2>
                                <h3> Time: @{Time} </h3>""",
            sizing_mode="scale_width",
            return_html=True, show_figure=False
            )

        out_table_html = df_mretts[mrett][['#', 'Time', 'Diff', 'Points']].to_html(classes=['uk-table', 'uk-table-small', 'uk-table-hover', 'uk-table-divider'], border=0)

        stage_html_graphs = stage_html_graphs + '<hr>' + '<h3>' + 'MRETT' + mrett + '</h3>' + '<p>' + out_html + '</p><p>' + out_table_html + '</p>'

print('''<html><head><title>MRETT Series 2</title>        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        
        <!-- UIkit CSS -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/uikit@3.6.22/dist/css/uikit.min.css" />

        <!-- UIkit JS -->
        <script src="https://cdn.jsdelivr.net/npm/uikit@3.6.22/dist/js/uikit.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/uikit@3.6.22/dist/js/uikit-icons.min.js"></script>

        </head><body><h1>MRETT Series 2</h1>''')
print(GC_html_graph, GC_html_table, stage_html_graphs)
print('</body></html>')