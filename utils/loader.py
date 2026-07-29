import os
import pandas as pd

DATA_FOLDER = "data"


def load_stock_master():

    file = os.path.join(
        DATA_FOLDER,
        "2026_Stock_Master.xlsx"
    )

    if not os.path.exists(file):
        return pd.DataFrame()

    df = pd.read_excel(
        file,
        sheet_name="Stock_Master",
        engine="openpyxl"
    )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    return df


def load_consumption_master():

    file = os.path.join(
        DATA_FOLDER,
        "2026_Consumption_Master1.xlsx"
    )

    if not os.path.exists(file):
        return pd.DataFrame()

    df = pd.read_excel(
        file,
        sheet_name="Consumption_Master",
        engine="openpyxl"
    )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month_name()
    df["Week"] = df["Date"].dt.isocalendar().week

    return df


def load_po_tracker():

    file = os.path.join(
        DATA_FOLDER,
        "2026_PO_Tracker.xlsx"
    )

    if not os.path.exists(file):
        return pd.DataFrame()

    return pd.read_excel(
        file,
        sheet_name="PO_Tracker",
        engine="openpyxl"
    )


def load_chemical_master():

    file = os.path.join(
        DATA_FOLDER,
        "Chemical_Master.xlsx"
    )

    if not os.path.exists(file):
        return pd.DataFrame()

    return pd.read_excel(
        file,
        sheet_name="Chemical_Master",
        engine="openpyxl"
    )


def stock_health(df):

    def get_status(days):

        if days >= 90:
            return "Healthy"

        elif days >= 30:
            return "Warning"

        return "Critical"

    df["Status"] = (
        df["Available Days"]
        .fillna(0)
        .apply(get_status)
    )

    return df
