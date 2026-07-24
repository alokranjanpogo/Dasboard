import glob
import pandas as pd


def build_master_stock():

    files = glob.glob("data/*normalized*.xlsx")

    if not files:
        return pd.DataFrame()

    master = []

    for file in files:

        df = pd.read_excel(
            file,
            sheet_name="Master_Data",
            engine="openpyxl"
        )

        master.append(df)

    master = pd.concat(
        master,
        ignore_index=True
    )

    master["Date"] = pd.to_datetime(
        master["Date"]
    )

    return master


def calculate_consumption():

    df = build_master_stock()

    if df.empty:
        return df

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

    df["Status"] = df[
        "Available Days"
    ].apply(status)

    return df
