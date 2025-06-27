#!/usr/bin/env python3
"""
Expand customers pro-rata by their hours and generate a unique random order of customers for each resource.

This script performs the following steps:
    1. Reads Data CoE Team & Customers.xlsx (expects columns: customer, hours, userstory)
    2. Adds a 'weight' column = hours / HOURS_DIVISOR
    3. Creates a deterministic list where proportions match exact weights
    4. Expands the customer list according to weights
    5. For each resource, creates a sheet in the output Excel file with a different random order of customers
    6. Saves the expanded and randomized lists to an Excel file with a sheet per resource

Typical usage example:
    $ python app.py
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv  # NEW: import dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

# ---------- Parameters ----------
SRC_DIR = Path(__file__).parent
DATA_DIR = SRC_DIR.parent / "data"

SOURCE_FILE = DATA_DIR / "Data CoE Team & Customers.xlsx"
today_str = datetime.now().strftime("%Y%m%d")
OUTPUT_FILE = DATA_DIR / f"dcoe_standup_sprint_to_psa_v3_{today_str}.xlsx"

# Configurable parameters
MAX_SAMPLES = int(os.getenv("MAX_SAMPLES", 200))  # Allow override via env var
HOURS_DIVISOR = int(os.getenv("HOURS_DIVISOR", 15))  # Magic number as constant
RANDOM_SEED_ENV = os.getenv("RANDOM_SEED")
if RANDOM_SEED_ENV is not None and RANDOM_SEED_ENV.strip() != "":
    RANDOM_SEED = int(RANDOM_SEED_ENV)
else:
    RANDOM_SEED = int(np.random.randint(0, 100000))
# --------------------------------

def generate_resource_customer_sheets(
    expanded_df: pd.DataFrame,
    resources_df: pd.DataFrame,
    output_path: Path,
    random_seed: Optional[int] = None
) -> bool:
    """
    For each resource, create a sheet in an Excel file with a unique randomized customer list.

    Args:
        expanded_df (pd.DataFrame): DataFrame containing expanded customer rows with columns 'customer' and 'ceremony'.
        resources_df (pd.DataFrame): DataFrame containing resources with a 'resource' column.
        output_path (Path): Path to the output Excel file.
        random_seed (Optional[int], optional): Random seed for reproducibility. Defaults to None.

    Returns:
        bool: True if sheets are generated (even if none are written), False otherwise.
    """
    resource_names = resources_df['resource'].unique()
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        if len(resource_names) == 0:
            print("[WARN] No resources found. No sheets will be written.")
        else:
            for i, resource in enumerate(resource_names):
                # Use a different seed for each resource to ensure different shuffles
                resource_seed = (random_seed + i) if random_seed is not None else None
                shuffled_customers = expanded_df.sample(frac=1, random_state=resource_seed).reset_index(drop=True)
                # Add empty 'claimed' and 'what' columns
                shuffled_customers = shuffled_customers[['customer', 'ceremony']].copy()
                shuffled_customers['claimed'] = ''
                shuffled_customers['what'] = ''
                shuffled_customers.to_excel(writer, sheet_name=str(resource), index=False)
    return True

def main() -> None:
    """
    Main execution function for expanding customers and generating resource sheets.

    Loads customer and resource data, calculates weights and occurrences, expands the customer list,
    and generates an Excel file with a sheet for each resource.
    """
    # 1️⃣ Load the original file (from Excel, 'customers' and 'resources' sheets)
    try:
        customers_df = pd.read_excel(SOURCE_FILE, sheet_name="customers")
        resources_df = pd.read_excel(SOURCE_FILE, sheet_name="resources")
    except FileNotFoundError:
        print(f"[ERROR] Source file not found: {SOURCE_FILE}")
        return
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    # Check required columns
    for col in ["customer", "hours"]:
        if col not in customers_df.columns:
            print(f"[ERROR] Missing required column: {col}")
            return

    # 2️⃣ Weight column (hours ÷ HOURS_DIVISOR)
    customers_df["weight"] = customers_df["hours"] / HOURS_DIVISOR
    weight_sum = customers_df["weight"].sum()
    customers_df["proportion"] = customers_df["weight"] / weight_sum
    customers_df["exact_occurrences"] = customers_df["proportion"] * MAX_SAMPLES
    customers_df["occurrences"] = np.floor(customers_df["exact_occurrences"]).astype(int)

    # 3️⃣ Add ceremony column (was: userstory)
    customers_df["ceremony"] = customers_df["userstory"].apply(lambda u: f"{u}: Data CoE ceremony")

    # 4️⃣ Distribute remaining samples based on fractional parts
    remaining_samples = MAX_SAMPLES - customers_df["occurrences"].sum()
    if remaining_samples > 0:
        fractional_parts = customers_df["exact_occurrences"] - customers_df["occurrences"]
        indices = fractional_parts.sort_values(ascending=False).index[:int(remaining_samples)]
        customers_df.loc[indices, "occurrences"] += 1

    # 5️⃣ Create expanded dataframe using repetition
    expanded_df = pd.DataFrame({
        'customer': np.repeat(customers_df['customer'].to_numpy(), customers_df['occurrences'].to_numpy()),
        'ceremony': np.repeat(customers_df['ceremony'].to_numpy(), customers_df['occurrences'].to_numpy()),
        'hours': np.repeat(customers_df['hours'].to_numpy(), customers_df['occurrences'].to_numpy())
    })

    # 6️⃣ Generate resource sheets
    generate_resource_customer_sheets(
        expanded_df,
        resources_df,
        OUTPUT_FILE,
        random_seed=RANDOM_SEED
    )
    print(f"📝  Created {OUTPUT_FILE} with a sheet for each resource.")

if __name__ == "__main__":
    main()