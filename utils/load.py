import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
import psycopg2
from psycopg2.extras import execute_values

def save_to_csv(df: pd.DataFrame, file_path: str):
    """Simpan DataFrame ke file CSV."""
    df.to_csv(file_path, index=False)
    print(f"Data berhasil disimpan ke: {file_path}")


# def save_to_google_sheets(df: pd.DataFrame, sheet_name: str, service_account_path: str):
#     """
#     Simpan DataFrame ke Google Sheets.
    
#     Pastikan file service_account_path (format JSON) adalah kredensial yang punya akses EDIT.
#     """
#     gc = gspread.service_account(filename=service_account_path)
    
#     try:
#         sh = gc.open(sheet_name)
#     except gspread.SpreadsheetNotFound:
#         # Jika sheet belum ada, buat baru
#         sh = gc.create(sheet_name)
#         # Share akses ke publik sebagai editor
#         sh.share(None, perm_type='anyone', role='writer')

#     worksheet = sh.get_worksheet(0) or sh.sheet1
#     worksheet.clear()  # hapus isi sheet sebelum upload baru

#     set_with_dataframe(worksheet, df)
#     print(f"Data berhasil diunggah ke Google Sheets: {sheet_name}")
#     print(f"Link: https://docs.google.com/spreadsheets/d/{sh.id}")


# def save_to_postgresql(df: pd.DataFrame, db_config: dict, table_name: str):
#     """
#     Simpan DataFrame ke PostgreSQL.

#     Parameter:
#     - db_config = {
#         'dbname': '',
#         'user': '',
#         'password': '',
#         'host': '',
#         'port': 5432
#       }
#     """
#     conn = psycopg2.connect(**db_config)
#     cursor = conn.cursor()

#     # Buat tabel jika belum ada (optional, tergantung kebutuhan)
#     create_table_query = f"""
#     CREATE TABLE IF NOT EXISTS {table_name} (
#         title TEXT,
#         price FLOAT,
#         rating FLOAT,
#         colors INTEGER,
#         size TEXT,
#         gender TEXT
#     );
#     """
#     cursor.execute(create_table_query)
#     conn.commit()

#     # Siapkan data sebagai list of tuples
#     records = df.to_records(index=False)
#     data = list(records)

#     # Insert data ke tabel
#     insert_query = f"INSERT INTO {table_name} (title, price, rating, colors, size, gender) VALUES %s"
#     execute_values(cursor, insert_query, data)
#     conn.commit()

#     cursor.close()
#     conn.close()
#     print(f"Data berhasil disimpan ke PostgreSQL: {table_name}")
