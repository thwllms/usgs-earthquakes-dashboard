import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import numpy as np
import pydeck as pdk

from datetime import datetime, timedelta




USGS_API_URL = 'https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime={}&endtime={}'


def get_url(start_date: datetime, end_date: datetime) -> str:
    return USGS_API_URL.format(start_date.strftime('%Y-%m-%d'),
                               end_date.strftime('%Y-%m-%d'))


@st.cache
def load_data(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    url = get_url(start_date, end_date)
    print(url)
    data = pd.read_csv(url, parse_dates=['time', 'updated'], infer_datetime_format=True)
    return data


def histogram(df: pd.DataFrame):
    fig = ff.create_distplot([df['mag'].values], group_labels=['magnitude'],
                             bin_size=[0.5])
    return fig


def pydeck_map(data, lat, lon, zoom):
    data_filtered = data[['latitude', 'longitude', 'mag']]
    st.pydeck_chart(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={
                "latitude": lat,
                "longitude": lon,
                "zoom": zoom,
                "pitch": 50,
            },
            layers=[
                pdk.Layer(
                    "HexagonLayer",
                    data=data_filtered,
                    get_position=["longitude", "latitude"],
                    auto_highlight=True,
                    radius=100000,
                    elevation_scale=4,
                    elevation_range=[0, 500000],
                    pickable=True,
                    extruded=True,
                ),
            ],
        )
    )


def streamlit_layout():
    st.title('USGS Earthquakes')

    start_date = st.date_input(
        "Start date",
        datetime.now() - timedelta(days=1))
    st.write('Selected start date:', start_date)

    end_date = st.date_input(
        "End date",
        datetime.now())
    st.write('Selected end date:', end_date)

    st.subheader('Raw data')
    df = load_data(start_date, end_date)
    st.write(df)
    st.subheader('Map')
    st.map(df)
    st.subheader('Histogram')
    fig = histogram(df)
    st.plotly_chart(fig, use_container_width=True)

    pydeck_map(df, 0, 0, 0)


if __name__ == '__main__':
    streamlit_layout()
