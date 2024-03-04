import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fetch_logs import fetch_log_list, fetch_logs
from process_logs import _RENAME_KEYS

# These are keys that someone might be intetested in, but which just clutter the
# application most of the time.
_HIDE_KEYS = [
    _RENAME_KEYS["condiDps"],  # --> 'dps' should be enough
    _RENAME_KEYS["powerDps"],  # --> 'dps' should be enough
    _RENAME_KEYS["resurrects"],  # --> unclear what it means
    _RENAME_KEYS["resurrectTime"],  # --> unclear what it means
    _RENAME_KEYS["condiCleanseSelf"],  # --> not interesting in group fights
    _RENAME_KEYS["wasted"],  # --> unclear what it means
    _RENAME_KEYS["timeWasted"],  # --> unclear what it means
    _RENAME_KEYS["saved"],  # --> unclear what it means
    _RENAME_KEYS["timeSaved"],  # --> unclear what it means
    _RENAME_KEYS["avgActiveBoons"],  # --> 'avgBoons' should be enough
    _RENAME_KEYS["avgActiveConditions"],  # --> 'avgConditions' should be enough
    _RENAME_KEYS["skillCastUptimeNoAA"],  # --> 'skillCastUptime' should be enough
    _RENAME_KEYS["totalDamageCount"],  # --> 'dps' should be enough
    # _RENAME_KEYS["criticalRate"], # --> might be hidden when boon / fury uptime is added
    _RENAME_KEYS["flankingRate"],  # --> very niche
]

_UNSELECTABLE_KEYS = [
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


def fetch_data(userToken: str):
    log_list = [fetch_log_list(userToken)[0]]
    st.write(log_list)
    df = fetch_logs(log_list)
    return df


# parse userTokens from env
user_tokens = {"Custom": ""}
if "DPS_REPORT_TOKENS" in os.environ:
    for token in os.environ["DPS_REPORT_TOKENS"].split(","):
        name, value = token.split(":")
        user_tokens |= {name: value.strip()}


# fetch data
token_help = """
# PROTECT YOUR USER TOKEN! Treat it like a password.
Anyone with access to this value can look up any logs uploaded with it.

If you select 'Custom', you will be able to use your own userToken.
If other values can be selected they were added by the person hosting this application.
Talk to them if you want to know their values.

ArcDps logs that were uploaded with the selected userToken will be displayed here.
In order to upload logs with the correct userToken you can use the [PlenBotLogUploader](https://plenbot.net/uploader/) (recommended)
or the [Arcdps-Uploader Extension](https://github.com/nbarrios/arcdps-uploader) (less well maintained).

See the relevant documentation [here](https://dps.report/api).
"""


url_params = st.experimental_get_query_params()

# User Token
user_token = None
user_token_name_default = (
    list(user_tokens).index(url_params["userTokenName"][0])
    if "userTokenName" in url_params
    else 0
)
user_token_name = st.sidebar.selectbox(
    "dps.report userToken:",
    options=user_tokens.keys(),
    index=user_token_name_default,
    help=token_help,
)
if user_token_name == "Custom":
    user_token = st.sidebar.text_input("custom token", label_visibility="collapsed")
else:
    user_token = user_tokens[user_token_name]
if not user_token:
    st.stop()
df = fetch_data(user_token)

# Metric
metrics = list(df)
hidden_metrics = _UNSELECTABLE_KEYS
hide_obscure_metrics_help = """
Most values reported by ArcDps are either useless or it is unclear what they
mean. Deselect this checkbox if you want to browse through them anyway.
"""
hide_obscure_metrics_default = (
    url_params["hide_obscure_metrics"][0] == "True"
    if "hide_obscure_metrics" in url_params
    else True
)
hide_obscure_metrics = st.sidebar.checkbox(
    "Hide obscure metrics",
    value=hide_obscure_metrics_default,
    help=hide_obscure_metrics_help,
)
if hide_obscure_metrics:
    hidden_metrics += _HIDE_KEYS

metrics = [metric for metric in metrics if metric not in hidden_metrics]
metric_default = (
    metrics.index(url_params["metric"][0])
    if "metric" in url_params and url_params["metric"][0] in metrics
    else 0
)
metric = st.sidebar.selectbox(
    "Select Metric",
    options=metrics,
    index=metric_default,
    help="Choose the data that you are interested in.",
)

# GroupBy
group_by_options = ["character name", "character name & profession", "profession"]
group_by_selection_default = (
    group_by_options.index(url_params["group_by_selection"][0])
    if "group_by_selection" in url_params
    else 0
)
group_by_selection = st.sidebar.selectbox(
    "Group by:",
    options=group_by_options,
    index=group_by_options.index(url_params["group_by_selection"][0])
    if "group_by_selection" in url_params
    else 0,
)
group_by = "profession+name"
if group_by_selection == "character name":
    group_by = "name"
elif group_by_selection == "profession":
    group_by = "profession"

account_name_filter = st.sidebar.multiselect(
    "Filter Account Names:",
    options=sorted(df.account.unique()),
    default=url_params["account_name_filter"]
    if "account_name_filter" in url_params
    else None,
)
if account_name_filter:
    df = df[df["account"].isin(account_name_filter)]
character_name_filter = st.sidebar.multiselect(
    "Filter Character Names:",
    options=sorted(df.name.unique()),
    default=url_params["character_name_filter"]
    if "character_name_filter" in url_params
    else None,
)
if character_name_filter:
    df = df[df["name"].isin(character_name_filter)]
profession_filter = st.sidebar.multiselect(
    "Filter Professions:",
    options=sorted(df.profession.unique()),
    default=url_params["profession_filter"]
    if "profession_filter" in url_params
    else None,
)
if profession_filter:
    df = df[df["profession"].isin(profession_filter)]

# Filter By Time
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
df = df[df["timeStart"].between(start_time_min, start_time_max)]

st.experimental_set_query_params(
    userTokenName=user_token_name,
    hide_obscure_metrics=hide_obscure_metrics,
    metric=metric,
    group_by_selection=group_by_selection,
    account_name_filter=account_name_filter,
    character_name_filter=character_name_filter,
    profession_filter=profession_filter,
    # start_time_min=start_time_min,
    # start_time_max=start_time_max,
)

format = "%d.%m.%y %H:%M"
time_range_string = (
    "("
    + pd.Timestamp(start_time_min).strftime(format)
    + " - "
    + pd.Timestamp(start_time_max).strftime(format)
    + ")"
)


if st.checkbox("Show raw data"):
    f"df (filtered) {df.shape}:", df


groups = df.groupby(group_by)
mean = groups.mean(numeric_only=True)
if st.checkbox("Show averaged data"):
    f"df (filtered) {mean.shape}:", mean


# violoin plot
fig = go.Figure()
sorted_keys = mean[metric].sort_values()
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
            y=groups.get_group(group)[metric],
        )
    )
fig.update_layout(
    title=f"{metric}  {time_range_string}",
    title_x=0.5,
    legend_traceorder="reversed",
)
st.write(fig)

# rolling average
rolling_average_help = """
The plot below shows how the selected metric has changed over time.
This slider causes the data to be averaged over N fights instead of
displaying each data point individually. Choose higher values for
metrics that vary wildly from fight to fight.
"""
rolling_average_window = st.slider(
    "Rolling Avgerage Window Size:", 1, 25, 5, help=rolling_average_help
)
df["rolling_average"] = (
    df.groupby(group_by)[metric]
    .rolling(rolling_average_window, win_type="triang")
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
fig.update_layout(title=metric, title_x=0.5, legend_traceorder="reversed")
fig.layout = {"xaxis": {"type": "category", "categoryorder": "category ascending"}}
st.write(fig)
