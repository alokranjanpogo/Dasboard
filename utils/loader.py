# ==========================================================
# Chemical Dashboard - Data Loader
# ==========================================================

import pandas as pd
import re

stock_file = "chemical_stock.xlsx"


# ==========================================================
# Read Complete Workbook
# ==========================================================

def load_stock():
    return pd.read_excel(
        stock_file,
        sheet_name=None,
        header=1,
        engine="openpyxl"
    )


# ==========================================================
# Check whether sheet name is a date
# ==========================================================

def is_date_sheet(sheet):

    pattern = r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}"

    return bool(re.match(pattern, str(sheet)))


# ==========================================================
# Build Master DataFrame
# ==========================================================

def build_master_stock():

    workbook = load_stock()

    master = []

    for sheet_name, df in workbook.items():

        if not is_date_sheet(sheet_name):
            continue

        df = df.dropna(how="all")

        if df.empty:
            continue

        df = df.dropna(subset=[df.columns[0]])

        df = df.reset_index(drop=True)

        df.columns = [
            "Chemical",
            "Daily Requirement",
            "Monthly Requirement",
            "3 Month Requirement",
            "Available Stock",
            "Available Days",
            "Vendor"
        ]

        df = df[
            ~df["Chemical"].astype(str).str.contains(
                "Group",
                case=False,
                na=False
            )
        ]

        df = df[
            ~df["Chemical"].astype(str).str.contains(
                "Total",
                case=False,
                na=False
            )
        ]

        df["Date"] = pd.to_datetime(
            sheet_name,
            dayfirst=True,
            errors="coerce"
        )

        master.append(df)

    master = pd.concat(master, ignore_index=True)

    master["Year"] = master["Date"].dt.year

    master["Month"] = master["Date"].dt.month_name()

    master["Week"] = master["Date"].dt.isocalendar().week

    master["Day"] = master["Date"].dt.day

    return master


# ==========================================================
# Latest Stock
# ==========================================================

def get_latest_stock():

    master = build_master_stock()

    latest = master["Date"].max()

    latest_df = master[
        master["Date"] == latest
    ]

    return latest.strftime("%d-%m-%Y"), latest_df


# ==========================================================
# Available Years
# ==========================================================

def get_years():

    df = build_master_stock()

    return sorted(df["Year"].dropna().unique())


# ==========================================================
# Available Months
# ==========================================================

def get_months(year):

    df = build_master_stock()

    df = df[df["Year"] == year]

    return df["Month"].unique()


# ==========================================================
# Filter Data
# ==========================================================

def filter_stock(year=None, month=None, week=None):

    df = build_master_stock()

    if year is not None:
        df = df[df["Year"] == year]

    if month is not None:
        df = df[df["Month"] == month]

    if week is not None:
        df = df[df["Week"] == week]

    return df
