"""
Name: Zehui Yuan
Course: CS602 SN1
Data: New York City Vehicle Collisions, 2015 to present
URL: Link to your web application online (see extra credit)
Description: This program aims to let users put their desired date/time and boroughs, then get some analysis charts
            including line chart, bar chart, and geographic map based on their aim and preference. These charts will
            help them better understand New York City vehicle collisions situations from 2015 to 2017, for example,
            the relationship between collisions and date/time, the relationship between collision and day of week,
            distribution of collision in New York City, etc.
"""

import pandas as pd
import numpy as np
import datetime
from datetime import datetime, timedelta
import altair as alt
import pydeck as pdk
import streamlit as st
from PIL import Image


# set page layout
st.set_page_config(page_title='New York City Vehicle Collisions Analysis', layout='wide')


# read cvs data
data = pd.read_csv('nyc_veh_crash_sample.csv')


# set title of the project
st.title('🚘 New York City Vehicle Collisions Analysis (2015 to 2017)')

# insert a picture
Image.open('collision.jpeg').convert('RGB').save('new.jpeg')
image = Image.open('new.jpeg')
st.image(image, caption='Vehicle Collision',width=750)

# set intro of the project
intro = '<p style="font-family:sans-serif; color:Grey; ' \
                  'font-size: 15px;">The vehicle collision database includes the date and time, location ' \
        '(as borough, street names, zip code and latitude and longitude coordinates), injuries and fatalities, ' \
        'vehicle number and types, and related factors for all 5000 collisions in New York City during January 2015 ' \
        'and February 2017. The vehicle collision data was collected by the NYPD and published by NYC OpenData.</p>'
st.markdown(intro, unsafe_allow_html=True)


# widget 1: choose the time frame
option_t = st.sidebar.selectbox(
    '*(Required)* Please select time frame you want:',
    ('<select>', 'Only Date (e.g., 07/29/2015)', 'Only Time (e.g., 8:03:00 PM)',
     'Date+Time (e.g., 07/29/2015 8:03:00 PM)')
)


# widget 2: Date/Time selection
# data time range generation
def datetime_range(start, end, delta):
    current = start
    while current < end:
        yield current
        current += delta
dts = [dt.strftime('%H:%M') for dt in datetime_range(datetime(2016, 9, 1, 0), datetime(2016, 9, 2),
       timedelta(minutes=10))]
dts.append('23:59')
row = np.arange(0, 145, 1)
t_dic = {}
for i in range(0, 145):
    t_dic[row[i]] = dts[i]
# show following selection based on the time frame chosen
# find the range of date in the dataset
list_of_dates = [datetime.strptime(date_str, '%m/%d/%Y') for date_str in data['DATE']]
max_date = max(list_of_dates)
min_date = min(list_of_dates)
def show_option_dt(option_t):
    start_date = min_date
    end_date = max_date
    start_date_str = ''
    end_date_str = ''
    start_time_str = ''
    end_time_str = ''
    if option_t == 'Only Date (e.g., 07/29/2015)':
        start_date = st.sidebar.date_input('Please select the start date:', datetime.strptime('01/01/2015', '%m/%d/%Y'))
        end_date = st.sidebar.date_input('Please select the end date:', datetime.strptime('02/28/2017', '%m/%d/%Y'))
        if start_date.strftime('%Y/%m/%d') >= min_date.strftime('%Y/%m/%d') and end_date.strftime('%Y/%m/%d') <= max_date.strftime('%Y/%m/%d') and end_date.strftime('%Y/%m/%d') >= start_date.strftime('%Y/%m/%d'):
            st.write('Your selected date from  __', start_date.strftime('%m/%d/%Y'), '__  to  __', end_date.strftime('%m/%d/%Y'),'__')
            start_date_str = start_date.strftime('%m/%d/%Y')
            end_date_str = end_date.strftime('%m/%d/%Y')
        elif start_date.strftime('%Y/%m/%d') >= min_date.strftime('%Y/%m/%d') and end_date.strftime('%Y/%m/%d') <= max_date.strftime('%Y/%m/%d') and end_date.strftime('%Y/%m/%d') < start_date.strftime('%Y/%m/%d'):
            st.write('__Error!__ End date __cannot__ be less than the start date! Please select again.')
            text = '<p style="font-family:sans-serif; color:Red; ' \
                  'font-size: 8px;">**Error: End date cannot be less than the start date! Please select again.</p>'
            st.sidebar.markdown(text, unsafe_allow_html=True)
            start_date = datetime.strptime('2014/01/01', '%Y/%m/%d')
            end_date = datetime.strptime('2014/01/01', '%Y/%m/%d')
            start_date_str = start_date.strftime('%m/%d/%Y')
            end_date_str = end_date.strftime('%m/%d/%Y')
        else:
            st.write('__Error!__ Please select date between __2015/01/01__ and __2017/02/28__.')
            text = '<p style="font-family:sans-serif; color:Red; ' \
                  'font-size: 8px;">**Error: Please select date between 2015/01/01 and 2017/02/28.</p>'
            st.sidebar.markdown(text, unsafe_allow_html=True)
            start_date = datetime.strptime('2014/01/01', '%Y/%m/%d')
            end_date = datetime.strptime('2014/01/01', '%Y/%m/%d')
            start_date_str = start_date.strftime('%m/%d/%Y')
            end_date_str = end_date.strftime('%m/%d/%Y')
    elif option_t == 'Only Time (e.g., 8:03:00 PM)':
        time = st.sidebar.slider('Please select the start time and the end time:', 0, 6*24, (0, 6*24))
        clarify = '<p style="font-family:sans-serif; color:CadetBlue; ' \
                  'font-size: 8px;">*Note: 0 represents 00:00, 143 represents 23:50. Increasing by 1 means increasing by ' \
                  '10 minutes.</p>'
        st.sidebar.markdown(clarify, unsafe_allow_html=True)
        st.write('Your selected time  __', t_dic[time[0]], '__  to  __', t_dic[time[1]], '__')
        start_time_str = t_dic[time[0]]
        end_time_str = t_dic[time[1]]
    elif option_t == 'Date+Time (e.g., 07/29/2015 8:03:00 PM)':
        start_date = st.sidebar.date_input('Please select the start date:', datetime.strptime('01/01/2015', '%m/%d/%Y'))
        end_date = st.sidebar.date_input('Please select the end date:', datetime.strptime('02/28/2017', '%m/%d/%Y'))
        if start_date.strftime('%Y/%m/%d') >= min_date.strftime('%Y/%m/%d') and end_date.strftime('%Y/%m/%d') <= max_date.strftime('%Y/%m/%d') and end_date.strftime('%Y/%m/%d') >= start_date.strftime('%Y/%m/%d'):
            st.write('Your selected date from  __', start_date.strftime('%m/%d/%Y'), ' __to__', end_date.strftime('%m/%d/%Y'), '__')
            start_date_str = start_date.strftime('%m/%d/%Y')
            end_date_str = end_date.strftime('%m/%d/%Y')
        elif start_date.strftime('%Y/%m/%d') >= min_date.strftime('%Y/%m/%d') and end_date.strftime('%Y/%m/%d') <= max_date.strftime('%Y/%m/%d') and end_date.strftime('%Y/%m/%d') < start_date.strftime('%Y/%m/%d'):
            st.write('__Error!__ End date __cannot__ be less than the start date! Please select again.')
            text = '<p style="font-family:sans-serif; color:Red; ' \
                  'font-size: 8px;">**Error: End date cannot be less than the start date！ Please select again.</p>'
            st.sidebar.markdown(text, unsafe_allow_html=True)
            start_date = datetime.strptime('2014/01/01', '%Y/%m/%d')
            end_date = datetime.strptime('2014/01/01', '%Y/%m/%d')
            start_date_str = start_date.strftime('%m/%d/%Y')
            end_date_str = end_date.strftime('%m/%d/%Y')
        else:
            st.write('__Error!__ Please select date between __2015/01/01__ and __2017/02/28__.')
            text = '<p style="font-family:sans-serif; color:Red; ' \
                  'font-size: 8px;">**Error: Please select date between 2015/01/01 and 2017/02/28.</p>'
            st.sidebar.markdown(text, unsafe_allow_html=True)
            start_date = datetime.strptime('2014/01/01', '%Y/%m/%d')
            end_date = datetime.strptime('2014/01/01', '%Y/%m/%d')
            start_date_str = start_date.strftime('%m/%d/%Y')
            end_date_str = end_date.strftime('%m/%d/%Y')
        time = st.sidebar.slider('Please select the start time and the end time for analysis:', 0, 144, (0, 6*24))
        clarify = '<p style="font-family:sans-serif; color:CadetBlue; ' \
                  'font-size: 8px;">*Note: 0 represents 00:00, 143 represents 23:50. Increasing by 1 means increasing by ' \
                  '10 minutes.</p>'
        st.sidebar.markdown(clarify, unsafe_allow_html=True)
        st.write('Your selected time from  __', t_dic[time[0]], ' __  to  __ ', t_dic[time[1]], '__')
        start_time_str = t_dic[time[0]]
        end_time_str = t_dic[time[1]]
    return start_date_str, end_date_str, start_time_str, end_time_str


# widget 3: Borough multi-check selection
def borough_select():
    if option_t == '<select>':
        option_b = []
    else:
        muticheck_title = '<p style="font-family:sans-serif; color:Black; ' \
                  'font-size: 12px;">Please select boroughs you want for analysis:</p>'
        st.sidebar.markdown(muticheck_title, unsafe_allow_html=True)
        notes = '<p style="font-family:sans-serif; color:CadetBlue; ' \
                  'font-size: 8px;">*Note: not checking any of the check box means select all boroughs.</p>'
        st.sidebar.markdown(notes, unsafe_allow_html=True)

        option_1 = st.sidebar.checkbox('Bronx')
        option_2 = st.sidebar.checkbox('Brooklyn')
        option_3 = st.sidebar.checkbox('Manhattan')
        option_4 = st.sidebar.checkbox('Queens')
        option_5 = st.sidebar.checkbox('Staten Island')
        option_bool = [option_1,option_2,option_3,option_4,option_5]
        BOROUGH = ['Bronx', 'Brooklyn', 'Manhattan', 'Queens', 'Staten Island']
        option_b = []
        for i in range(0, 5):
            if option_bool[i]:
                option_b.append(BOROUGH[i].upper())
    return option_b


# widget 4: Columns selection - users can choose which columns he/she wants to display (multi-selection)
def column_select():
    if option_t == '<select>':
        option_c = []
    else:
        data_columns = data.columns
        data_columns_list = [columns for columns in data_columns]
        option_c = st.sidebar.multiselect('Please select the columns to display:', data_columns_list)
        notes = '<p style="font-family:sans-serif; color:CadetBlue; ' \
                  'font-size: 8px;">*Note: not selecting any of the conlumn means select all conlumns.</p>'
        st.sidebar.markdown(notes, unsafe_allow_html=True)
    return option_c


# add "Analyze" button to let user press to get output based on their choice
def set_button():
    m = st.markdown("""
    <style>
        div.stButton > button:first-child {
        background-color: #708090;
        border-color: #708090;
        color: #F8F8FF;
        border-radius: 10%;
        height: 2.5em;
        width: 6.5em;
        font: "Cursive";
        font-size: 1.4em;
        font-weight: bold
        }
    </style>""", unsafe_allow_html=True)
    button = st.sidebar.button("Analyze")
    return button


# display the data based on the time frame, date/time, borough and columns selection
# date formatting: convert 12/31/2016 to 2016/12/31
def date_format(str):
    formatted = str.split('/')[2]+'/'+str.split('/')[0]+'/'+str.split('/')[1]
    return formatted
# time formatting: convert 8:00 to 08:00
def time_format(str):
    time_formatted = ''
    if str.split(':')[0] in ['0','1','2','3','4','5','6','7','8','9']:
        time_formatted = '0'+str.split(':')[0]+':'+str.split(':')[1]
    else:
        time_formatted = str
    return time_formatted

def show_option_dataframe(option_t, option_b, option_c, start_date_str, end_date_str, start_time_str, end_time_str):
    # replace the old time with formatted time
    data['TIME'] = pd.Series([time_format(date) for date in data['TIME']])
    # add converted date column into the original data
    data['DATE_C'] = pd.Series([date_format(date) for date in data['DATE']])
    data_filtered = pd.DataFrame()
    if option_t == '<select>':
        if option_c == [] and option_b == []:
            st.write('__Data Display:__')
            data.sort_values(['DATE_C', 'TIME'], ascending=[True, True], inplace=True)
            data.drop(columns=['DATE_C'], inplace=True)
            st.dataframe(data)
            data_filtered = data
    elif option_t == 'Only Date (e.g., 07/29/2015)':
        if option_c == [] and option_b == []:
            st.write('__Data Display:__')
            data_dt = data[(data['DATE_C'] >= date_format(start_date_str)) & (data['DATE_C'] <= date_format(end_date_str))]
            data_dt.sort_values(['DATE_C', 'TIME'], ascending=[True, True], inplace=True)
            data_dt.drop(columns=['DATE_C'], inplace=True)
            st.dataframe(data_dt)
            data_filtered = data_dt
        elif option_c == [] and option_b != []:
            st.write('__Data Display:__')
            data_dt = data[(data['DATE_C'] >= date_format(start_date_str)) & (data['DATE_C'] <= date_format(end_date_str))]
            data_dt.sort_values(['DATE_C', 'TIME'], ascending=[True, True], inplace=True)
            data_dt.drop(columns=['DATE_C'], inplace=True)
            data_dt_borough = data_dt[data_dt['BOROUGH'].isin(option_b)]
            st.dataframe(data_dt_borough)
            data_filtered = data_dt_borough
        elif option_c != [] and option_b == []:
            st.write('__Data Display:__')
            data_dt = data[(data['DATE_C'] >= date_format(start_date_str)) & (data['DATE_C'] <= date_format(end_date_str))]
            data_dt.sort_values(['DATE_C', 'TIME'], ascending=[True, True], inplace=True)
            data_dt.drop(columns=['DATE_C'], inplace=True)
            st.dataframe(data_dt[option_c])
            data_filtered = data_dt
        else:
            st.write('__Data Display:__')
            data_dt = data[(data['DATE_C'] >= date_format(start_date_str)) & (data['DATE_C'] <= date_format(end_date_str))]
            data_dt.sort_values(['DATE_C', 'TIME'], ascending=[True, True], inplace=True)
            data_dt.drop(columns=['DATE_C'], inplace=True)
            data_dt_borough = data_dt[data_dt['BOROUGH'].isin(option_b)]
            st.dataframe(data_dt_borough[option_c])
            data_filtered = data_dt_borough
    elif option_t == 'Only Time (e.g., 8:03:00 PM)':
        if option_c == [] and option_b == []:
            st.write('__Data Display:__')
            data_dt = data[(data['TIME'] >= start_time_str) & (data['TIME'] <= end_time_str)]
            data_dt.sort_values(['DATE_C', 'TIME'], ascending=[True, True], inplace=True)
            data_dt.drop(columns=['DATE_C'], inplace=True)
            st.dataframe(data_dt)
            data_filtered = data_dt
        elif option_c == [] and option_b != []:
            st.write('__Data Display:__')
            data_dt = data[(data['TIME'] >= start_time_str) & (data['TIME'] <= end_time_str)]
            data_dt.sort_values(['DATE_C', 'TIME'], ascending=[True, True], inplace=True)
            data_dt.drop(columns=['DATE_C'], inplace=True)
            data_dt_borough = data_dt[data_dt['BOROUGH'].isin(option_b)]
            st.dataframe(data_dt_borough)
            data_filtered = data_dt_borough
        elif option_c != [] and option_b == []:
            st.write('__Data Display:__')
            data_dt = data[(data['TIME'] >= start_time_str) & (data['TIME'] <= end_time_str)]
            data_dt.sort_values(['DATE_C', 'TIME'], ascending=[True, True], inplace=True)
            data_dt.drop(columns=['DATE_C'], inplace=True)
            st.dataframe(data_dt[option_c])
            data_filtered = data_dt
        else:
            st.write('__Data Display:__')
            data_dt = data[(data['TIME'] >= start_time_str) & (data['TIME'] <= end_time_str)]
            data_dt.sort_values(['DATE_C', 'TIME'], ascending=[True, True], inplace=True)
            data_dt.drop(columns=['DATE_C'], inplace=True)
            data_dt_borough = data_dt[data_dt['BOROUGH'].isin(option_b)]
            st.dataframe(data_dt_borough[option_c])
            data_filtered = data_dt_borough
    elif option_t == 'Date+Time (e.g., 07/29/2015 8:03:00 PM)':
        if option_c == [] and option_b == []:
            st.write('__Data Display:__')
            data_dt = data[(data['DATE_C'] >= date_format(start_date_str)) & (data['DATE_C'] <= date_format(end_date_str)) &
                           (data['TIME'] >= start_time_str) & (data['TIME'] <= end_time_str)]
            data_dt.sort_values(['DATE_C', 'TIME'], ascending=[True, True], inplace=True)
            data_dt.drop(columns=['DATE_C'], inplace=True)
            st.dataframe(data_dt)
            data_filtered = data_dt
        elif option_c == [] and option_b != []:
            st.write('__Data Display:__')
            data_dt = data[(data['DATE_C'] >= date_format(start_date_str)) & (data['DATE_C'] <= date_format(end_date_str)) &
                           (data['TIME'] >= start_time_str) & (data['TIME'] <= end_time_str)]
            data_dt.sort_values(['DATE_C', 'TIME'], ascending=[True, True], inplace=True)
            data_dt.drop(columns=['DATE_C'], inplace=True)
            data_dt_borough = data_dt[data_dt['BOROUGH'].isin(option_b)]
            st.dataframe(data_dt_borough)
            data_filtered = data_dt_borough
        elif option_c != [] and option_b == []:
            st.write('__Data Display:__')
            data_dt = data[(data['DATE_C'] >= date_format(start_date_str)) & (data['DATE_C'] <= date_format(end_date_str)) &
                           (data['TIME'] >= start_time_str) & (data['TIME'] <= end_time_str)]
            data_dt.sort_values(['DATE_C', 'TIME'], ascending=[True, True], inplace=True)
            data_dt.drop(columns=['DATE_C'], inplace=True)
            st.dataframe(data_dt[option_c])
            data_filtered = data_dt
        else:
            st.write('__Data Display:__')
            data_dt = data[(data['DATE_C'] >= date_format(start_date_str)) & (data['DATE_C'] <= date_format(end_date_str)) &
                           (data['TIME'] >= start_time_str) & (data['TIME'] <= end_time_str)]
            data_dt.sort_values(['DATE_C', 'TIME'], ascending=[True, True], inplace=True)
            data_dt.drop(columns=['DATE_C'], inplace=True)
            data_dt_borough = data_dt[data_dt['BOROUGH'].isin(option_b)]
            st.dataframe(data_dt_borough[option_c])
            data_filtered = data_dt_borough
    return data_filtered


# geographic map showing all data points
def showing_map(data_t):
    data_t = data_t[data_t['LONGITUDE'].notna()]
    columns_keep = ['LATITUDE', 'LONGITUDE']
    data_t = data_t[columns_keep]
    view_state_lat = data_t['LATITUDE'].mean()
    view_state_lon = data_t['LONGITUDE'].mean()
    view_state = pdk.ViewState(
        latitude=view_state_lat,
        longitude=view_state_lon,
        zoom=10,
        pitch=0)

    layer = pdk.Layer(
        'ScatterplotLayer',
        data=data_t,
        get_position=['LONGITUDE', 'LATITUDE'],
        get_radius=80,
        filled=True,
        get_fill_color=[255, 140, 0])

    r = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9', layers=[layer], initial_view_state=view_state)
    st.write('__Geographic Map:__')
    st.pydeck_chart(r)
    st.write('----------------------------')


#display different chart
# 1. line chart:date/time/date+time (collisions vs date/time)
def linechart(option_t, data_filtered):
    if option_t == 'Only Date (e.g., 07/29/2015)':
        data_filtered['DATE'] = pd.to_datetime(data_filtered['DATE']) # covert the column DATE into a real date
        data_filtered['Amount of Collisions'] = 1
        date_count = data_filtered.groupby(['DATE', 'BOROUGH'])['Amount of Collisions'].sum().reset_index()

        line_chart = alt.Chart(date_count).mark_line(point=True).encode(
            x=alt.X('DATE', timeUnit='yearmonthdate', title='DATE'),
            y='Amount of Collisions',
            color='BOROUGH',
            tooltip=[alt.Tooltip('DATE', timeUnit='yearmonthdate'),
            alt.Tooltip('BOROUGH'),
            alt.Tooltip('Amount of Collisions')]).properties(
            title='Amount of Collisions VS Date'
            ).configure_title(offset=5, fontSize=20, orient='top', anchor='middle')
        st.altair_chart(line_chart, use_container_width=True)
    elif option_t == 'Only Time (e.g., 8:03:00 PM)':
        data_filtered['TIME'] = pd.to_datetime(data_filtered['TIME'])
        data_filtered['Amount of Collisions'] = 1
        time_count = data_filtered.groupby(['TIME', 'BOROUGH'])['Amount of Collisions'].sum().reset_index()

        line_chart = alt.Chart(time_count).mark_line(point=True).encode(
            x=alt.X('TIME', timeUnit='hoursminutes', title='TIME'),
            y='Amount of Collisions',
            color='BOROUGH',
            tooltip=[alt.Tooltip('TIME', timeUnit='hoursminutes'),
            alt.Tooltip('BOROUGH'),
            alt.Tooltip('Amount of Collisions')]).properties(
            title='Amount of Collisions VS Time'
            ).configure_title(offset=5, fontSize=20, orient='top', anchor='middle')
        st.altair_chart(line_chart, use_container_width=True)
    elif option_t == 'Date+Time (e.g., 07/29/2015 8:03:00 PM)':
        data_filtered['DATE TIME'] = pd.to_datetime(data_filtered['DATE'] + ' ' + data_filtered['TIME'])
        data_filtered['Amount of Collisions'] = 1
        date_time_count = data_filtered.groupby(['DATE TIME', 'BOROUGH'])['Amount of Collisions'].sum().reset_index()

        line_chart = alt.Chart(date_time_count).mark_line(point=True).encode(
            x=alt.X('DATE TIME', timeUnit="yearmonthdatehoursminutes",
                    title='DATE TIME', axis=alt.Axis(labelAngle=-45)),
            y='Amount of Collisions',
            color='BOROUGH',
            tooltip=[alt.Tooltip('DATE TIME', title='DATE'),
            alt.Tooltip('DATE TIME', timeUnit='hoursminutes', title='TIME'),
            alt.Tooltip('BOROUGH'),
            alt.Tooltip('Amount of Collisions')]).properties(
            title='Amount of Collisions VS Date Time'
            ).configure_title(offset=5, fontSize=20, orient='top', anchor='middle')
        st.altair_chart(line_chart, use_container_width=True)
        st.write('----------------------------')
    elif option_t == '<select>':
        pass

# 2. group bar chart:date/date+time (collisions vs day of week)
def barchart(option_t, data_filtered):
    if option_t == 'Only Date (e.g., 07/29/2015)' or option_t == 'Date+Time (e.g., 07/29/2015 8:03:00 PM)':
        # calculate each date into it's corresponding day of week and add a column into the original data
        data_filtered['DAY_OF_WEEK'] = pd.to_datetime(data_filtered['DATE']).dt.dayofweek # Monday=0, Sunday=6
        data_filtered_reset = data_filtered.reset_index()

        day_of_week_lst = []
        # convert 0 to Monday, 6 to Sunday, etc.
        for day_of_week in data_filtered_reset['DAY_OF_WEEK']:
            if day_of_week == 0:
                day_of_week_lst.append('Monday')
            elif day_of_week == 1:
                day_of_week_lst.append('Tuesday')
            elif day_of_week == 2:
                day_of_week_lst.append('Wednesday')
            elif day_of_week == 3:
                day_of_week_lst.append('Thursday')
            elif day_of_week == 4:
                day_of_week_lst.append('Friday')
            elif day_of_week == 5:
                day_of_week_lst.append('Saturday')
            elif day_of_week == 6:
                day_of_week_lst.append('Sunday')
        data_filtered_reset['DAY_OF_WEEK'] = pd.Series(day_of_week_lst)
        data_filtered_reset['Amount of Collisions'] = 1
        day_of_week_count = data_filtered_reset.groupby(['DAY_OF_WEEK','BOROUGH'])['Amount of Collisions'].sum().reset_index()

        bar_chart = alt.Chart(day_of_week_count).mark_bar(size=13).encode(
            x=alt.X('BOROUGH', axis=None),
            y='Amount of Collisions',
            color='BOROUGH',
            column=alt.Column('DAY_OF_WEEK', sort=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
                              header=alt.Header(titleOrient='bottom')),
            tooltip=[alt.Tooltip('DAY_OF_WEEK'),
            alt.Tooltip('BOROUGH'),
            alt.Tooltip('Amount of Collisions')]
            ).properties(width=67, title='Amount of Collisions VS Day of Week').configure_title(offset=5, fontSize=20,
                                                                                                orient='top', anchor='middle')
        st.altair_chart(bar_chart, use_container_width=False)
        st.write('----------------------------')

    elif option_t == '<select>' or option_t == 'Only Time (e.g., 8:03:00 PM)':
        pass


# 3. line chart:date+time (the difference between weekdays and weekends)
def linechart_cor(option_t, data_filtered):
    if option_t == 'Date+Time (e.g., 07/29/2015 8:03:00 PM)':
        data_filtered['TIME'] = pd.to_datetime(data_filtered['TIME']) # covert the column TIME into a real date
        data_filtered['DAY_OF_WEEK'] = pd.to_datetime(data_filtered['DATE']).dt.dayofweek # Monday=0, Sunday=6
        data_filtered['Amount of Collisions'] = 1
        data_filtered_reset = data_filtered.reset_index()
        day_of_week_lst = []
        # convert 0 to Monday, 6 to Sunday, etc.
        for day_of_week in data_filtered_reset['DAY_OF_WEEK']:
            if day_of_week == 0:
                day_of_week_lst.append('Monday')
            elif day_of_week == 1:
                day_of_week_lst.append('Tuesday')
            elif day_of_week == 2:
                day_of_week_lst.append('Wednesday')
            elif day_of_week == 3:
                day_of_week_lst.append('Thursday')
            elif day_of_week == 4:
                day_of_week_lst.append('Friday')
            elif day_of_week == 5:
                day_of_week_lst.append('Saturday')
            elif day_of_week == 6:
                day_of_week_lst.append('Sunday')
        data_filtered_reset['DAY_OF_WEEK'] = pd.Series(day_of_week_lst)
        day_of_week_count = data_filtered_reset.groupby(['TIME', 'DAY_OF_WEEK'])['Amount of Collisions'].sum().reset_index()

        line_chart = alt.Chart(day_of_week_count).mark_line(point=True).encode(
            x=alt.X('TIME', timeUnit='hoursminutes', title='Time'),
            y='Amount of Collisions',
            color=alt.Color('DAY_OF_WEEK', sort=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']),
            tooltip=[alt.Tooltip('TIME', timeUnit='hoursminutes'),
            alt.Tooltip('DAY_OF_WEEK'),
            alt.Tooltip('Amount of Collisions')]).properties(
            title='Difference between Weekdays and Weekend'
            ).configure_title(offset=5, fontSize=20, orient='top', anchor='middle')
        st.altair_chart(line_chart, use_container_width=True)
        st.write('----------------------------')
    else:
        pass


# 4. top 10 dangerous street based on date/time selection
def table(option_t, data_filtered):
    if option_t == '<select>':
        pass
    else:
        data_filtered['Amount of Collisions'] = 1
        data_filtered_reset = data_filtered.reset_index()
        street_count = data_filtered_reset.groupby('ON STREET NAME')['Amount of Collisions'].sum().reset_index()

        street_count.sort_values(by=['Amount of Collisions'], ascending=False, inplace = True)
        street_count_reset = street_count.reset_index()
        street_count_reset.drop(columns=['index'], inplace=True)
        street_count_top10 = street_count_reset.loc[0:9]
        street_count_top10.index = ['Top 1', 'Top 2', 'Top 3', 'Top 4', 'Top 5', 'Top 6', 'Top 7', 'Top 8', 'Top 9', 'Top 10']
        table_title = '<p style="text-align:center"; color:Black; ' \
                  'font-size: 23px;"><strong>The 10 most dangerous streets of New York</strong></p>'
        st.markdown(table_title, unsafe_allow_html=True)
        st.table(street_count_top10)



# main function
def main():
    start_date_str, end_date_str, start_time_str, end_time_str = show_option_dt(option_t)
    option_b = borough_select()
    option_c = column_select()
    button = set_button()
    if start_date_str == end_date_str == '01/01/2014':
        pass
    else:
        data_filtered = show_option_dataframe(option_t, option_b, option_c,
                                          start_date_str, end_date_str, start_time_str, end_time_str)
        data_t = data_filtered
        st.write('----------------------------')
        showing_map(data_t)
        if button == True:
            st.write('__Analysis Chart(s):__')
            linechart(option_t, data_filtered)
            barchart(option_t, data_filtered)
            linechart_cor(option_t, data_filtered)
            table(option_t, data_filtered)



main()





