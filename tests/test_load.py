import pandas as pd
from utils.load import save_to_csv
from unittest.mock import patch, MagicMock
import os

import pytest
import pandas as pd

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "Title": ["Product A"],
        "Price": [100000.0],
        "Rating": [4.0],
        "Colors": [2],
        "Size": ["M"],
        "Gender": ["Male"],
        "timestamp": ["2024-01-01T00:00:00"]
    })

def test_save_to_csv(tmp_path):
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    file_path = tmp_path / "test.csv"

    save_to_csv(df, str(file_path))

    assert os.path.exists(file_path)

    # ✅ Tambahan: cek isi file
    loaded_df = pd.read_csv(file_path)
    pd.testing.assert_frame_equal(df, loaded_df)

@patch("utils.load.gspread.service_account")
def test_save_to_google_sheets(mock_service_account, sample_dataframe):
    from utils.load import save_to_google_sheets

    mock_gc = MagicMock()
    mock_sh = MagicMock()
    mock_ws = MagicMock()

    mock_ws.row_count = 0
    mock_ws.col_count = 0

    mock_gc.open.return_value = mock_sh
    mock_sh.get_worksheet.return_value = mock_ws
    mock_service_account.return_value = mock_gc

    save_to_google_sheets(sample_dataframe, "Sheet1", "fake-path.json")

    mock_service_account.assert_called_once_with(filename="fake-path.json")
    mock_gc.open.assert_called_once_with("Sheet1")
    mock_sh.get_worksheet.assert_called_once_with(0)
    mock_ws.clear.assert_called_once()

@patch("utils.load.psycopg2.connect")
def test_save_to_postgresql(mock_connect, sample_dataframe):
    from utils.load import save_to_postgresql

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    db_config = {
        "host": "localhost",
        "dbname": "testdb",
        "user": "test",
        "password": "test"
    }

    save_to_postgresql(sample_dataframe, db_config, "test_table")

    mock_connect.assert_called_once_with(**db_config)
    mock_cursor.execute.assert_any_call(  # Check create table query dipanggil
        f"""
        CREATE TABLE IF NOT EXISTS test_table (
            title TEXT,
            price FLOAT,
            rating FLOAT,
            colors INTEGER,
            size TEXT,
            gender TEXT,
            timestamp TIMESTAMP
        );
        """
    )
    assert mock_cursor.execute.call_count >= 1
    mock_conn.commit.assert_called()

def test_save_to_csv_empty(tmp_path):
    from utils.load import save_to_csv

    df = pd.DataFrame(columns=["Title", "Price", "Rating", "Colors", "Size", "Gender", "timestamp"])
    file_path = tmp_path / "empty.csv"

    save_to_csv(df, str(file_path))

    # File tidak dibuat karena empty
    assert not file_path.exists()

@patch("utils.load.gspread.service_account")
def test_save_to_google_sheets_create_new(mock_service_account, sample_dataframe):
    from utils.load import save_to_google_sheets
    import gspread

    mock_gc = MagicMock()
    mock_sh = MagicMock()
    mock_ws = MagicMock()

    mock_ws.row_count = 1000  # harus integer
    mock_ws.col_count = 26    # harus integer

    mock_gc.open.side_effect = gspread.SpreadsheetNotFound("Spreadsheet not found")
    mock_gc.create.return_value = mock_sh
    mock_sh.get_worksheet.return_value = mock_ws
    mock_service_account.return_value = mock_gc

    save_to_google_sheets(sample_dataframe, "NewSheet", "fake-path.json")

    mock_service_account.assert_called_once_with(filename="fake-path.json")
    mock_gc.create.assert_called_once_with("NewSheet")
    mock_sh.get_worksheet.assert_called_once_with(0)
    mock_ws.clear.assert_called_once()

@patch("utils.load.psycopg2.connect")
def test_save_to_postgresql_empty_df(mock_connect):
    from utils.load import save_to_postgresql

    df = pd.DataFrame(columns=["Title", "Price", "Rating", "Colors", "Size", "Gender", "timestamp"])
    db_config = {
        "host": "localhost",
        "dbname": "testdb",
        "user": "test",
        "password": "test"
    }

    save_to_postgresql(df, db_config, "test_table")

    # Tidak ada koneksi yang dipanggil karena df kosong
    mock_connect.assert_not_called()
