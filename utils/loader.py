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

    latest_sheet = list(sheets.keys())[-1]

    df = sheets[latest_sheet]

    df = df.dropna(how="all")

    return latest_sheet, df
