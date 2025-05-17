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
    for column, invalid_values in dirty_patterns.items():
        if row[column] in invalid_values:
            return True
    return False

def clean_and_transform(df):
    # Buang data yang mengandung nilai tidak valid
    df = df[~df.apply(is_invalid, axis=1)]

    # Bersihkan dan ubah tipe data
    df['Price'] = (
        df['Price']
        .str.replace('$', '', regex=False)
        .astype(float) * DOLLAR_TO_IDR
    )

    df['Rating'] = (
        df['Rating']
        .str.replace('/ 5', '', regex=False)
        .astype(float)
    )

    df['Colors'] = (
        df['Colors']
        .str.extract(r'(\d+)')  # ambil angka dari "3 Colors"
        .astype(int)
    )

    df['Size'] = df['Size'].str.replace('Size: ', '', regex=False).astype(str)
    df['Gender'] = df['Gender'].str.replace('Gender: ', '', regex=False).astype(str)

    # Hapus duplikat dan nilai null
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)

    return df
