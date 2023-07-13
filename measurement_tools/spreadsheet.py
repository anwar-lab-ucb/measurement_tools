import os

import pandas as pd


def add_to_spreadsheet(fname, df, **kwargs):
    """
    Note that the kwargs are passed to both
    the read and write fn of the spreadsheet.
    Useful for e.g. sheet_name.

    Creates a spreadsheet if one does not exist.

    Replaces columns if they already exist.
    """
    if os.path.exists(fname):
        old_df = read_spreadsheet(fname, **kwargs)
        duplicate_columns = set(old_df.columns).intersection(df.columns)
        df = old_df.join(df, how='outer', lsuffix='_todelete')
        if len(duplicate_columns) > 0:
            df = df.drop(columns=[f'{c}_todelete' for c in duplicate_columns])
    write_spreadsheet(fname, df, **kwargs)


def read_spreadsheet(fname, **kwargs):
    extension = os.path.splitext(fname)[1]
    fn = pd.read_csv if extension == ".csv" else pd.read_excel
    return fn(fname, **kwargs)


def write_spreadsheet(fname, df, **kwargs):
    """
    Overwrites!
    """
    extension = os.path.splitext(fname)[1]
    fn = df.to_csv if extension == ".csv" else df.to_excel
    fn(fname, index=False)
