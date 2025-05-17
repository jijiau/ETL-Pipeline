import pandas as pd
from utils.extract import scrape_products
from utils.transform import clean_and_transform
from utils.load import save_to_csv, save_to_google_sheets

def main():
    try:
        raw_data = scrape_products()
        if not raw_data:
            print("[ERROR] Failed to fetch data.")
            return

        df_raw = pd.DataFrame(raw_data)
        print(f"[INFO] Total Rows (Raw scraped data): {len(df_raw)}")

        df_clean = clean_and_transform(df_raw)
        print(f"[INFO] Total Rows (After Transform/Cleaned): {len(df_clean)}")

        print("[INFO] Data Types:\n", df_clean.dtypes)

        # save_to_csv(df_clean, "products.csv")
        # print("[INFO] Data successfully saved to 'products.csv'.")

        # Save to Google Sheets
        service_account_path = "google-sheets-api.json"  # Sesuaikan path Anda
        sheet_name = "ETL Products Data"                      # Nama Google Sheet
        try:
            save_to_google_sheets(df_clean, sheet_name, service_account_path)
        except Exception as e:
            print(f"[ERROR] Upload to Google Sheets failed: {e}")




    except Exception as e:
        print(f"[FATAL] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
