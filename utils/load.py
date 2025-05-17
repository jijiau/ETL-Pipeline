import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
import psycopg2
from psycopg2.extras import execute_values

def save_to_csv(df: pd.DataFrame, file_path: str):
    if df.empty:
        print(f"[WARN] DataFrame is empty. Skipped saving to {file_path}.")
        return

    try:
        df.to_csv(file_path, index=False)
        print(f"Saved to {file_path}")
    except Exception as e:
        print(f"[ERROR] Saving to CSV failed: {e}")


def save_to_google_sheets(df: pd.DataFrame, sheet_name: str, service_account_path: str):
    """
    Simpan DataFrame ke Google Sheets.
    
    Pastikan file service_account_path (format JSON) adalah kredensial yang punya akses EDIT.
    """
    gc = gspread.service_account(filename=service_account_path)
    
    try:
        sh = gc.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        # Jika sheet belum ada, buat baru
        sh = gc.create(sheet_name)
        # Share akses ke publik sebagai editor
        sh.share(None, perm_type='anyone', role='writer')
    
    worksheet = sh.get_worksheet(0) or sh.sheet1
    worksheet.clear()  # hapus isi sheet sebelum upload baru

    set_with_dataframe(worksheet, df)
    print(f"[INFO] Data successfully saved to Google Sheets: {sheet_name}.")
    print(f"Link: https://docs.google.com/spreadsheets/d/{sh.id}")

def save_to_postgresql(df: pd.DataFrame, db_config: dict, table_name: str):
    if df.empty:
        print(f"[WARN] DataFrame is empty. Skipped saving to PostgreSQL.")
        return

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            title TEXT,
            price FLOAT,
            rating FLOAT,
            colors INTEGER,
            size TEXT,
            gender TEXT,
            timestamp TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        conn.commit()

        df = df[['Title', 'Price', 'Rating', 'Colors', 'Size', 'Gender', 'timestamp']]

        records = df.to_records(index=False)
        data = [tuple(map(lambda x: x.item() if hasattr(x, 'item') else x, record)) for record in records]

        insert_query = f"""
        INSERT INTO {table_name} 
        (title, price, rating, colors, size, gender, timestamp) 
        VALUES %s
        """
        execute_values(cursor, insert_query, data)
        conn.commit()

        cursor.close()
        conn.close()
        print(f"[INFO] Data successfully saved to table: {table_name}.")
    except Exception as e:
        print(f"[ERROR] Saving to PostgreSQL failed: {e}")