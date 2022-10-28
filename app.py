import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fetch_logs import fetch_log_list, fetch_logs


def fetch_data(userToken: str):
    logList = fetch_log_list(userToken)
    df = fetch_logs(logList)
    return df


# fetch data
userToken = st.sidebar.text_input("dps.report userToken:", "")
if not userToken:
    st.stop()
df = fetch_data(userToken)

# create inputs
stats = list(df)
unselectable_stats = [
    "id",
    "timeStart",
    "profession",
    "name",
    "profession+name",
    "group",
    "spec_color",
    "timeEnd",
    "duration",
    "account",
    "hasCommanderTag",
    "activeTimes",
]
stat_selector = st.sidebar.selectbox(
    "Select Stats", [stat for stat in stats if stat not in unselectable_stats]
)

group_by_selection = st.sidebar.selectbox(
    "Group by:", ["character name", "character name & profession", "profession"]
)
group_by = "profession+name"
if group_by_selection == "character name":
    group_by = "name"
elif group_by_selection == "profession":
    group_by = "profession"

account_name_filter = st.sidebar.multiselect(
    "Filter Account Names:", df.account.unique()
)
character_name_filter = st.sidebar.multiselect(
    "Filter Character Names:", df.name.unique()
)
profession_filter = st.sidebar.multiselect(
    "Filter Professions:", df.profession.unique()
)
dates = df["timeStart"].unique()
format = "%d.%m. %H:%M"
start_time_min = st.sidebar.select_slider(
    "First + Last Date:",
    format_func=lambda t: pd.Timestamp(t).strftime(format),
    options=dates,
    value=dates.min(),
)
start_time_max = st.sidebar.select_slider(
    "hidden",
    label_visibility="collapsed",
    format_func=lambda t: pd.Timestamp(t).strftime(format),
    options=dates,
    value=dates.max(),
)
if start_time_min > start_time_max:
    st.sidebar.error("First Date must be before Last Date")
    st.stop()

format = "%d.%m.%y %H:%M"
time_range_string = (
    "("
    + pd.Timestamp(start_time_min).strftime(format)
    + " - "
    + pd.Timestamp(start_time_max).strftime(format)
    + ")"
)


# apply filters
df = df[df["timeStart"].between(start_time_min, start_time_max)]
if character_name_filter:
    df = df[df["name"].isin(character_name_filter)]
if account_name_filter:
    df = df[df["account"].isin(account_name_filter)]
if profession_filter:
    df = df[df["profession"].isin(profession_filter)]

if st.checkbox("Show raw data"):
    f"df (filtered) {df.shape}:", df


groups = df.groupby(group_by)
mean = groups.mean()
if st.checkbox("Show averaged data"):
    f"df (filtered) {mean.shape}:", mean


# violoin plot
fig = go.Figure()
sorted_keys = mean[stat_selector].sort_values()
for group in sorted_keys.index:
    marker = {
        "color": groups.get_group(group)["spec_color"].value_counts().idxmax(),
    }
    fig.add_trace(
        go.Violin(
            jitter=1,
            marker=marker,
            meanline_visible=True,
            name=group,
            pointpos=0,
            points="all",
            spanmode="hard",
            y=groups.get_group(group)[stat_selector],
        )
    )
fig.update_layout(
    title=f"{stat_selector}  {time_range_string}",
    title_x=0.5,
    legend_traceorder="reversed",
)
st.write(fig)

# rolling average
rolling_average_window = st.slider("Rolling Avgerage Window Size:", 1, 25, 5)
df["rolling_average"] = (
    df.groupby(group_by)[stat_selector]
    .rolling(rolling_average_window)
    .mean()
    .reset_index(0, drop=True)
)
fig = go.Figure()
for group in sorted_keys.index:
    marker = {"color": groups.get_group(group)["spec_color"].value_counts().idxmax()}
    fig.add_trace(
        go.Scatter(
            marker=marker,
            mode="markers+lines",
            name=group,
            x=groups.get_group(group)["timeStart"],
            y=groups.get_group(group)["rolling_average"],
        )
    )
fig.update_layout(title=stat_selector, title_x=0.5, legend_traceorder="reversed")
fig.layout = {"xaxis": {"type": "category", "categoryorder": "category ascending"}}
st.write(fig)
