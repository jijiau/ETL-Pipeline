import pandas as pd

# Nilai tukar dollar ke rupiah
DOLLAR_TO_IDR = 16000

# Pola nilai tidak valid
dirty_patterns = {
    "Title": ["Unknown Product"],
    "Rating": ["Invalid Rating / 5", "Not Rated"],
    "Price": ["Price Unavailable", None]
}

def is_invalid(row):
    try:
        for column, invalid_values in dirty_patterns.items():
            # Periksa apakah kolom ada di row
            if column not in row:
                print(f"[WARN] Column '{column}' not found in row: {row}")
                continue

            # Cek nilai yang tidak valid
            if row[column] in invalid_values:
                return True
    except Exception as e:
        print(f"[ERROR] Failed to validate row {row}: {e}")
        return True  # Anggap tidak valid jika ada error
    return False

def clean_and_transform(df):
    try:
        # Buang data yang mengandung nilai tidak valid
        df = df[~df.apply(is_invalid, axis=1)].copy()
    except Exception as e:
        print(f"[ERROR] Failed to filter invalid rows: {e}")
        return df  # Kembalikan data mentah jika filtering gagal

    # Transformasi kolom satu per satu dengan try-except lokal
    try:
        df['Price'] = (
            df['Price']
            .str.replace('$', '', regex=False)
            .astype(float) * DOLLAR_TO_IDR
        )
    except Exception as e:
        print(f"[ERROR] Failed to clean 'Price' column: {e}")

    try:
        df['Rating'] = (
            df['Rating']
            .str.replace('/ 5', '', regex=False)
            .astype(float)
        )
    except Exception as e:
        print(f"[ERROR] Failed to clean 'Rating' column: {e}")

    try:
        df['Colors'] = (
            df['Colors']
            .str.extract(r'(\d+)')  # ambil angka dari "3 Colors"
            .astype(int)
        )
    except Exception as e:
        print(f"[ERROR] Failed to extract 'Colors' column: {e}")

    try:
        df['Size'] = df['Size'].str.replace('Size: ', '', regex=False).astype(str)
    except Exception as e:
        print(f"[ERROR] Failed to clean 'Size' column: {e}")

    try:
        df['Gender'] = df['Gender'].str.replace('Gender: ', '', regex=False).astype(str)
    except Exception as e:
        print(f"[ERROR] Failed to clean 'Gender' column: {e}")

    # Hapus duplikat dan nilai null
    try:
        df.drop_duplicates(inplace=True)
        df.dropna(inplace=True)
    except Exception as e:
        print(f"[ERROR] Failed to drop duplicates or nulls: {e}")

    return df

