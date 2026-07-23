import pandas as pd
import os
import glob

# =====================================================
# Folder containing all Excel files
# =====================================================

DATA_FOLDER = "data"

# =====================================================
# Read Latest Stock
# =====================================================

def get_latest_stock():

    files = glob.glob(os.path.join(DATA_FOLDER, "*.xlsx"))

    if len(files) == 0:
        return None, pd.DataFrame()

    latest_file = max(files, key=os.path.getmtime)

    date = os.path.basename(latest_file).replace(".xlsx", "")

    df = pd.read_excel(latest_file)

    return date, df


# =====================================================
# Build Master Stock (All Years)
# =====================================================

def build_master_stock():

    files = glob.glob(os.path.join(DATA_FOLDER, "*.xlsx"))

    master = []

    for file in files:

        try:

            df = pd.read_excel(file)

            filename = os.path.basename(file).replace(".xlsx", "")

            df["Date"] = pd.to_datetime(filename)

            df["Year"] = df["Date"].dt.year

            df["Month"] = df["Date"].dt.month_name()

            df["Week"] = df["Date"].dt.isocalendar().week

            master.append(df)

        except:

            continue

    if len(master) == 0:

        return pd.DataFrame()

    return pd.concat(master, ignore_index=True)
