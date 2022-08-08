import plotly.express as px
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

# plot
fig = px.line(df, x="timeStart", y="result",
              color=group_by, title=stat_selector)
fig.update_traces(mode='markers+lines')
fig.layout = dict(xaxis=dict(
    type="category", categoryorder='category ascending'))
st.plotly_chart(fig)

# XXX: other Rolling version
# fig = px.scatter(df, x="timeStart", y=stat_selector, color=group_by,
#                  title=f"{stat_selector} (avg of {rolling_average_window})", trendline="rolling", trendline_options=dict(window=rolling_average_window))
# # fig.update_traces(mode='markers+lines')
# fig.data = [t for t in fig.data if t.mode == "lines"]
# # trendlines have showlegend=False by default
# fig.update_traces(showlegend=True)
# fig.layout = dict(xaxis=dict(
#     type="category", categoryorder='category ascending'))
# st.plotly_chart(fig)


# @TODO: altair alternative
# fig = alt.Chart(df).mark_line().encode(x="timeStart", y="dps", color="name")
# st.altair_chart(fig)
