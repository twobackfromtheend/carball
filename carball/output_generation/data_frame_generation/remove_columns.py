import pandas as pd

COLUMNS_TO_REMOVE = [
    'boost_temp',
    'potential_boost_collect'
]


def remove_columns(df: pd.DataFrame):
    for column in df.columns:
        if column[1] in COLUMNS_TO_REMOVE:
            df.drop(columns=column, inplace=True)
