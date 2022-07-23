import pandas as pd
import streamlit as st


def explode_apply(df: pd.DataFrame, column: str):
    return pd.concat([df.drop(columns=[column]), df.explode(
        column)[column].apply(pd.Series)], axis=1)


@st.cache()
def transform_data(logData: dict) -> pd.DataFrame:
    df = pd.DataFrame(logData).transpose()

    # expand metadata and data columns
    metadata = df['metaData'].apply(pd.Series)
    data = df['data'].apply(pd.Series)
    df = metadata.join(data)

    # create a separate row for each player of a fight
    players = df.explode('players')['players'].apply(pd.Series)
    # and join to original dataFrame
    df = df.drop(columns=['players'])
    df = df.join(players)

    # XXX need to look at this again
    df = df.drop(columns=['squadBuffsActive'], axis=1)

    # create a separate row for each stat
    for column in ['dpsAll', 'support', 'statsAll']:
        df = explode_apply(df, column)

    # Fix datetime columns
    df['timeStart'] = pd.to_datetime(df['timeStart'])
    df['timeEnd'] = pd.to_datetime(df['timeEnd'])
    df = df.sort_values('timeStart').reset_index(drop=True)
    return df
