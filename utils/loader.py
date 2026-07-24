import glob
import pandas as pd


def build_master_stock():

    files = glob.glob("data/*.xlsx")

    if not files:
        return pd.DataFrame()

    master = []

    for file in files:

        xl = pd.ExcelFile(file)

        # Read first sheet automatically
        first_sheet = xl.sheet_names[0]

        df = pd.read_excel(
            file,
            sheet_name=first_sheet,
            engine="openpyxl"
        )

        master.append(df)

    master = pd.concat(
        master,
        ignore_index=True
    )

    return master


def calculate_consumption():

    df = build_master_stock()

    if df.empty:
        return df

    df["Date"] = pd.to_datetime(df["Date"])

    df = df.sort_values(
        ["Chemical", "Date"]
    )

    df["Consumption"] = (
        df.groupby("Chemical")
        ["Available Stock"]
        .shift(1)
        - df["Available Stock"]
    )

    df["Consumption"] = (
        df["Consumption"]
        .fillna(0)
        .clip(lower=0)
    )

    return df


def stock_health(df):

    df = df.copy()

    def status(days):

        if days >= 90:
            return "Healthy"

        elif days >= 30:
            return "Warning"

        return "Critical"

    df["Status"] = df["Available Days"].apply(
        status
    )

    return df
