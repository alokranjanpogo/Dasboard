import pandas as pd

consumption_file="data/chemical_consumption.xlsx"
stock_file="data/chemical_stock.xlsx"


def load_consumption():

    sheets=pd.read_excel(
        consumption_file,
        sheet_name=None,
        engine="openpyxl"
    )

    return sheets


def load_stock():

    sheets=pd.read_excel(
        stock_file,
        sheet_name=None,
        engine="openpyxl"
    )

    return sheets


def get_sheet_names():

    consumption=load_consumption()

    stock=load_stock()

    return list(consumption.keys()),list(stock.keys())
