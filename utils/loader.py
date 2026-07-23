import pandas as pd

consumption_file = "chemical_consumption.xlsx"
stock_file = "chemical_stock.xlsx"


def load_consumption():
    return pd.read_excel(
        consumption_file,
        sheet_name=None,
        engine="openpyxl"
    )


def load_stock():
    return pd.read_excel(
        stock_file,
        sheet_name=None,
        engine="openpyxl"
    )


def get_latest_stock():

    sheets = load_stock()

    latest_sheet = None
    latest_df = None

    for sheet_name, df in reversed(list(sheets.items())):

        df = df.dropna(how="all")

        if not df.empty:
            latest_sheet = sheet_name
            latest_df = df
            break

    return latest_sheet, latest_df
