import streamlit as st
import pandas as pd


def transform_data(logData: dict) -> pd.DataFrame:
    print('------------------------')
    df = pd.DataFrame(logData).transpose()

    # expand metadata and data columns
    metadata = df['metaData'].apply(pd.Series)
    data = df['data'].apply(pd.Series)
    df = metadata.join(data)

    # create a separate row for each player of a fight
    df = df.explode('players')
    # expand player columns
    players = df['players'].apply(pd.Series)
    st.write(players.shape)
    df = df.drop(columns=['players'])
    st.write(df.shape)
    df = df.join(players)  # XXX join at id -> dont create new entries
    st.write(df.shape)
    return df

    # 'support' is actually a list with 1 element in it
    df = df.explode('support')
    # expand support columns
    support = df['support'].apply(pd.Series)
    df = df.drop(columns=['support'])
    df = df.join(support)

    # return
    df = df.drop(columns=['squadBuffsActive'])
    df = df.drop(columns=['dpsAll'])
    df = df.drop(columns=['statsAll'])
    return df
