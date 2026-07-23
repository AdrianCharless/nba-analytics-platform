import streamlit as st
import pandas as pd
from databricks import sql
import plotly.express as px
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="NBA Analytics Dashboard", layout="wide")
st.title("🏀 NBA Team Performance Dashboard")
st.caption("2023-24 Regular Season | Home vs. Away Analysis")

@st.cache_data(ttl=600)
def load_data():
    connection = sql.connect(
        server_hostname=os.environ["DATABRICKS_HOST"].replace("https://", ""),
        http_path=os.environ["DATABRICKS_SQL_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
    )
    query = "SELECT * FROM nba_analytics.gold.team_home_away_performance"
    df = pd.read_sql(query, connection)
    connection.close()
    return df

df = load_data()

# Sidebar filter
teams = sorted(df["TEAM_NAME"].unique())
selected_team = st.sidebar.selectbox("Select a team (or view all)", ["All Teams"] + teams)

if selected_team != "All Teams":
    df_filtered = df[df["TEAM_NAME"] == selected_team]
else:
    df_filtered = df

# Top-level metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Teams", df["TEAM_NAME"].nunique())
with col2:
    st.metric("Total Games Tracked", int(df["GAMES_PLAYED"].sum()))
with col3:
    avg_home_win_pct = df[df["IS_HOME_GAME"] == True]["WIN_PCT"].mean()
    st.metric("League Avg Home Win %", f"{avg_home_win_pct:.1%}")

st.divider()

# Win % comparison chart
st.subheader("Win Percentage: Home vs. Away")
fig = px.bar(
    df_filtered,
    x="TEAM_NAME",
    y="WIN_PCT",
    color="IS_HOME_GAME",
    barmode="group",
    labels={"WIN_PCT": "Win %", "TEAM_NAME": "Team", "IS_HOME_GAME": "Home Game"},
    color_discrete_map={True: "#1f77b4", False: "#ff7f0e"},
)
st.plotly_chart(fig, use_container_width=True)

# Raw data table
st.subheader("Full Data")
st.dataframe(df_filtered, use_container_width=True)