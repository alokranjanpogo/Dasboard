# ==========================================
# Loader.py
# Chemical Dashboard
# ==========================================

import pandas as pd

# ==========================================
# File Paths
# ==========================================

consumption_file = "chemical_consumption.xlsx"
stock_file = "chemical_stock.xlsx"

# ==========================================
# Load Consumption Workbook
# ==========================================

def load_consumption():
    return pd.read_excel(
        consumption_file,
        sheet_name=None,
        engine="openpyxl"
    )

# ==========================================
# Load Stock Workbook
# ==========================================

def load_stock():
    return pd.read_excel(
        stock_file,
        sheet_name=None,
        engine="openpyxl"
    )

# ==========================================
# Get Latest Stock Sheet
# ==========================================

def get_latest_stock():

    sheets = load_stock()

    latest_sheet = None
    latest_df = None

    # Start checking from last sheet
    for sheet_name, df in reversed(list(sheets.items())):

        # Ignore completely empty sheets
        if df.dropna(how="all").empty:
            continue

        latest_sheet = sheet_name

        # Read again using second row as header
        latest_df = pd.read_excel(
            stock_file,
            sheet_name=sheet_name,
            header=1,
            engine="openpyxl"
        )

        break

    # Remove empty rows
    latest_df = latest_df.dropna(how="all")

    # Remove rows where first column is empty
    latest_df = latest_df.dropna(subset=[latest_df.columns[0]])

    # Remove Group headings
    latest_df = latest_df[
        ~latest_df.iloc[:, 0].astype(str).str.contains(
            "Group",
            case=False,
            na=False
        )
    ]

    # Remove Total rows if present
    latest_df = latest_df[
        ~latest_df.iloc[:, 0].astype(str).str.contains(
            "Total",
            case=False,
            na=False
        )
    ]

    latest_df.reset_index(drop=True, inplace=True)

    return latest_sheet, latest_df


# ==========================================
# Get Sheet Names
# ==========================================

def get_sheet_names():

    consumption = load_consumption()
    stock = load_stock()

    return list(consumption.keys()), list(stock.keys())

      
