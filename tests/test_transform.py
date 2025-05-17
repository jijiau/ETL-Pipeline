import pandas as pd
from utils.transform import is_invalid, clean_and_transform

def test_is_invalid_valid_row():
    row = {
        "Title": "Product",
        "Rating": "4.0 / 5",
        "Price": "$10"
    }
    assert is_invalid(row) is False

def test_is_invalid_invalid_row():
    row = {
        "Title": "Unknown Product",
        "Rating": "4.0 / 5",
        "Price": "$10"
    }
    assert is_invalid(row) is True

def test_clean_and_transform_typical():
    data = {
        "Title": ["Product A"],
        "Price": ["$10"],
        "Rating": ["4.5 / 5"],
        "Colors": ["3 Colors"],
        "Size": ["Size: M"],
        "Gender": ["Gender: Female"],
        "timestamp": ["2023-01-01T00:00:00"]
    }
    df = pd.DataFrame(data)
    df_clean = clean_and_transform(df)
    assert not df_clean.empty
    assert df_clean.iloc[0]["Price"] == 160000.0
    assert df_clean.iloc[0]["Rating"] == 4.5
    assert df_clean.iloc[0]["Colors"] == 3

def test_clean_and_transform_empty_df():
    df = pd.DataFrame(columns=["Title", "Price", "Rating", "Colors", "Size", "Gender", "timestamp"])
    df_clean = clean_and_transform(df)
    assert df_clean.empty

def test_clean_and_transform_remove_invalid():
    data = {
        "Title": ["Unknown Product", "Product B"],
        "Price": ["Price Unavailable", "$15"],
        "Rating": ["Invalid Rating / 5", "4.0 / 5"],
        "Colors": ["3 Colors", "2 Colors"],
        "Size": ["Size: L", "Size: M"],
        "Gender": ["Gender: Male", "Gender: Female"],
        "timestamp": ["2023-01-01T00:00:00", "2023-01-01T00:00:00"]
    }
    df = pd.DataFrame(data)
    df_clean = clean_and_transform(df)

    assert len(df_clean) == 1  # Hanya Product B yang lolos
    assert df_clean.iloc[0]["Title"] == "Product B"
    assert df_clean.iloc[0]["Price"] == 240000.0  # $15 * 16000

def test_clean_and_transform_duplicates_and_nulls():
    data = {
        "Title": ["Product C", "Product C", None],
        "Price": ["$20", "$20", "$30"],
        "Rating": ["5.0 / 5", "5.0 / 5", "4.0 / 5"],
        "Colors": ["2 Colors", "2 Colors", "3 Colors"],
        "Size": ["Size: XL", "Size: XL", "Size: M"],
        "Gender": ["Gender: Unisex", "Gender: Unisex", "Gender: Male"],
        "timestamp": ["2023-01-01T00:00:00", "2023-01-01T00:00:00", "2023-01-01T00:00:00"]
    }
    df = pd.DataFrame(data)
    df_clean = clean_and_transform(df)

    assert len(df_clean) == 1  # Duplikat & null dibuang
    assert df_clean.iloc[0]["Title"] == "Product C"
    assert df_clean.iloc[0]["Price"] == 320000.0  # $20 * 16000