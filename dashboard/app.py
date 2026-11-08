import os

import folium
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from streamlit_folium import st_folium

load_dotenv(".env")

st.set_page_config(page_title="BRI - Baltic Resilience Intelligence", layout="wide")
st.title("Baltic Resilience Intelligence")
st.markdown("**Work Package 5 MVP** - Public Event Intelligence")


@st.cache_resource
def get_engine():
    user = os.getenv("POSTGRES_USER", "bri")
    pw = os.getenv("POSTGRES_PASSWORD", "change_me")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "bri")
    return create_engine(f"postgresql+psycopg://{user}:{pw}@{host}:{port}/{db}")


def load_data():
    engine = get_engine()
    query = """
        SELECT 
            e.event_id,
            e.country_code,
            r.region_name,
            e.event_type,
            e.reported_cause,
            e.occurred_at,
            e.event_status,
            e.verification_status,
            ST_Y(ST_Centroid(r.geom)) AS lat,
            ST_X(ST_Centroid(r.geom)) AS lon
        FROM events e
        LEFT JOIN regions r ON e.region_code = r.region_code
        ORDER BY e.occurred_at DESC;
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df


df = load_data()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Recent Public Reports")
    if df.empty:
        st.info("No events currently in the database.")
    else:
        st.dataframe(df.drop(columns=["lat", "lon"]), width="stretch", hide_index=True)

with col2:
    st.subheader("Geographic Distribution")
    m = folium.Map(location=[57.0, 25.0], zoom_start=6, tiles="OpenStreetMap")

    if not df.empty:
        for _, row in df.iterrows():
            if pd.notnull(row["lat"]) and pd.notnull(row["lon"]):
                popup_text = f"""
                <b>{row["country_code"]}</b><br>
                {row["event_type"]}<br>
                Cause: {row["reported_cause"]}<br>
                Status: {row["event_status"]}
                """
                folium.Marker(
                    location=[row["lat"], row["lon"]],
                    popup=folium.Popup(popup_text, max_width=250),
                    icon=folium.Icon(color="red", icon="info-sign"),
                ).add_to(m)

    st_folium(m, width=800, height=500, returned_objects=[])

st.markdown("---")
st.caption(
    "Data provenance: Cloudflare Radar. This platform does not publish precise critical-infrastructure locations."
)
