import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from fetch_logs import fetch_log_data, fetch_log_list


def get_data(userToken: str):
    if not userToken:
        return None
    logList = fetch_log_list(userToken)
    df = fetch_log_data(logList)
    return df


# fetch data
userToken = st.sidebar.text_input("arcDPS userToken:", "")
if not userToken:
    st.stop()
df_original = get_data(userToken)
df = df_original

# create inputs
stats = list(df)
removed_stats = ['id', 'permalink', 'uploadTime', 'encounterTime', 'timeStart', 'name', 'group',
                 'timeEnd', 'duration', 'account', 'hasCommanderTag', 'profession', 'healing']
stat_selector = st.sidebar.selectbox(
    "Select Stats", [stat for stat in stats if stat not in removed_stats])
group_by = st.sidebar.selectbox("Group by:", ['name', 'account', 'profession'])

account_names = st.sidebar.multiselect(
    "Filter Account Names:", df.account.unique())
character_names = st.sidebar.multiselect(
    "Filter Character Names:", df.name.unique())
professions = st.sidebar.multiselect(
    "Filter Professions:", df.profession.unique())

# apply filters
if character_names:
    df = df[df['name'].isin(character_names)]
if account_names:
    df = df[df['account'].isin(account_names)]
if professions:
    df = df[df['profession'].isin(professions)]

if st.checkbox("Show raw data"):
    f"df (filtered) {df.shape}:", df

if st.checkbox("Show averaged data"):
    mean = df.groupby(group_by).mean()
    f"df (filtered) {mean.shape}:", mean

# compute rolling average
rolling_average_window = st.sidebar.slider(
    "Rolling Avgerage Window Size:", 1, 25)
df["result"] = df.groupby(group_by)[stat_selector].rolling(
    rolling_average_window).mean().reset_index(0, drop=True)

# box plots
fig = go.Figure()
for k, v in df.groupby(group_by):
    fig.add_trace(go.Box(y=v[stat_selector], name=k,
                  boxpoints="all", jitter=1, pointpos=0))
st.write(fig)

# rollin average line charts
fig = px.line(df, x="timeStart", y="result",
              color=group_by, title=stat_selector)
fig.update_traces(mode='markers+lines')
fig.layout = dict(xaxis=dict(
    type="category", categoryorder='category ascending'))
st.write(fig)
