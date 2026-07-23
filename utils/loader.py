# ==========================================================
# Chemical Dashboard
# Loader.py
# ==========================================================

import os
import glob
import pandas as pd

# ==========================================================
# DATA FOLDER
# ==========================================================

DATA_FOLDER = "data"

# ==========================================================
# GET ALL YEAR FILES
# ==========================================================

def get_excel_files():

    files = glob.glob(
        os.path.join(DATA_FOLDER, "*.xlsx")
    )

    files.sort()

    return files


# ==========================================================
# VALID MONTH SHEETS
# ==========================================================

MONTHS = [

    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"

]



# ==========================================================
# READ WORKBOOK
# ==========================================================

def read_workbook(file):

    try:

        workbook = pd.read_excel(
            file,
            sheet_name=None,
            header=1, # Second row contains headers
            engine="openpyxl"
        )

        return workbook

    except Exception as e:

        print(e)

        return {}

# ==========================================================
# BUILD MASTER DATAFRAME
# ==========================================================

# ==========================================================
# BUILD MASTER DATAFRAME
# ==========================================================

def build_master_stock():

    files = get_excel_files()

    master = []

    if not files:
        return pd.DataFrame()

    for file in files:

        workbook = read_workbook(file)

        for sheet_name, df in workbook.items():

            # Ignore unwanted sheets
            if str(sheet_name).lower() in ["sheet1", "sheet2"]:
                continue

            if df.empty:
                continue

            # Remove completely blank rows
            df = df.dropna(how="all")

            if df.empty:
                continue

           # Keep only first 8 columns if available
            df = df.iloc[:, :min(8, len(df.columns))]
            
            # Skip sheets having fewer than 8 columns
            if len(df.columns) < 8:
                continue
            
            df.columns = [
                "Date",
                "Chemical",
                "Daily Requirement",
                "Monthly Requirement",
                "3 Month Requirement",
                "Available Stock",
                "Available Days",
                "Vendor"
            ]
            # Remove blank chemicals
            df = df.dropna(subset=["Chemical"])

            # Remove Group rows
            df = df[
                ~df["Chemical"].astype(str).str.contains(
                    "Group",
                    case=False,
                    na=False
                )
            ]

            # Remove Total rows
            df = df[
                ~df["Chemical"].astype(str).str.contains(
                    "Total",
                    case=False,
                    na=False
                )
            ]

            # Date comes from SHEET NAME
            sheet_date = pd.to_datetime(
                sheet_name,
                dayfirst=True,
                errors="coerce"
            )

            if pd.isna(sheet_date):
                continue

            df["Date"] = sheet_date

            df["Year"] = sheet_date.year
            df["Month"] = sheet_date.strftime("%B")
            df["Week"] = int(sheet_date.isocalendar().week)
            df["Day"] = sheet_date.day

            numeric = [
                "Daily Requirement",
                "Monthly Requirement",
                "3 Month Requirement",
                "Available Stock",
                "Available Days"
            ]

            for col in numeric:
                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

            master.append(df)

    if not master:
        return pd.DataFrame()

    master = pd.concat(
        master,
        ignore_index=True
    )

    master = master.sort_values("Date")

    master.reset_index(
        drop=True,
        inplace=True
    )

    return master

# ==========================================================
# GET LATEST STOCK
# ==========================================================

def get_latest_stock():

    master = build_master_stock()

    if master.empty:

        return "", pd.DataFrame()

    latest_date = master["Date"].max()

    latest_df = master[
        master["Date"] == latest_date
    ].copy()

    latest_df.reset_index(
        drop=True,
        inplace=True
    )

    return (
        latest_date.strftime("%d-%m-%Y"),
        latest_df
    )


# ==========================================================
# AVAILABLE YEARS
# ==========================================================

def get_years():

    master = build_master_stock()

    if master.empty:

        return []

    years = sorted(
        master["Year"].dropna().unique().tolist()
    )

    return years


# ==========================================================
# AVAILABLE MONTHS
# ==========================================================

def get_months(year="All"):

    master = build_master_stock()

    if master.empty:

        return []

    if year != "All":

        master = master[
            master["Year"] == year
        ]

    months = []

    for month in MONTHS:

        if month in master["Month"].unique():

            months.append(month)

    return months


# ==========================================================
# AVAILABLE WEEKS
# ==========================================================

def get_weeks(
        year="All",
        month="All"
):

    master = build_master_stock()

    if master.empty:

        return []

    if year != "All":

        master = master[
            master["Year"] == year
        ]

    if month != "All":

        master = master[
            master["Month"] == month
        ]

    weeks = sorted(
        master["Week"].dropna().unique().tolist()
    )

    return weeks


# ==========================================================
# AVAILABLE CHEMICALS
# ==========================================================

def get_chemicals():

    master = build_master_stock()

    if master.empty:

        return []

    chemicals = sorted(
        master["Chemical"].dropna().unique().tolist()
    )

    return chemicals


# ==========================================================
# FILTER DATA
# ==========================================================

def filter_data(
    year="All",
    month="All",
    week="All",
    chemical="All"
):

    master = build_master_stock()

    if master.empty:

        return master

    if year != "All":

        master = master[
            master["Year"] == year
        ]

    if month != "All":

        master = master[
            master["Month"] == month
        ]

    if week != "All":

        master = master[
            master["Week"] == week
        ]

    if chemical != "All":

        master = master[
            master["Chemical"] == chemical
        ]

    master.reset_index(
        drop=True,
        inplace=True
    )

    return master

# ==========================================================
# DAILY CONSUMPTION CALCULATION
# ==========================================================

def calculate_consumption():

    master = build_master_stock()

    if master.empty:

        return pd.DataFrame()

    master = master.sort_values(
        ["Chemical", "Date"]
    )

    consumption = []

    for chemical in master["Chemical"].unique():

        temp = master[
            master["Chemical"] == chemical
        ].copy()

        temp = temp.sort_values("Date")

        temp["Consumption"] = (
            temp["Available Stock"].shift(1)
            - temp["Available Stock"]
        )

        temp["Consumption"] = (
            temp["Consumption"]
            .fillna(0)
            .clip(lower=0)
        )

        consumption.append(temp)

    consumption = pd.concat(
        consumption,
        ignore_index=True
    )

    return consumption


# ==========================================================
# WEEKLY CONSUMPTION
# ==========================================================

def weekly_consumption():

    df = calculate_consumption()

    if df.empty:

        return pd.DataFrame()

    return (
        df.groupby(
            ["Year", "Week"],
            as_index=False
        )["Consumption"]
        .sum()
    )


# ==========================================================
# MONTHLY CONSUMPTION
# ==========================================================

def monthly_consumption():

    df = calculate_consumption()

    if df.empty:

        return pd.DataFrame()

    return (
        df.groupby(
            ["Year", "Month"],
            as_index=False
        )["Consumption"]
        .sum()
    )


# ==========================================================
# YEARLY CONSUMPTION
# ==========================================================

def yearly_consumption():

    df = calculate_consumption()

    if df.empty:

        return pd.DataFrame()

    return (
        df.groupby(
            "Year",
            as_index=False
        )["Consumption"]
        .sum()
    )


# ==========================================================
# CHEMICAL CONSUMPTION
# ==========================================================

def chemical_consumption():

    df = calculate_consumption()

    if df.empty:

        return pd.DataFrame()

    return (
        df.groupby(
            "Chemical",
            as_index=False
        )["Consumption"]
        .sum()
    )


# ==========================================================
# EXECUTIVE KPI SUMMARY
# ==========================================================

def dashboard_summary():

    latest_date, latest = get_latest_stock()

    if latest.empty:

        return {}

    summary = {

        "Latest Date": latest_date,

        "Total Chemicals":
            latest["Chemical"].nunique(),

        "Total Stock":
            round(
                latest["Available Stock"].sum(),
                2
            ),

        "Daily Requirement":
            round(
                latest["Daily Requirement"].sum(),
                2
            ),

        "Monthly Requirement":
            round(
                latest["Monthly Requirement"].sum(),
                2
            ),

        "Healthy":
            len(
                latest[
                    latest["Available Days"] >= 90
                ]
            ),

        "Warning":
            len(
                latest[
                    (latest["Available Days"] >= 30)
                    &
                    (latest["Available Days"] < 90)
                ]
            ),

        "Critical":
            len(
                latest[
                    latest["Available Days"] < 30
                ]
            )

    }

    return summary


# ==========================================================
# STOCK HEALTH
# ==========================================================

def stock_health(df):

    if df.empty:

        return df

    df = df.copy()

    def health(days):

        if days >= 90:

            return "Healthy"

        elif days >= 30:

            return "Warning"

        else:

            return "Critical"

    df["Status"] = df[
        "Available Days"
    ].apply(health)

    return df
