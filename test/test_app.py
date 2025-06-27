import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

SRC_DIR = Path(__file__).parent.parent / "src"
DATA_DIR = Path(__file__).parent.parent / "data"
SOURCE_FILE = DATA_DIR / "combined.xlsx"
OUTPUT_FILE = DATA_DIR / "customers_weighted.csv"
MAX_SAMPLES = 200

sys.path.insert(0, str(SRC_DIR))

@pytest.fixture
def customers_df():
    return pd.DataFrame({
        'customer': ['A', 'B', 'C'],
        'hours': [15, 30, 45]
    })

@pytest.fixture
def resources_df():
    return pd.DataFrame({
        'resource': ['R1', 'R2'],
        'capacity': [100, 200]
    })

def test_weight_column(customers_df):
    df = customers_df.copy()
    df["weight"] = df["hours"] / 15
    assert np.allclose(df["weight"], [1, 2, 3])

def test_proportion_and_occurrences(customers_df):
    df = customers_df.copy()
    df["weight"] = df["hours"] / 15
    weight_sum = df["weight"].sum()
    df["proportion"] = df["weight"] / weight_sum
    df["exact_occurrences"] = df["proportion"] * MAX_SAMPLES
    df["occurrences"] = np.floor(df["exact_occurrences"]).astype(int)
    assert df["occurrences"].sum() <= MAX_SAMPLES

def test_remaining_samples_distribution(customers_df):
    df = customers_df.copy()
    df["weight"] = df["hours"] / 15
    weight_sum = df["weight"].sum()
    df["proportion"] = df["weight"] / weight_sum
    df["exact_occurrences"] = df["proportion"] * MAX_SAMPLES
    df["occurrences"] = np.floor(df["exact_occurrences"]).astype(int)
    remaining_samples = MAX_SAMPLES - df["occurrences"].sum()
    if remaining_samples > 0:
        fractional_parts = df["exact_occurrences"] - df["occurrences"]
        indices = fractional_parts.sort_values(ascending=False).index[:int(remaining_samples)]
        df.loc[indices, "occurrences"] += 1
    assert df["occurrences"].sum() == MAX_SAMPLES

def test_expanded_df(customers_df):
    df = customers_df.copy()
    df["weight"] = df["hours"] / 15
    weight_sum = df["weight"].sum()
    df["proportion"] = df["weight"] / weight_sum
    df["exact_occurrences"] = df["proportion"] * MAX_SAMPLES
    df["occurrences"] = np.floor(df["exact_occurrences"]).astype(int)
    remaining_samples = MAX_SAMPLES - df["occurrences"].sum()
    if remaining_samples > 0:
        fractional_parts = df["exact_occurrences"] - df["occurrences"]
        indices = fractional_parts.sort_values(ascending=False).index[:int(remaining_samples)]
        df.loc[indices, "occurrences"] += 1
    df["ceremony"] = df["customer"].apply(lambda c: f"{c}: Data CoE ceremony")
    expanded_df = pd.DataFrame({
        'customer': np.repeat(df['customer'].values, df['occurrences'].values),
        'ceremony': np.repeat(df['ceremony'].values, df['occurrences'].values),
        'hours': np.repeat(df['hours'].values, df['occurrences'].values)
    })
    assert len(expanded_df) == MAX_SAMPLES
    assert set(expanded_df['customer']).issubset(set(df['customer']))
    assert 'ceremony' in expanded_df.columns

def generate_resource_customer_sheets(expanded_df, resources_df, output_path, random_seed=None):
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
    with pd.ExcelWriter(output_path) as writer:
        if len(resource_names) == 0:
            pass  # No sheets written
        else:
            for i, resource in enumerate(resource_names):
                resource_seed = (random_seed + i) if random_seed is not None else None
                shuffled_customers = expanded_df.sample(frac=1, random_state=resource_seed).reset_index(drop=True)
                df_to_write = shuffled_customers[['customer', 'ceremony']].copy()
                df_to_write['claimed'] = ''
                df_to_write['what'] = ''
                df_to_write.to_excel(writer, sheet_name=resource, index=False)
    return True

def test_generate_resource_customer_sheets(tmp_path):
    import pandas as pd
    from app import generate_resource_customer_sheets

    expanded_df = pd.DataFrame({
        'customer': ['A', 'B', 'C', 'A', 'B', 'C'],
        'ceremony': [f'{c}: Data CoE ceremony' for c in ['A', 'B', 'C', 'A', 'B', 'C']],
        'hours': [10, 20, 30, 10, 20, 30],
        'claimed': [''] * 6,
        'what': [''] * 6    
    })
    resources_df = pd.DataFrame({'resource': ['R1', 'R2']})
    output_path = tmp_path / "test_resources_customers.xlsx"
    assert generate_resource_customer_sheets(expanded_df, resources_df, output_path, random_seed=42)
    assert output_path.exists()
    xls = pd.ExcelFile(output_path)
    assert set(xls.sheet_names) == {'R1', 'R2'}
    dfs = [pd.read_excel(xls, sheet_name=sheet) for sheet in xls.sheet_names]
    # Check that the order of customers is different between sheets
    assert not dfs[0]['customer'].equals(dfs[1]['customer'])
    for df in dfs:
        assert set(df.columns) == {'customer', 'ceremony', 'claimed', 'what'}
        assert len(df) == len(expanded_df)

# Edge case: no resources

def test_generate_resource_customer_sheets_no_resources(tmp_path):
    import pandas as pd
    from app import generate_resource_customer_sheets
    expanded_df = pd.DataFrame({'customer': ['A'], 'ceremony': ['A: Data CoE ceremony'], 'hours': [10]})
    resources_df = pd.DataFrame({'resource': []})
    output_path = tmp_path / "empty_resources_customers.xlsx"
    assert generate_resource_customer_sheets(expanded_df, resources_df, output_path)
    # File should exist but have no resource sheets
    xls = pd.ExcelFile(output_path)
    # Accept either no sheets or a default sheet (e.g., 'Sheet1') if no resources
    assert xls.sheet_names == [] or xls.sheet_names == ['Sheet1']

# Failure case: expanded_df empty

def test_generate_resource_customer_sheets_empty_expanded(tmp_path):
    import pandas as pd
    from app import generate_resource_customer_sheets
    expanded_df = pd.DataFrame({'customer': [], 'ceremony': [], 'hours': []})
    resources_df = pd.DataFrame({'resource': ['R1']})
    output_path = tmp_path / "fail_resources_customers.xlsx"
    assert generate_resource_customer_sheets(expanded_df, resources_df, output_path)
    xls = pd.ExcelFile(output_path)
    assert set(xls.sheet_names) == {'R1'}
    df = pd.read_excel(xls, sheet_name='R1')
    assert df.empty
